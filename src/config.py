import sys
import os

if getattr(sys, 'frozen', None):
     basedir = sys._MEIPASS
else:
     basedir = os.path.dirname(__file__)