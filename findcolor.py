from PIL import Image
import webcolors

def closest_color_name(rgb):
    try:
        return webcolors.rgb_to_name(rgb, spec='css3')
    except ValueError:
        min_distance = None
        closest_name = None
        # Works in webcolors 2.x+ (no CSS3_NAMES_TO_HEX)
        for name in webcolors.names('css3'):
            hex_code = webcolors.name_to_hex(name)
            r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
            dist = (r_c - rgb[0])**2 + (g_c - rgb[1])**2 + (b_c - rgb[2])**2
            if min_distance is None or dist < min_distance:
                min_distance = dist
                closest_name = name
        return closest_name

IMAGE_PATH = r"E:\QuranSqlAllData\GwalQuran\ModificationForIndopak\InProgress\pages\MOD\page005.png"
img = Image.open(IMAGE_PATH).convert("RGB")

colors = img.getcolors(maxcolors=img.width * img.height)
colors_sorted = sorted(colors, key=lambda x: x[0], reverse=True)

print(f"Found {len(colors_sorted)} unique colors:")
for count, color in colors_sorted:
    name = closest_color_name(color)
    hex_val = webcolors.rgb_to_hex(color)
    print(f"{color} {hex_val} ({name}) → {count} pixels")


# Found 5 unique colors:
# (0, 0, 0) #000000 (black) → 2110803 pixels
# (234, 234, 234) #eaeaea (lavender) → 102525 pixels
# (162, 156, 118) #a29c76 (rosybrown) → 67929 pixels
# (204, 204, 153) #cccc99 (tan) → 47015 pixels
# (102, 51, 51) #663333 (saddlebrown) → 31024 pixels


#a29c76 , rgba(162,156,118,255) remove
#cccc99 , rgba(204,204,153,255) remove
#663333 , rgba(102,51,51,255) (remove)

#eaeaea , rgba(234,234,234,255) (check)
