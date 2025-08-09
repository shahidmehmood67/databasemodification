import sqlite3
from collections import defaultdict

DB_PATH = r"D:\Assets\modified\v1\quranpages.sqlite"

# Predefined miny and maxy for lines 1 to 16 (page 4)
MINY_VALUES = [
    75, 160, 245, 330, 415, 500, 585, 670,
    755, 840, 925, 1010, 1095, 1180, 1265, 1350
]

MAXY_VALUES = [
    150, 235, 320, 405, 490, 575, 660, 745,
    830, 915, 1000, 1085, 1170, 1255, 1340, 1425
]

MINX_START = 55
MAXX_END = 850
TOTAL_WIDTH = MAXX_END - MINX_START

def update_page4_dynamic_minmax():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Step 1: Fetch all page 4 rows ordered by line, soraid, ayaid, word
    cur.execute("""
        SELECT rowid, line, soraid, ayaid, word
        FROM ayarects
        WHERE page = 4
        ORDER BY line, soraid, ayaid, word
    """)
    rows = cur.fetchall()

    # Step 2: Group data by line -> soraid -> ayaid
    # For each group, collect words and track last word for half-count
    page_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for row in rows:
        rowid, line_no, soraid, ayaid, word = row
        page_data[line_no][soraid][ayaid].append((word, rowid))

    # Step 3: Process each line separately
    for line_no in sorted(page_data.keys()):
        ayahs = page_data[line_no]

        # Calculate words count per ayah on this line
        # Determine if ayah ends on this line by checking next line
        ayah_word_counts = {}
        ayah_last_words = {}  # last word in this line for each ayah

        # Get all ayaids sorted for this line per soraid and ayaid
        for soraid in ayahs:
            for ayaid in ayahs[soraid]:
                words = sorted(ayahs[soraid][ayaid], key=lambda x: x[0])
                word_numbers = [w[0] for w in words]
                last_word = word_numbers[-1]
                ayah_word_counts[(soraid, ayaid)] = len(words)
                ayah_last_words[(soraid, ayaid)] = last_word

        # Step 4: Determine if ayah ends on this line
        # If the ayah does NOT appear in the next line, then it ends here

        next_line_no = line_no + 1
        ayahs_next_line = page_data.get(next_line_no, {})

        ayah_ends_on_line = {}
        for (soraid, ayaid) in ayah_word_counts:
            # Check if this ayaid is present in next line under same soraid
            # If no, then ayah ends on this line
            next_line_ayaids = ayahs_next_line.get(soraid, {})
            if ayaid not in next_line_ayaids:
                ayah_ends_on_line[(soraid, ayaid)] = True
            else:
                ayah_ends_on_line[(soraid, ayaid)] = False

        # Step 5: Calculate effective word counts with last word as half if ayah ends
        total_effective_words = 0
        ayah_effective_word_counts = {}
        for key in ayah_word_counts:
            count = ayah_word_counts[key]
            if ayah_ends_on_line.get(key, False):
                count -= 0.5
            ayah_effective_word_counts[key] = count
            total_effective_words += count

        if total_effective_words == 0:
            # Avoid division by zero, skip this line
            print(f"Warning: line {line_no} has zero total effective words, skipping.")
            continue

        width_per_word = TOTAL_WIDTH / total_effective_words

        # Step 6: Assign minx and maxx for ayahs in RTL order:
        # Sort ayahs right to left means descending order of ayaid (or soraid then ayaid)
        # Assuming sorting by soraid asc, ayaid desc for RTL inside each soraid

        # Flatten ayahs into list of (soraid, ayaid) sorted by soraid asc, ayaid desc
        ayah_keys = []
        for soraid in sorted(ayahs.keys()):
            sorted_ayas = sorted(ayahs[soraid].keys(), reverse=True)
            for ayaid in sorted_ayas:
                ayah_keys.append((soraid, ayaid))

        current_x = MINX_START
        ayah_minmax_x = {}

        for key in ayah_keys:
            effective_words = ayah_effective_word_counts[key]
            ayah_width = effective_words * width_per_word
            minx = current_x
            maxx = current_x + ayah_width
            ayah_minmax_x[key] = (minx, maxx)
            current_x = maxx

        # Step 7: Update DB rows for this line with calculated minx, maxx, and fixed miny, maxy
        miny = MINY_VALUES[line_no - 1]
        maxy = MAXY_VALUES[line_no - 1]

        for (soraid, ayaid), (minx, maxx) in ayah_minmax_x.items():
            # Update all words of this ayah on this line
            words = ayahs[soraid][ayaid]
            for word_num, rowid in words:
                cur.execute("""
                    UPDATE ayarects
                    SET minx = ?,
                        maxx = ?,
                        miny = ?,
                        maxy = ?
                    WHERE rowid = ?
                """, (minx, maxx, miny, maxy, rowid))

        print(f"Updated line {line_no} with dynamic minx/maxx and fixed miny/maxy.")

    conn.commit()
    conn.close()
    print("✅ Page 4 update complete.")

if __name__ == "__main__":
    update_page4_dynamic_minmax()
