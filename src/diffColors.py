import logging
import sys
import copy
from engine import Engine
import cv2 as cv
import numpy as np

DEBUG = True

logging.basicConfig(encoding="utf-8", level=logging.DEBUG, 
                    format="%(levelname)s %(asctime)s %(message)s",
                    handlers=[logging.FileHandler("log.txt", ("w" if DEBUG else "w+")), logging.StreamHandler(sys.stdout)])

e = Engine()
img = e.loadImage("testShapes.png")
img2 = e.loadImage("testColors.png")
r = copy.deepcopy(img)
r2 = copy.deepcopy(img2)

gray = e.grayscaleImage(img)
gray2 = e.grayscaleImage(img2)
contours = e.findContours(gray)
contours2 = e.findContours(gray2)

diff = e.findDiffColors(img, img2, contours, contours2)
if diff is None:
    print("No diff in color")
else:
    for d in diff:
        r = e.drawContours(r, [d[0][0]], color=d[1][1])
        r2 = e.drawContours(r2, [d[0][1]], color=d[1][0])

e.exportImage(e.horizontalCombine(r, r2), "result.png")
	
#cropped_img = img[y_start:y_end, x_start:x_end]
