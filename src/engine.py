import cv2 as cv
import numpy as np
import logging
import os
import copy

class Engine:
    def __init__(self):
        self.__log = logging.getLogger(__name__)

    # returns image size (width, height)
    def getImageSize(self, image):
        width = image.shape[0]
        height = image.shape[1]
        return (width, height)

    def genBlankImage(self, width, height):
        self.__log.info(f"Generating {width}x{height} blank image")
        image = np.zeros((height, width,3), np.uint8)
        #self.__log.info("Blank image generated!")
        return image

    def genMask(self, image, contour):
        width, height, channels = image.shape
        #self.__log.info(f"Generating {width}x{height} image mask")
        mask = np.zeros(image.shape[:2], np.uint8)
        cv.drawContours(mask, [contour], -1, 255, -1)
        return mask

    def exportImage(self, image, filename):
        self.__log.info(f"Exporting image as '{filename}'")
        if os.path.exists(filename):
            self.__log.warning(f"'{filename}' already exists! It will be overwritten!")
        width, height = self.getImageSize(image)
        self.__log.debug(f"Writing {width}x{height} image")
        cv.imwrite(filename, image)
        #self.__log.info(f"Image exported successfully!")

    # returns None in case of an error
    def loadImage(self, filename):
        self.__log.info(f"Loading image '{filename}'")
        if not os.path.exists(filename):
            self.__log.error(f"File does not exist!")
            return None
        img = cv.imread(filename)
        #self.__log.info(f"Image loaded successfully!")
        return img

    def viewImage(self, image):
        self.__log.debug("Viewing image")
        cv.imshow("Showing image", image)
        cv.waitKey(0)
        #self.__log.debug("Image view cancelled!")

    def viewImages(self, image1, image2):
        self.__log.debug("Viewing two images horizontally")
        comb = self.horizontalCombine(image1, image2)
        if comb is None:
            self.__log.debug("Image view cancelled due to combination errors!")
            return
        cv.imshow("Showing image", comb)
        cv.waitKey(0)
        #self.__log.debug("Image view cancelled!")

    def cropImage(self, image, xStart, xEnd, yStart, yEnd):
        cropped = image[yStart:yEnd, xStart:xEnd]
        return cropped

    # cropps image and changes contours. Returns (image, contours)
    def cropToContour(self, image, contour):
        self.__log.info("Cropping image to contour")
        width, height, channels = image.shape
        x, y, w, h = cv.boundingRect(contour)
        x2 = x+w
        y2 = y+h
        offset = 200 #px

        x -= offset
        if x <= 0:
            x = 1

        y -= offset
        if y <= 0:
            y = 2

        x2 += offset
        if x2 >= width:
            x2 = width-1

        y2 += offset
        if y2 >= height:
            y2 = height-1

        return image[min(y, y2):max(y, y2), min(x, x2):max(x, x2)]

    def grayscaleImage(self, image, invert=False):
        cpy = copy.deepcopy(image)
        self.__log.info("Grayscaling image")
        img = cv.cvtColor(cpy, cv.COLOR_BGR2GRAY)
        ret, img = cv.threshold(img, 0, 255, cv.THRESH_OTSU)

        # sobel magnitude
        sx = cv.Sobel(img, cv.CV_32F, 1, 0)
        sy = cv.Sobel(img, cv.CV_32F, 0, 1)
        img = cv.magnitude(sx,sy)
        img = cv.normalize(img, None, 0.0, 255.0, cv.NORM_MINMAX, cv.CV_8U)

        if invert:
            img = cv.bitwise_not(img)
        return img

    def findContours(self, image, limit=-1):
        self.__log.info("Finding contours")
        contours, hierarchy = cv.findContours(image, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
        #self.__log.info("Contours found!")
        self.__log.info(f"Found {len(contours)} contours")
        if len(contours) > limit and limit > 0:
            return contours[:limit]
        return contours

    def drawContours(self, image, contours, color=(0,0,255), thickness=2, drawBoundingBox=False):
        self.__log.info("Drawing contours")
        if drawBoundingBox:
            for i in contours:
                x, y, w, h = cv.boundingRect(i)
                cv.rectangle(image, (x, y), (x+w, y+h), color ,2)
        else:
            cv.drawContours(image, contours, -1, color,thickness=thickness)

    def drawDot(self, image, position):
        self.__log.info("Drawing a dot on the image")
        cv.circle(image, position, 3, (0,255,0), -1)
        return image

    # returns None in case of an error
    def horizontalCombine(self, image1, image2):
        self.__log.info("Combining two images horizontally")
        if (image1.shape != image2.shape):
            self.__log.error("Two images must have same size and depth!")
            return None
        res = np.concatenate((image1, image2), axis=1)
        #self.__log.info("Combined two images horizontally!")
        return res

    # returns [[first contours array], [second contours array]] or None if contours are equal
    def findDiffShapes(self, contours, contours2):
        self.__log.info("Searching for difference in shapes")
        diff = [[], []]
        for i, j in zip(contours, contours2):
            if self.findDiffVertices(i, j) is not None:
                diff[0].append(i)
                diff[1].append(j)
        return diff if len(diff[0]) > 0 else None

    # returns indices of the different vertices or if contours are equal
    def findDiffVertices(self, cont1, cont2):
        self.__log.info("Searching for difference in vertices")
        indices = []
        for index, it in enumerate(zip(cont1, cont2)):
            if not (it[0] == it[1]).all():
                indices.append(index)
        return indices if len(indices) > 1 else None

    def getColor(self, image, contour):
        #self.__log.info("Getting mean color of an area")
        mask = self.genMask(image, contour)
        clr = cv.mean(image, mask=mask)
        cpy = list(copy.deepcopy(clr))
        for ind, c in enumerate(clr):
            cpy[ind] = round(c)
        return cpy

    # returns [((first contour, second contour) (first color, second color))]
    def findDiffColors(self, image1, image2, contours1, contours2):
        self.__log.info("Searching for difference in colors")
        res = []
        for i, j in zip(contours1, contours2):
            c1 = self.getColor(image1, i)
            c2 = self.getColor(image2, j)
            print(c1, c2)
            if c1 != c2:
                res.append(((i, j), (c1, c2)))
        return res if len(res) > 1 else None
