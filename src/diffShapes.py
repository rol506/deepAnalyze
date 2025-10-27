import logging
import sys
import copy
from engine import Engine

DEBUG = True

logging.basicConfig(encoding="utf-8", level=logging.DEBUG, 
                    format="%(levelname)s %(asctime)s %(message)s",
                    handlers=[logging.FileHandler("log.txt", ("w" if DEBUG else "w+")), logging.StreamHandler(sys.stdout)])

e = Engine()
img = e.loadImage("test1.png")
img2 = e.loadImage("test1.png")
r = copy.deepcopy(img)
r2 = copy.deepcopy(img2)
if img is None:
    exit(0)

gray = e.grayscaleImage(img)
gray2 = e.grayscaleImage(img2)
contours = e.findContours(gray)
contours2 = e.findContours(gray2)

df = e.findDiffShapes(contours, contours2)
if df is None:
    print("No diff in shapes!")
else:
    r = e.drawContours(r, df[0])
    r2 = e.drawContours(r2, df[1])

#e.viewImages(r, r2)
e.exportImage(e.horizontalCombine(r, r2), "result.png")
	
#cropped_img = img[y_start:y_end, x_start:x_end]
