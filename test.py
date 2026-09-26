from rmscene import read_blocks, SceneLineItemBlock
from PIL import Image, ImageDraw
import Vision
from Foundation import NSURL

# Checklist template, numbers from the template file
FIRST_ROW = 270
ROW_H = 97.4
BOX_LEFT = 85
BOX_RIGHT = 140
BOX_H = 55


# ocrmac just froze. vision's language correction waits for a download that
# never finishes on my mac and ocrmac cant turn it off, so this is ocrmac's
# code (ocrmac.py on github) with language correction off
def read_text(path):
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(0)  # 0 = accurate
    request.setUsesLanguageCorrection_(False)
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(NSURL.fileURLWithPath_(path), None)
    handler.performRequests_error_([request], None)
    results = []
    for r in request.results():
        results.append(r.text())
    return results


def row_number(y):
    # the date at the top is above the first row
    if y < FIRST_ROW - 42:
        return None
    return int((y - FIRST_ROW + 42) / ROW_H)


def middle(stroke):
    xs = [p[0] for p in stroke]
    ys = [p[1] for p in stroke]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def is_tick(stroke, row):
    x, y = middle(stroke)
    top = FIRST_ROW + row * ROW_H
    return BOX_LEFT < x < BOX_RIGHT and top < y < top + BOX_H


def is_strike(stroke):
    xs = [p[0] for p in stroke]
    return max(xs) - min(xs) > 300


f = open("test_pages/after.rm", "rb")
strokes = []
for block in read_blocks(f):
    if isinstance(block, SceneLineItemBlock):
        # deleted strokes are still in the file but value is None
        if block.item.value is not None:
            points = []
            for p in block.item.value.points:
                # x is 0 in the middle of the page, not the left side
                points.append((p.x + 702, p.y))
            strokes.append(points)

print(len(strokes), "strokes")

page = Image.new("RGB", (1404, 1872), "white")
draw = ImageDraw.Draw(page)
for s in strokes:
    draw.line(s, fill="black", width=4)

# put each stroke in a row using the middle of the stroke
rows = {}
for s in strokes:
    x, y = middle(s)
    row = row_number(y)
    if row is None:
        continue
    if row not in rows:
        rows[row] = []
    rows[row].append(s)

for row in sorted(rows):
    top = int(FIRST_ROW + row * ROW_H - 42)
    # start after the boxes, otherwise the tick gets read as a V
    page.crop((150, top, 1404, top + 127)).save("row.png")
    text = read_text("row.png")
    done = False
    for s in rows[row]:
        if is_tick(s, row) or is_strike(s):
            done = True
    # vision sometimes splits a row into pieces
    text = " ".join(text)
    if text != "":
        print(row, text, done)
