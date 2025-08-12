import sqlite3
from collections import defaultdict

# ==== CONFIG ====
db1_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\MOD\quranpages.sqlite"
db2_path = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\DB\Greentech\ORG\ayahinfo_1152.db"
page_limit = 10          # Only process first 10 DB1 pages for debug
page_offset = 1          # DB2 page number - page_offset = DB1 page number

# ==== CONNECT DBs ====
conn1 = sqlite3.connect(db1_path)
conn2 = sqlite3.connect(db2_path)
cur1 = conn1.cursor()
cur2 = conn2.cursor()

# ==== LOAD DB1 words info ====
cur1.execute("""
    SELECT soraid, ayaid, page, word, minx, maxx, miny, maxy
    FROM ayarects
    ORDER BY page, soraid, ayaid, word
""")
db1_words = cur1.fetchall()

# Organize DB1 by (sura, aya) -> list of words info
db1_dict = defaultdict(list)
for row in db1_words:
    sora, aya, page, word_num, minx, maxx, miny, maxy = row
    if page > page_limit:
        continue  # limit for debug
    db1_dict[(sora, aya)].append({
        'page': page,
        'word_num': word_num,
        'minx': minx,
        'maxx': maxx,
        'miny': miny,
        'maxy': maxy,
    })

# ==== LOAD DB2 lines info with page adjustment ====
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
        continue  # limit for debug
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

    min_x_total = min(line['min_x'] for line in lines)
    max_x_total = max(line['max_x'] for line in lines)
    total_width = max_x_total - min_x_total

    line_widths = [line['max_x'] - line['min_x'] for line in lines]
    total_line_width = sum(line_widths)
    # fallback fix if discrepancy large or zero width
    if total_line_width == 0 or abs(total_line_width - total_width) / total_width > 0.1:
        total_line_width = total_width if total_width != 0 else 1

    words_per_line = []
    cumulative = 0
    for i, line in enumerate(lines):
        ratio = line_widths[i] / total_line_width if total_line_width > 0 else 1.0 / len(lines)
        count = int(round(ratio * total_words))
        words_per_line.append(count)
        cumulative += count

    diff = cumulative - total_words
    if diff != 0:
        words_per_line[-1] -= diff

    print(f"Multi-line ayah: Sura {sura} Aya {aya}, total words: {total_words}")
    print(f"  Lines: {len(lines)}")
    print(f"  Words per line: {words_per_line}")

    current_word_index = 0
    for line_idx, count in enumerate(words_per_line):
        line = lines[line_idx]
        assigned_words = words_list[current_word_index:current_word_index + count]
        current_word_index += count
        if not assigned_words:
            print(f"  Line {line['line_num']} (Page {line['page']}): No words assigned (count={count})")
            continue
        print(f"  Line {line['line_num']} (Page {line['page']}), assigning words {assigned_words[0]['word_num']} to {assigned_words[-1]['word_num']} coords:")
        for w in assigned_words:
            print(f"    Word {w['word_num']} -> min_x:{line['min_x']} max_x:{line['max_x']} min_y:{line['min_y']} max_y:{line['max_y']}")

# ==== CLOSE ====
conn1.close()
conn2.close()
