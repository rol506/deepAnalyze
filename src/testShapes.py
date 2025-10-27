import logging
import sys
import copy
import os
import time
from engine import Engine
import cv2 as cv
import numpy as np
from docx import Document
from docx.shared import Inches

DEBUG = True

logging.basicConfig(encoding="utf-8", level=logging.DEBUG, 
                    format="%(levelname)s %(asctime)s %(message)s",
                    handlers=[logging.FileHandler("log.txt", ("w" if DEBUG else "w+")), logging.StreamHandler(sys.stdout)])

#def processImage(image):
#    gray = e.grayscaleImage(image)
#    contours = e.findContours(gray)
#
#    #gray = cv.cvtColor(gray, cv.COLOR_GRAY2BGR)
#    e.drawContours(image, contours)
#    #index = 49
#    #img = e.cropToContour(e.drawContours(img, [contours[index]]), contours[index])
#    return image

# returns processed image or None if no difference is found
#def findDiff(img1, img2):
#    gray1 = e.grayscaleImage(img1)
#    gray2 = e.grayscaleImage(img2)
#
#    cont1 = e.findContours(gray1)
#    cont2 = e.findContours(gray2)
#
#    r = copy.deepcopy(img1)
#    r2 = copy.deepcopy(img2)
#
#    #e.drawContours(r, cont1)
#
#    df = e.findDiffShapes(cont1, cont2)
#    if df is None:
#        logging.info("No difference in shapes found")
#        return None
#    else:
#        logging.info("Found difference in shapes!")
#        e.drawContours(r, df[0], thickness=-1, color=(0,0,255)) # draw diff contours from other img
#        e.drawContours(r2, df[1], thickness=-1, color=(0,0,255))
#        #r = e.drawContours(r, df[0])
#        #r2 = e.drawContours(r2, df[1])
#
#    diff = e.findDiffColors(img1, img2, cont1, cont2)
#    if diff is None:
#        logging.info("No difference in colors found")
#    else:
#        logging.info("Found difference in colors!")
#        for d in diff:
#            e.drawContours(r, [d[0][0]], color=d[1][1])
#            e.drawContours(r2, [d[0][1]], color=d[1][0])
#
#    return r

def loadTiles(filename, prefix, e):

    img = e.loadImage(filename)
    image_copy = img.copy() 
    imgheight=img.shape[0]
    imgwidth=img.shape[1]
    tileNames = []

    M = 500
    N = 500
    x1 = 0
    y1 = 0

    #TODO FIX CASE WHEN IMAGE IS SMALLER THAN A TILE
    if imgheight < M:
        logging.WARNING("Image height is smaller than a tile height! Undefined behaviour!")
    
    if imgwidth < N:
        logging.WARNING("Image width is smaller than a tile width! Undefined behaviour!")
     
    for y in range(0, imgheight, M):
        tileNamesRow = []
        for x in range(0, imgwidth, N):
            if (imgheight - y) < M or (imgwidth - x) < N:
                break
                 
            y1 = y + M
            x1 = x + N

            name = 'saved_patches/'+str(prefix)+'_tile'+str(x)+'_'+str(y)+'.jpg'

            # check whether the patch width or height exceeds the image width or height
            if x1 >= imgwidth and y1 >= imgheight:
                x1 = imgwidth - 1
                y1 = imgheight - 1
                #Crop into patches of size MxN
                tiles = image_copy[y:y+M, x:x+N]
                #Save each patch into file directory
                e.exportImage(tiles, name)
                #cv.rectangle(img, (x, y), (x1, y1), (0, 255, 0), 1)
            elif y1 >= imgheight: # when patch height exceeds the image height
                y1 = imgheight - 1
                #Crop into patches of size MxN
                tiles = image_copy[y:y+M, x:x+N]
                #Save each patch into file directory
                e.exportImage(tiles, name)
                #cv.rectangle(img, (x, y), (x1, y1), (0, 255, 0), 1)
            elif x1 >= imgwidth: # when patch width exceeds the image width
                x1 = imgwidth - 1
                #Crop into patches of size MxN
                tiles = image_copy[y:y+M, x:x+N]
                #Save each patch into file directory
                e.exportImage(tiles, name)
                #cv.rectangle(img, (x, y), (x1, y1), (0, 255, 0), 1)
            else:
                #Crop into patches of size MxN
                tiles = image_copy[y:y+M, x:x+N]
                #Save each patch into file directory
                e.exportImage(tiles, name)
                #cv.rectangle(img, (x, y), (x1, y1), (0, 255, 0), 1)

            tileNamesRow.append(name)

        tileNames.append(tileNamesRow)
    return tileNames

def processTiles(firstTiles, secondTiles, e, doc): 
    index = 0
    for tileRow1, tileRow2 in zip(firstTiles, secondTiles):
        for tile1, tile2 in zip(tileRow1, tileRow2):
            img1 = e.loadImage(tile1)
            img2 = e.loadImage(tile2)

            #os.remove(tile1)
            #os.remove(tile2)

            gray1 = e.grayscaleImage(img1)
            gray2 = e.grayscaleImage(img2)

            cont1 = e.findContours(gray1)
            cont2 = e.findContours(gray2)

            r = copy.deepcopy(img1)
            r2 = copy.deepcopy(img2)

            # COLOR DIFF
            diff = e.findDiffColors(img1, img2, cont1, cont2)
            if diff is None:
                logging.info("No difference in colors found")
            else:
                logging.info("Found difference in colors!")
                for d in diff:
                    #e.drawContours(r, d[0][0], color=d[1][1])
                    #e.drawContours(r2, d[0][1], color=d[1][0])
                    doc.add_heading("Найдено различие в цвете")
                    p = doc.add_paragraph()
                    run = p.add_run()
                    e.exportImage(e.cropToContour(r, d[0][0]), "tmp.jpg")
                    run.add_picture("tmp.jpg", width=Inches(2))
                    run = p.add_run()
                    e.exportImage(e.cropToContour(r2, d[0][1]), "tmp.jpg")
                    run.add_picture("tmp.jpg", width=Inches(2))
                    os.remove("tmp.jpg")

            # SHAPE DIFF
            df = e.findDiffShapes(cont1, cont2)
            if df is None:
                logging.info("No difference in shapes found")
                return None
            else:
                logging.info("Found difference in shapes!")
                e.drawContours(r, df[0], thickness=-1, color=(0,0,255)) # draw diff contours from other img
                e.drawContours(r2, df[1], thickness=-1, color=(0,0,255))
                for c1, c2 in zip(df[0], df[1]):
                    #e.viewImage(e.cropToContour(r, c1))
                    #! POSSIBLE DATA RACE
                    doc.add_heading("Различие в форме")
                    p = doc.add_paragraph()
                    run = p.add_run()
                    e.exportImage(e.cropToContour(r, c1), "tmp.jpg") 
                    run.add_picture("tmp.jpg", width=Inches(2))
                    run = p.add_run("    ")
                    e.exportImage(e.cropToContour(r2, c2), "tmp.jpg")
                    run.add_picture("tmp.jpg", width=Inches(2))
                    os.remove("tmp.jpg")

    img = None
    for ind, tileRow in enumerate(firstTiles):
        row = None
        for ind2, tile in enumerate(tileRow):
            tileImg = e.loadImage(tile)
            os.remove(tile)
            if ind2 == 0:
                row = tileImg
            else:
                row = np.concatenate((row, tileImg), axis=1)
        if row is None:
            break
        if ind == 0:
            img = row
        else:
            img = np.concatenate((img, row), axis=0)
    doc.save("summary.docx")
    return img

def processPair(first, second):
    e = Engine()
    doc = Document()

    firstTiles = loadTiles(first, "first", e)
    secondTiles = loadTiles(second, "second", e)

    start = time.time()
    img = processTiles(firstTiles, secondTiles, e, doc)
    if img is None:
        logging.error("Result image is None! Exporting first image...")
        e.exportImage(e.loadImage(first), "result.jpg")
    end = time.time()
    print(f"Process took {round(end-start, 2)}s")
