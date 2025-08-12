import sqlite3
from collections import defaultdict

# ==== CONFIG ====
db1_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quranpages.sqlite"
db2_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\ORG\ayahinfo_1152.db"
page_limit = 22       # limit for old DB1 pages
page_offset = 1       # DB2 page_number - page_offset = DB1 page_number

# ==== CONNECT DBs ====
conn1 = sqlite3.connect(db1_path)
conn2 = sqlite3.connect(db2_path)
cur1 = conn1.cursor()
cur2 = conn2.cursor()

# ==== LOAD DB1 words info ====
cur1.execute("""
    SELECT soraid, ayaid, page, word, minx, maxx, miny, maxy
    FROM ayarects
    WHERE page <= ?
    ORDER BY page, soraid, ayaid, word
""", (page_limit,))
db1_words = cur1.fetchall()

# Organize DB1 by (sura, aya) -> list of words info
db1_dict = defaultdict(list)
for row in db1_words:
    sora, aya, page, word_num, minx, maxx, miny, maxy = row
    db1_dict[(sora, aya)].append({
        'page': page,
        'word_num': word_num,
        'minx': minx,
        'maxx': maxx,
        'miny': miny,
        'maxy': maxy,
    })

# ==== LOAD DB2 lines info with page adjustment and limit ====
cur2.execute("""
    SELECT page_number, sura_number, ayah_number, line_number, min_x, max_x, min_y, max_y
    FROM glyphs
    ORDER BY page_number, sura_number, ayah_number, line_number
""")
db2_lines_raw = cur2.fetchall()

db2_lines = defaultdict(list)
for page_num, sura, aya, line_num, min_x, max_x, min_y, max_y in db2_lines_raw:
    db1_page_num = page_num - page_offset
    if db1_page_num < 1 or db1_page_num > page_limit:
        continue  # only lines for first 22 pages of DB1
    db2_lines[(sura, aya)].append({
        'page': db1_page_num,
        'line_num': line_num,
        'min_x': min_x,
        'max_x': max_x,
        'min_y': min_y,
        'max_y': max_y
    })

# ==== Process multi-line ayahs only ====
for (sura, aya), words_list in db1_dict.items():
    if (sura, aya) not in db2_lines:
        continue
    lines = db2_lines[(sura, aya)]
    if len(lines) <= 1:
        continue  # skip single line ayahs

    total_words = len(words_list)
    if total_words == 0:
        print(f"Warning: No words found for ({sura}, {aya}) in DB1")
        continue

    num_lines = len(lines)

    # Distribute words evenly
    base_count = total_words // num_lines
    remainder = total_words % num_lines

    words_per_line = []
    for i in range(num_lines):
        count = base_count + (1 if i < remainder else 0)
        words_per_line.append(count)

    print(f"Multi-line ayah: Sura {sura} Aya {aya}, total words: {total_words}")
    print(f"  Lines: {num_lines}")
    print(f"  Equal words per line: {words_per_line}")

    current_word_index = 0
    for line_idx, count in enumerate(words_per_line):
        line = lines[line_idx]
        assigned_words = words_list[current_word_index:current_word_index + count]
        current_word_index += count
        if not assigned_words:
            print(f"  Line {line['line_num']} (Page {line['page']}): No words assigned (count={count})")
            continue
        print(f"  Line {line['line_num']} (Page {line['page']}), assigning words {assigned_words[0]['word_num']} to {assigned_words[-1]['word_num']} coords:")

        # Update DB1 with new coordinates for assigned words
        for w in assigned_words:
            cur1.execute("""
                UPDATE ayarects
                SET minx = ?, maxx = ?, miny = ?, maxy = ?
                WHERE soraid = ? AND ayaid = ? AND page = ? AND word = ?
            """, (line['min_x'], line['max_x'], line['min_y'], line['max_y'], sura, aya, w['page'], w['word_num']))
            print(f"    Word {w['word_num']} updated -> min_x:{line['min_x']} max_x:{line['max_x']} min_y:{line['min_y']} max_y:{line['max_y']}")

# ==== COMMIT CHANGES AND CLOSE CONNECTIONS ====
# After processing and updating all words
conn1.commit()
print("\nAll multi-line ayahs processed and DB1 updated successfully.")
print(f"Pages processed: 1 to {page_limit}")
print("Database connection will now close.")

conn1.close()
conn2.close()

