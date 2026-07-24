from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display


# ============================================================
# SETTINGS
# ============================================================

# Your QPC font
font_path = r"H:\Other Projects\Python\db\fonts\qpc_v1_by_page\qpc_page_003.ttf"

# Output image
output_path = r"H:\Other Projects\Python\db\fonts\qpc_v1_by_page\surah_2_ayah_5_15.png"


# ============================================================
# QURAN TEXT
# SURAH AL-BAQARAH - AYAH 5 TO 15
# ============================================================

ayahs = [
    "أُولَٰئِكَ عَلَىٰ هُدًى مِّن رَّبِّهِمْ ۖ وَأُولَٰئِكَ هُمُ الْمُفْلِحُونَ",

    "إِنَّ الَّذِينَ كَفَرُوا سَوَاءٌ عَلَيْهِمْ أَأَنذَرْتَهُمْ أَمْ لَمْ تُنذِرْهُمْ لَا يُؤْمِنُونَ",

    "خَتَمَ اللَّهُ عَلَىٰ قُلُوبِهِمْ وَعَلَىٰ سَمْعِهِمْ ۖ وَعَلَىٰ أَبْصَارِهِمْ غِشَاوَةٌ ۖ وَلَهُمْ عَذَابٌ عَظِيمٌ",

    "وَمِنَ النَّاسِ مَن يَقُولُ آمَنَّا بِاللَّهِ وَبِالْيَوْمِ الْآخِرِ وَمَا هُم بِمُؤْمِنِينَ",

    "يُخَادِعُونَ اللَّهَ وَالَّذِينَ آمَنُوا وَمَا يَخْدَعُونَ إِلَّا أَنفُسَهُمْ وَمَا يَشْعُرُونَ",

    "فِي قُلُوبِهِم مَّرَضٌ فَزَادَهُمُ اللَّهُ مَرَضًا ۖ وَلَهُمْ عَذَابٌ أَلِيمٌ بِمَا كَانُوا يَكْذِبُونَ",

    "وَإِذَا قِيلَ لَهُمْ لَا تُفْسِدُوا فِي الْأَرْضِ قَالُوا إِنَّمَا نَحْنُ مُصْلِحُونَ",

    "أَلَا إِنَّهُمْ هُمُ الْمُفْسِدُونَ وَلَٰكِن لَّا يَشْعُرُونَ",

    "وَإِذَا قِيلَ لَهُمْ آمِنُوا كَمَا آمَنَ النَّاسُ قَالُوا أَنُؤْمِنُ كَمَا آمَنَ السُّفَهَاءُ ۗ أَلَا إِنَّهُمْ هُمُ السُّفَهَاءُ وَلَٰكِن لَّا يَعْلَمُونَ",

    "وَإِذَا لَقُوا الَّذِينَ آمَنُوا قَالُوا آمَنَّا وَإِذَا خَلَوْا إِلَىٰ شَيَاطِينِهِمْ قَالُوا إِنَّا مَعَكُمْ إِنَّمَا نَحْنُ مُسْتَهْزِئُونَ",

    "اللَّهُ يَسْتَهْزِئُ بِهِمْ وَيَمُدُّهُمْ فِي طُغْيَانِهِمْ يَعْمَهُونَ",
]


# ============================================================
# FONT SETTINGS
# ============================================================

font_size = 48

# Image width
image_width = 1600

# Margins
top_margin = 80
bottom_margin = 80

# Space between lines
line_spacing = 35


# ============================================================
# LOAD FONT
# ============================================================

try:
    font = ImageFont.truetype(
        font_path,
        font_size
    )

    print("Font loaded successfully:")
    print(font_path)

except Exception as e:
    print("ERROR: Could not load font")
    print(e)
    exit()


# ============================================================
# PREPARE ARABIC TEXT
# ============================================================

display_ayahs = []

for ayah in ayahs:

    # Arabic character shaping
    reshaped_text = arabic_reshaper.reshape(ayah)

    # Convert Arabic to visual RTL order
    display_text = get_display(reshaped_text)

    display_ayahs.append(display_text)


# ============================================================
# CALCULATE LINE HEIGHT
# ============================================================

bbox = font.getbbox("أ")

line_height = bbox[3] - bbox[1]

print("Line height:", line_height)


# ============================================================
# CALCULATE IMAGE HEIGHT
# ============================================================

number_of_lines = len(display_ayahs)

image_height = (
    top_margin
    + (line_height + line_spacing) * number_of_lines
    + bottom_margin
)


print("Number of Ayahs:", number_of_lines)

print(
    "Image size:",
    image_width,
    "x",
    image_height
)


# ============================================================
# CREATE IMAGE
# ============================================================

image = Image.new(
    "RGB",
    (
        image_width,
        image_height
    ),
    "white"
)

draw = ImageDraw.Draw(image)


# ============================================================
# DRAW AYAH TEXT
# ============================================================

y = top_margin


for index, display_text in enumerate(
    display_ayahs,
    start=5
):

    # Calculate text dimensions
    bbox = draw.textbbox(
        (0, 0),
        display_text,
        font=font
    )

    text_width = bbox[2] - bbox[0]

    text_height = bbox[3] - bbox[1]


    # Center text horizontally
    x = (
        image_width
        - text_width
    ) // 2


    # Draw text
    draw.text(
        (
            x,
            y
        ),
        display_text,
        font=font,
        fill="black"
    )


    print(
        f"Rendered Ayah 2:{index}"
    )


    # Move to next line
    y += (
        line_height
        + line_spacing
    )


# ============================================================
# SAVE IMAGE
# ============================================================

image.save(
    output_path
)


# ============================================================
# DONE
# ============================================================

print()
print("==========================================")
print("IMAGE CREATED SUCCESSFULLY")
print("==========================================")
print()
print("Output:")
print(output_path)
print()
print("Surah: Al-Baqarah")
print("Ayahs: 5 - 15")
print("Total Ayahs:", len(ayahs))
print("Image Width:", image_width)
print("Image Height:", image_height)