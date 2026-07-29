import sqlite3
import os
import shutil

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

SOURCE_DB = r"H:\Other Projects\Python\db\quranV2.sqlite"
OUTPUT_DB = r"H:\Other Projects\Python\db\quranV3.sqlite"


# ---------------------------------------------------------
# Translation Data
# id, language, title, assetpath, dbfilename
# ---------------------------------------------------------

translations = [
    (101, "Albanian", "Hasan Nahi", "on_lang_pack_albanian", "albanian_hasan_nahi"),
    (111, "Azerbaijani", "Musayev", "on_lang_pack_azerbaijani", "azerbaijani_musayev"),
    (121, "Bangla", "Muhiuddin Khan", "on_lang_pack_bangla", "bangla_muhiuddin_khan"),
    (131, "Bosnian", "Korkut", "on_lang_pack_bosnian", "bosnian_korkut"),
    (141, "Bulgarian", "Tsvetan Teofanov", "on_lang_pack_bulgarian", "bulgarian_tsvetan_teofanov"),
    (151, "Chinese", "Ma Jain (Simplified)", "on_lang_pack_chinese", "chinese_ma_jain_simplified"),
    (161, "Czeck", "Hrbek", "on_lang_pack_czeck", "czeck_hrbek"),
    (171, "Dutch", "M. F. Abdasalaam", "on_lang_pack_dutch", "dutch_m_f_abdasalaam"),

    (181, "English", "Sahih International", "on_lang_pack_english", "english_sahih_international"),
    (182, "English", "Pickthall", "on_lang_pack_english", "english_pickthall"),
    (183, "English", "Abdul Haleem", "on_lang_pack_english", "english_abdul_haleem"),
    (184, "English", "Transliteration", "on_lang_pack_english", "english_transliteration"),
    (185, "English", "Yusuf Ali", "on_lang_pack_english", "english_yusuf_ali"),

    (191, "Finnish", "Ahsen Böre", "on_lang_pack_finnish", "finnish_ahsen_b_re"),
    (201, "French", "Muhammad Hamidullah", "on_lang_pack_french", "french_muhammad_hamidullah"),

    (211, "German", "Abu Rida Muhammad", "on_lang_pack_german", "german_abu_rida_muhammad"),
    (212, "German", "A. S. F. Bubenheim and N. Elyas", "on_lang_pack_german", "german_a_s_f_bubenheim_and_n_elyas"),
    (213, "German", "Zaidan", "on_lang_pack_german", "german_zaidan"),

    (221, "Hausa", "Abubakar Mahmoud Gumi", "on_lang_pack_hausa", "hausa_abubakar_mahmoud_gumi"),
    (231, "Indonesian", "Ministry of Religious Affairs (Kemenag)", "on_lang_pack_indonesian", "indonesian_ministry_of_religious_affairs_kemenag"),
    (241, "Italian", "Hamza Roberto Piccardo", "on_lang_pack_italian", "italian_hamza_roberto_piccardo"),
    (251, "Japanese", "Ryoichi Mita", "on_lang_pack_japanese", "japanese_ryoichi_mita"),
    (261, "Korean", "Hamid Choi", "on_lang_pack_korean", "korean_hamid_choi"),

    (271, "Kurdish", "Muhammad Saleh Bamoki", "on_lang_pack_kurdi", "kurdish_muhammad_saleh_bamoki"),
    (272, "Kurdish", "Kurdish Kurmanji", "on_lang_pack_kurdi", "kurdish_kurmanji_unknown"),

    (281, "Malay", "Abdullah Muhammad Basmeih", "on_lang_pack_malay", "malay_abdullah_muhammad_basmeih"),
    (291, "Malayalam", "Abdul Hamid Haidar and Kunhi Muhammad", "on_lang_pack_malayalam", "malayalam_abdul_hamid_haidar_and_kunhi_muhammad"),
    (301, "Maranao", "Guro Alim Saromantang", "on_lang_pack_maranao", "maranao_guro_alim_saromantang"),
    (311, "Norwegian", "Einar Berg", "on_lang_pack_norwegian", "norwegian_einar_berg"),

    (321, "Persian", "Elahi Ghomshei (الهی قمشه‌ای)", "on_lang_pack_persian", "persian_elahi_ghomshei"),
    (322, "Persian", "Hossein Ansarian (حسین انصاریان)", "on_lang_pack_persian", "persian_hossein_ansarian"),
    (323, "Persian", "Naser Makarem Shirazi (ناصر مکارم شیرازی)", "on_lang_pack_persian", "persian_naser_makarem_shirazi"),

    (331, "Poland", "Bielawskiego", "on_lang_pack_poland", "poland_bielawskiego"),
    (341, "Portuguese", "Samir El Hayek", "on_lang_pack_portuguese", "portuguese_samir_el_hayek"),
    (351, "Romanian", "George Grigore", "on_lang_pack_romanian", "romanian_george_grigore"),

    (361, "Russian", "Valeriya Porokhova (Валерия Порохова)", "on_lang_pack_russian", "russian_valeriya_porokhova"),
    (362, "Russian", "Magomed-Nuri Osmanov (М. Н. О. Османов)", "on_lang_pack_russian", "russian_magomed_nuri_osmanov"),
    (363, "Russian", "Elmir Kuliev (Эльмир Кулиев)", "on_lang_pack_russian", "russian_elmir_kuliev"),

    (371, "Somali", "Mahmud Muhammad Abduh", "on_lang_pack_somali", "somali_mahmud_muhammad_abduh"),
    (381, "Spanish", "Julio Cortes", "on_lang_pack_spanish", "spanish_julio_cortes"),
    (391, "Swahili", "Ali Muhsin Al-Barwani", "on_lang_pack_swahili", "swahili_ali_muhsin_al_barwani"),
    (401, "Swedish", "Mohammed Knut Bernström", "on_lang_pack_swedish", "swedish_mohammed_knut_bernstr_m"),
    (411, "Tamil", "Jan Trust Foundation", "on_lang_pack_tamil", "tamil_jan_trust_foundation"),
    (421, "Tatar", "Yakub Ibn Nugman", "on_lang_pack_tatar", "tatar_yakub_ibn_nugman"),
    (431, "Thai", "King Fahad Quran Complex", "on_lang_pack_thai", "thai_king_fahad_quran_complex"),

    (441, "Turkish", "Diyanet Isleri", "on_lang_pack_turkish", "turkish_diyanet_isleri"),
    (442, "Turkish", "Elmalılı Hamdi Yazır", "on_lang_pack_turkish", "turkish_elmal_l_hamdi_yaz_r"),
    (443, "Turkish", "Süleyman Ateş", "on_lang_pack_turkish", "turkish_s_leyman_ate"),

    (451, "Urdu", "Abul A'la Maududi (ابوالاعلیٰ مودودی)", "on_lang_pack_urdu", "urdu_abul_a_la_maududi"),
    (452, "Urdu", "Ahmed Raza Khan (احمد رضا خان)", "on_lang_pack_urdu", "urdu_ahmed_raza_khan"),
    (453, "Urdu", "Fateh Muhammad Jalandhari (فتح محمد جالندھری)", "on_lang_pack_urdu", "urdu_fateh_muhammad_jalandhari"),

    (461, "Uzbek", "Muhammad Sodik Muhammad Yusuf(Мухаммад Содик)", "on_lang_pack_uzbek", "uzbek_muhammad_sodik_muhammad_yusuf"),
]


# ---------------------------------------------------------
# Create quranV3.sqlite by copying quranV2.sqlite
# ---------------------------------------------------------

if not os.path.exists(SOURCE_DB):
    raise FileNotFoundError(f"Source database not found:\n{SOURCE_DB}")

# Remove existing quranV3 if it already exists
if os.path.exists(OUTPUT_DB):
    os.remove(OUTPUT_DB)

print("Copying database...")

shutil.copy2(SOURCE_DB, OUTPUT_DB)

print(f"Created:\n{OUTPUT_DB}")


# ---------------------------------------------------------
# Open new database
# ---------------------------------------------------------

conn = sqlite3.connect(OUTPUT_DB)
cursor = conn.cursor()


# ---------------------------------------------------------
# Remove old tafaseer table
# ---------------------------------------------------------

print("Removing old tafaseer table...")

cursor.execute("DROP TABLE IF EXISTS tafaseer")


# ---------------------------------------------------------
# Create new tafaseer table
# ---------------------------------------------------------

print("Creating new tafaseer table...")

cursor.execute("""
    CREATE TABLE tafaseer (
        id INTEGER PRIMARY KEY,
        language TEXT NOT NULL,
        title TEXT NOT NULL,
        assetpath TEXT NOT NULL,
        dbfilename TEXT NOT NULL
    )
""")


# ---------------------------------------------------------
# Insert translations
# ---------------------------------------------------------

print("Inserting translations...")

cursor.executemany("""
    INSERT INTO tafaseer (
        id,
        language,
        title,
        assetpath,
        dbfilename
    )
    VALUES (?, ?, ?, ?, ?)
""", translations)


# ---------------------------------------------------------
# Commit changes
# ---------------------------------------------------------

conn.commit()


# ---------------------------------------------------------
# Verify data
# ---------------------------------------------------------

cursor.execute("SELECT COUNT(*) FROM tafaseer")
count = cursor.fetchone()[0]

print(f"Inserted {count} translation records.")


# ---------------------------------------------------------
# Close database
# ---------------------------------------------------------

conn.close()

print()
print("========================================")
print("Database creation completed successfully")
print("========================================")
print(f"Output: {OUTPUT_DB}")