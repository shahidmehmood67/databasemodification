import os
import time
import queue
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

# ============================================================
# CONFIG
# ============================================================

SOURCE_DB = r"D:\Android & Code Work\Working Code\CIT\HolyQuran-Gwal\on_lang_pack_kurdi\src\main\assets\kurdish_kurmanji_unknown.db"

OUTPUT_ROOT = r"D:\Android & Code Work\Assets Working\db\translationnewdb"
OUTPUT_DB = os.path.join(OUTPUT_ROOT, "kurmanji.db")

BASE_URL = "https://surahquran.info/language-Kurmanji-Surah-{sura}-ayat-{ayah}.html"

# ------------------------------------------------------------
# TEST MODE
# ------------------------------------------------------------
# True  = only Surah 1
# False = all Quran
# ------------------------------------------------------------

TEST_SURAH_1_ONLY = False

# ------------------------------------------------------------
# PERFORMANCE
# ------------------------------------------------------------

MAX_WORKERS = 5
REQUEST_TIMEOUT = 20
MAX_RETRIES = 5

# ============================================================
# DB
# ============================================================

def create_output_db():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    conn = sqlite3.connect(OUTPUT_DB)

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS verses (
            sura INTEGER NOT NULL,
            ayah INTEGER NOT NULL,
            text TEXT,
            PRIMARY KEY (sura, ayah)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS failed (
            sura INTEGER,
            ayah INTEGER,
            error TEXT
        )
    """)

    conn.commit()
    conn.close()


def load_verse_list():
    conn = sqlite3.connect(SOURCE_DB)
    cur = conn.cursor()

    if TEST_SURAH_1_ONLY:
        cur.execute("""
            SELECT sura, ayah
            FROM verses
            WHERE sura = 1
            ORDER BY sura, ayah
        """)
    else:
        cur.execute("""
            SELECT sura, ayah
            FROM verses
            ORDER BY sura, ayah
        """)

    rows = cur.fetchall()

    conn.close()

    return rows


# ============================================================
# RESUME SUPPORT
# ============================================================

def verse_already_exists(conn, sura, ayah):
    cur = conn.cursor()

    cur.execute("""
        SELECT 1
        FROM verses
        WHERE sura=? AND ayah=?
        LIMIT 1
    """, (sura, ayah))

    return cur.fetchone() is not None


# ============================================================
# SCRAPING
# ============================================================

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):

        session = requests.Session()

        session.headers.update({
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0 Safari/537.36"
        })

        thread_local.session = session

    return thread_local.session


def extract_translation(html):

    soup = BeautifulSoup(html, "html.parser")

    h2 = soup.find(
        "h2",
        style=lambda s: s and "font-size: 15pt" in s
    )

    if not h2:
        return None

    text = h2.get_text(" ", strip=True)

    if not text:
        return None

    return text


def fetch_translation(sura, ayah):

    url = BASE_URL.format(
        sura=sura,
        ayah=ayah
    )

    session = get_session()

    last_error = None

    for attempt in range(MAX_RETRIES):

        try:

            response = session.get(
                url,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            text = extract_translation(response.text)

            if not text:
                raise Exception("Translation not found")

            return {
                "success": True,
                "sura": sura,
                "ayah": ayah,
                "text": text
            }

        except Exception as e:

            last_error = str(e)

            wait = 2 ** attempt

            print(
                f"[RETRY {attempt + 1}/{MAX_RETRIES}] "
                f"{sura}:{ayah} -> {e}"
            )

            time.sleep(wait)

    return {
        "success": False,
        "sura": sura,
        "ayah": ayah,
        "error": last_error
    }


# ============================================================
# DB WRITER THREAD
# ============================================================

def writer_worker(result_queue):

    conn = sqlite3.connect(OUTPUT_DB)

    cur = conn.cursor()

    saved = 0
    failed = 0

    while True:

        item = result_queue.get()

        if item is None:
            break

        try:

            if item["success"]:

                cur.execute("""
                    INSERT OR REPLACE INTO verses
                    (sura, ayah, text)
                    VALUES (?, ?, ?)
                """, (
                    item["sura"],
                    item["ayah"],
                    item["text"]
                ))

                saved += 1

                print(
                    f"[SAVED] "
                    f"{item['sura']}:{item['ayah']}"
                )

            else:

                cur.execute("""
                    INSERT INTO failed
                    (sura, ayah, error)
                    VALUES (?, ?, ?)
                """, (
                    item["sura"],
                    item["ayah"],
                    item["error"]
                ))

                failed += 1

                print(
                    f"[FAILED] "
                    f"{item['sura']}:{item['ayah']} "
                    f"{item['error']}"
                )

            conn.commit()

        except Exception as e:

            print(
                f"[DB ERROR] "
                f"{item.get('sura')}:{item.get('ayah')} "
                f"{e}"
            )

        result_queue.task_done()

    conn.close()

    print()
    print("Writer finished")
    print("Saved :", saved)
    print("Failed:", failed)


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading verses...")

    create_output_db()

    source_verses = load_verse_list()

    db_conn = sqlite3.connect(OUTPUT_DB)

    verses_to_scrape = []

    for sura, ayah in source_verses:

        if not verse_already_exists(
            db_conn,
            sura,
            ayah
        ):
            verses_to_scrape.append(
                (sura, ayah)
            )

    db_conn.close()

    print()
    print(f"Total source verses : {len(source_verses)}")
    print(f"Need scraping       : {len(verses_to_scrape)}")
    print()

    if not verses_to_scrape:
        print("Everything already exists.")
        return

    result_queue = queue.Queue()

    writer_thread = threading.Thread(
        target=writer_worker,
        args=(result_queue,),
        daemon=True
    )

    writer_thread.start()

    completed = 0

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        future_map = {
            executor.submit(
                fetch_translation,
                sura,
                ayah
            ): (sura, ayah)
            for sura, ayah in verses_to_scrape
        }

        for future in as_completed(future_map):

            result = future.result()

            completed += 1

            print(
                f"[{completed}/{len(verses_to_scrape)}] "
                f"{result['sura']}:{result['ayah']}"
            )

            result_queue.put(result)

    result_queue.join()

    result_queue.put(None)

    writer_thread.join()

    print()
    print("DONE")


if __name__ == "__main__":
    main()