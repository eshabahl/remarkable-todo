from rmscene import read_blocks, SceneLineItemBlock
from PIL import Image, ImageDraw
import Vision
from Foundation import NSURL

# Checklist template, numbers from the template file
FIRST_ROW = 270
ROW_H = 97.4


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


f = open("test_pages/page1.rm", "rb")
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

# put each stroke in a row using the middle of the stroke
rows = {}
for s in strokes:
    ys = [p[1] for p in s]
    middle = (min(ys) + max(ys)) / 2
    row = int((middle - FIRST_ROW) / ROW_H)
    if row not in rows:
        rows[row] = []
    rows[row].append(s)

for row in sorted(rows):
    img = Image.new("RGB", (1404, 140), "white")
    draw = ImageDraw.Draw(img)
    top = FIRST_ROW + row * ROW_H - 60
    for s in rows[row]:
        moved = []
        for x, y in s:
            moved.append((x, y - top))
        draw.line(moved, fill="black", width=4)
    img.save("row.png")
    text = read_text("row.png")
    if len(text) > 0:
        print(row, text[0])
