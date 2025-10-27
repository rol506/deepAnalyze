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
img2 = e.loadImage("test2.png")
