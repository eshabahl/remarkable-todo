from rmscene import read_blocks, SceneLineItemBlock
from PIL import Image, ImageDraw
import Vision
from Foundation import NSURL

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

img = Image.new("RGB", (1404, 1872), "white")
draw = ImageDraw.Draw(img)
for s in strokes:
    draw.line(s, fill="black", width=4)
img.save("page.png")

print(read_text("page.png"))
