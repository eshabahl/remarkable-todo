from rmscene import read_blocks, SceneLineItemBlock
from PIL import Image, ImageDraw
import Vision
from Foundation import NSURL

# the page is 1404 x 1872
PAGE_W = 1404
PAGE_H = 1872

# Checklist template. y numbers from the template file,
# box x I measured from check.png
FIRST_ROW = 270
ROW_H = 97.4
BOX_LEFT = 85
BOX_RIGHT = 140
BOX_H = 55
ROWS = 16


def read_strokes(path):
    f = open(path, "rb")
    strokes = []
    for block in read_blocks(f):
        if isinstance(block, SceneLineItemBlock):
            # deleted strokes are still in the file but value is None
            if block.item.value is not None:
                points = []
                for p in block.item.value.points:
                    # x is 0 in the middle of the page, not the left side
                    points.append((p.x + PAGE_W / 2, p.y))
                strokes.append(points)
    f.close()
    return strokes


def draw_page(strokes):
    page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    draw = ImageDraw.Draw(page)
    for s in strokes:
        draw.line(s, fill="black", width=4)
    return page


def middle(stroke):
    xs = [p[0] for p in stroke]
    ys = [p[1] for p in stroke]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def row_number(y):
    # the date at the top is above the first row
    if y < FIRST_ROW - 42:
        return None
    return int((y - FIRST_ROW + 42) / ROW_H)


def find_rows(strokes):
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
    return rows


def is_tick(stroke, row):
    x, y = middle(stroke)
    top = FIRST_ROW + row * ROW_H
    return BOX_LEFT < x < BOX_RIGHT and top < y < top + BOX_H


def is_strike(stroke):
    xs = [p[0] for p in stroke]
    return max(xs) - min(xs) > 300


def row_image(page, row):
    top = int(FIRST_ROW + row * ROW_H - 42)
    # start after the boxes, otherwise the tick gets read as a V
    return page.crop((150, top, PAGE_W, top + 127))


# ocrmac just froze. vision's language correction waits for a download that
# never finishes on my mac and ocrmac cant turn it off, so this is ocrmac's
# code (ocrmac.py on github) with language correction off
def read_text(img):
    img.save("row.png")
    request = Vision.VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(0)  # 0 = accurate
    request.setUsesLanguageCorrection_(False)
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(NSURL.fileURLWithPath_("row.png"), None)
    handler.performRequests_error_([request], None)
    results = []
    for r in request.results():
        results.append(r.text())
    # vision sometimes splits a row into pieces
    return " ".join(results)
