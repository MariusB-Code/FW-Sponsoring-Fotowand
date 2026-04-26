# ----------------------------------------------------------
# Dieser Code wurde an der ZHAW School of Engineering für die Frackwoche 2026
# erstellt. Er dient dazu, eine Fotowand mit allen Sponsoren-Logos zu erstellen.
# Der Code ist saulangsam, daher Geduld haben :)
# Viel Spass beim verwenden! LG Marius, Kassier FW26
# ----------------------------------------------------------
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random

# ----------------------------------------------------------
# Grundeinstellungen: Canvas-Grösse (Daten der Druckerei)
# ----------------------------------------------------------
CANVAS_W_MM = 3680 # Fotowandbreite total in mm
CANVAS_H_MM = 2270 # Fotowandhöhe total in mm

SEAM_ALLOWANCE = 10 # Nahtzugabe in mm
MARGIN_MIN_MM = 50 # minimale Marge (mininaler Abstand der Bilder vom Rand) in mm
MARGIN_ADD_MM = 20 # Zusätzliche Marge vom Rand in mm
SIDE_W_MM = 290 # Falls die Druckerei die Seiten der messewand bedruckt, hier eingeben

COLS = 12   # Anzahl Spalten (Anz. Bilder horizontal) # mit 12 passen die Felder
ROWS = 11   # Anzahl Zeilen (Anz. Bilder vertikal) 
# Werte Frackwochen:
# FW26: Fotowand 4x3 mit seitenfläche, COLS = 12, ROWS = 11 (COLS = Anz. Sponsoren-Logos+2)

# Einstellung ob und wie gross (in Zellen) die Mittlere Overlay-Zelle sein soll
# ----------------------------------------------------------
center_cell_en = True   # Enable für in der Mitte der Wand zentrierte Zelle
center_cells = [2,3]    # Breite und Höhe der Zentralen Zellen anhand der normalen Zellengrösse

# Einstellungen: Debugging-Modus und PDF-Export-enable
# ----------------------------------------------------------
debug_modus = True  # Modus zum debuggen (ohne dass Bilder eingefügt werden)
pdf_export_en = False # Wenn "True": Exportiert das generierte Collage-Bild als PDF (nur wenn debug_modus = False)

# Grössen der Bilder auf der fotowand (Platinsponsoren haben grössere Bilder als Goldsponsoren)
# ----------------------------------------------------------
scale_img_large = 1.0 # Skalierung relativ zu Zelle (grösste Dimension)
scale_img_small = 0.5 # Skalierung relativ zu Zelle (grösste Dimension)

# Weitere Parameter: Margin (Bider zu Rand) sollte genug gross sein und Gap
# ----------------------------------------------------------
MARGIN_MM = SEAM_ALLOWANCE+MARGIN_MIN_MM+MARGIN_ADD_MM # Margin (Abstand der Bilder vom Rand)
GAP_MM = MARGIN_MM/2 # Abstand der Bilderzellen in mm
DPI = 300 # wird für Konvertierung vom mm zu pixel benötigt

# Pfade zum FW-Logo (Mitte), Platin-Logos (gross) & Gold-Logos (klein)
# ----------------------------------------------------------
FW_LOGO_DIR  = Path("./0-fw-logo")
LARGE_DIR = Path("./1-platin")
SMALL_DIR = Path("./2-gold")

# ----------------------------------------------------------
# Start Berechnungen aus Grundeinstellungen
# ----------------------------------------------------------
# Nutzbaren Bereich (Effektivbereich) berechnen
usable_w_mm = CANVAS_W_MM-(2*(MARGIN_MM))-(COLS-1)*GAP_MM
usable_h_mm = CANVAS_H_MM-(2*(MARGIN_MM))-(ROWS-1)*GAP_MM

# Zellgrösse berechnen
CELL_W_MM = usable_w_mm / COLS
CELL_H_MM = usable_h_mm / ROWS
print(f"Zellgrösse (bxh): {CELL_W_MM:.1f} x {CELL_H_MM:.1f} mm")

# ----------------------------------------------------------
# Funktion: mm zu Pixel mit dpi-Wert
# ----------------------------------------------------------
def mm_to_px(mm):
    return int(mm * DPI / 25.4)

# ----------------------------------------------------------
# Funktion: Bild laden und skalieren
# ----------------------------------------------------------
def render_cell_image(image_path,cell_w_px,cell_h_px,bg_color,scale=1.0):
    img = Image.open(image_path).convert("RGB")
    img_w, img_h = img.size

    # Basis-Skalierung: Skaliert auf Zellengrösse hoch oder runter
    # grösserer Faktor nehmen: max. höhe oder Breite der Zelle
    base_scale = min((cell_w_px / img_w), (cell_h_px / img_h)) 
    new_w = int(img_w * base_scale)
    new_h = int(img_h * base_scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Zusätzliche Skalierung mit Faktor
    img = img.resize((int(new_w * scale), int(new_h * scale)), Image.LANCZOS)

    # Zelle erstellen
    cell = Image.new("RGB", (cell_w_px, cell_h_px), bg_color)

    # Bild zentrieren
    x = (cell_w_px - img.width) // 2
    y = (cell_h_px - img.height) // 2
    cell.paste(img, (x, y))

    return cell # return: PIL.Image der fertigen Zelle

# ----------------------------------------------------------
# Funktion: Diagonale Anordnung
# ----------------------------------------------------------
def diagonal_indices(rows, cols):
    indices = []
    for s in range(rows + cols - 1):
        for row in range(rows):
            col = s - row
            if 0 <= col < cols:
                indices.append((row, col))
    return indices


# ----------------------------------------------------------
# Logos laden & in Zufälliger Reihenfolge in Array verpacken
# ----------------------------------------------------------
fw_img  = list(FW_LOGO_DIR.glob("*.*"))
large_imgs = list(LARGE_DIR.glob("*.*"))
small_imgs = list(SMALL_DIR.glob("*.*"))

# Pfade und Skalierung der Sponsorenbilder
cell_images = []
# Pfade und Skalierung Grosser Bilder in Array verpacken
for p in large_imgs:
    #cell_images.append((p, scale_img_large))
    if (p==1):      # Stage-Sound-Logo leicht verkleinern
        cell_images.append((p,0.9))
    else:
        cell_images.append((p,scale_img_large))
    
# Pfade und Skalierung kleiner Bilder in Array verpacken
for p in small_imgs:
    cell_images.append((p,scale_img_small))

# Pfad und Skalierung des als Zentralen Bildes
center_image = []
for p in fw_img:
    center_image.append((p,scale_img_large))



# shuffle cell_images-array
#print(f"cell_images original: ", cell_images)
random.shuffle(cell_images)
#print(f"cell_images shuffled: ", cell_images)
# ----------------------------------------------------------
# Canvas erstellen
# ----------------------------------------------------------
canvas = Image.new(
    mode="RGB",
    size=(mm_to_px(CANVAS_W_MM), mm_to_px(CANVAS_H_MM)),
    color="white")  # neutraler Hintergrund außerhalb des Rasters

canvas.info["dpi"] = (DPI, DPI)
draw = ImageDraw.Draw(canvas)

# ----------------------------------------------------------
# Raster zeichnen, Logos zeichnen oder im Debug-Modus schwarz/weiss füllen
# ----------------------------------------------------------
cell_index = 0
textsize = 500
font = ImageFont.load_default(size=textsize)
cell_w_px = mm_to_px(CELL_W_MM)
cell_h_px = mm_to_px(CELL_H_MM)
no_images = len(cell_images)


for row in range(ROWS):
    # berechne y-Koordinate für die Feld
    y_px = mm_to_px(MARGIN_MM + row*(CELL_H_MM+GAP_MM))
    for col in range(COLS):
           # berechne x-Koordinate für das Feld
        x_px = mm_to_px(MARGIN_MM + col*(CELL_W_MM+GAP_MM))

        # wenn Debug-modus: zeichne die felder ohne Bilder und mit nummern
        if debug_modus:
            fill_color = "black" if (row + col) % 2 == 0 else "gray"
            draw.rectangle(
                [x_px, y_px, x_px + cell_w_px, y_px + cell_h_px],
                fill=fill_color)
            draw.text(
                (x_px+int(cell_w_px/2)-textsize/2,y_px+int(cell_h_px/2)-textsize/2),
                str(cell_index),
                fill="white",
                font=font)
        # im Produktionsmodus:  Bild wählen, nach Modus einpassen und einfügen
        else:
            fill_color = "white"
            i = cell_index % no_images
            cell_img = cell_images[i]
            path, scale = cell_images[i]

            # Bild im Normal-Modus rendern und platzieren
            rendered = render_cell_image(path,cell_w_px,cell_h_px,fill_color,scale)
            canvas.paste(rendered, (x_px, y_px))

            
        cell_index+=1

if (center_cell_en):
    #Grösse der mittleren zelle berechnen
    gap_px = mm_to_px(GAP_MM)
    center_cell_w_px = int((cell_w_px+gap_px)*center_cells[0])
    center_cell_h_px = int((cell_h_px+gap_px)*center_cells[1])
    #Position der mittleren Zelle berechnen
    center_x_px = (mm_to_px(CANVAS_W_MM) - center_cell_w_px) // 2
    center_y_px = (mm_to_px(CANVAS_H_MM) - center_cell_h_px) // 2

    # wenn Debug-modus: zeichne das Feld ohne Bild und mit Text
    if(debug_modus):
        draw.rectangle(
            [center_x_px, center_y_px, center_x_px + center_cell_w_px, center_y_px + center_cell_h_px],
            fill="lightgray")
        draw.text(
                (center_x_px+(center_cell_w_px/3),center_y_px+(center_cell_h_px-textsize)/2),
                str("overlay-cell"),
                fill="black",
                font=font)
    # im Produktionsmodus: Bild einfügen
    else:
        path, scale = center_image[0]
        #Mittelzelle rendern & plazireen
        center_img = render_cell_image(
            image_path=path,
            cell_w_px=center_cell_w_px,
            cell_h_px=center_cell_h_px,
            bg_color="white",
            scale=scale)
        
        # Bild im Normal-Modus rendern und platzieren
        canvas.paste(center_img, (center_x_px, center_y_px))


# Wenn im Debug-Modus und seiten vorhanden sind, linien für den "Knick" zeichnen
if(debug_modus and (SIDE_W_MM>0)):
    line_x_mm = SEAM_ALLOWANCE+MARGIN_MIN_MM+SIDE_W_MM
    line_x_px = mm_to_px(line_x_mm)

    draw.line(
        [(line_x_px,0),(line_x_px,mm_to_px(CANVAS_H_MM))],
        fill="red",
        width=100)
    
    lineR_px = mm_to_px(CANVAS_W_MM-line_x_mm)
    draw.line(
        [(lineR_px,0),(lineR_px,mm_to_px(CANVAS_H_MM))],
        fill="red",
        width=100)

# ----------------------------------------------------------
# Speichern und zeigen
# ----------------------------------------------------------
if(debug_modus):
    canvas.save("raster_debug_auto_cells.png", dpi=(DPI, DPI))
    
else:
    canvas.save("Fotowand.png", dpi=(DPI, DPI))

canvas.show()

#als PDF speichern
if(pdf_export_en and not debug_modus):
    # ZUM KORREKTEN EXPORT MUSS DER CANVAS GLEICH GROSS WIE DIE SOLL-ENDGRÖSSE DER DATEI SEIN!!!
    canvas.save("Fotowand_FW.pdf", "PDF", dpi=(DPI, DPI))
