import sys
import os

try:
    from PyQt5.QtCore import QString
except ImportError:
    QString = str

try:
    from urllib2 import urlopen, quote
except ImportError:
    from urllib.request import urlopen, quote

def find_path(*args):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)

    return os.path.join(datadir, *args)

CACHE_FOLDER = find_path( "cache" )
if os.path.exists(CACHE_FOLDER) == False:
    os.makedirs(CACHE_FOLDER)



__all__     = ['QString', 'urlopen', 'quote', 'CACHE_FOLDER', 'find_path']
__version__ = "0.1"