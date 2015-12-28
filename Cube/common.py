import os
import sys
import logging
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

CONSOLE_LOG_FMT = '%(asctime)s p:%(process)d t:%(thread)11d %(name)6.6s: %(levelname)-5.5s %(message)s'
logging.basicConfig(format=CONSOLE_LOG_FMT, level=logging.INFO)


__all__     = ['urlopen', 'quote', 'CACHE_FOLDER', 'find_path']
__version__ = "0.1"