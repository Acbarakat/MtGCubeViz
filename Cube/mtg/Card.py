import os
import json
import logging
from collections import defaultdict

from PyQt5 import QtGui, QtCore

try:
    from common import urlopen, quote
    from mtg import *
except ImportError:
    import sys
    fpath, _ = os.path.split(__file__)
    sys.path.append(os.path.join(fpath, ".."))
    from common import urlopen, quote
    from __init__ import *

log = logging.getLogger("card")
log.setLevel(logging.DEBUG)

CARD_WIDTH, CARD_HEIGHT = (223, 311)

IMAGE_CACHE_FOLDER = os.path.join( os.path.split(os.path.abspath(__file__))[0], "..", "cache" )

class Card(object):
    """description of class"""

    def __init__(self, name_or_multiverse_id, *args, **kwargs):
        self._data = defaultdict(str)
        self.image_data = QtGui.QPixmap()
        self._getImageFailed = False

        if type(name_or_multiverse_id) == int:
            data = self._getJSONdata(name_or_multiverse_id)
            if data:
                self._data.update(data)
        elif type(name_or_multiverse_id) == str:
            data = self._getJSONdata(name_or_multiverse_id)
            if data:
                self._data.update(data[0])
        elif type(name_or_multiverse_id) == dict:
            if name_or_multiverse_id:
                self._data = name_or_multiverse_id
        else:
            raise Exception("Unhandled type %s!"  % type(name_or_multiverse_id))

        del self._data["type"]
        del self._data["id"]
        del self._data["imageName"]

        return super(Card, self).__init__(*args, **kwargs)

    def __repr__(self):
        if self.name:
            return "<Card(%s)>" % self.name.encode("utf8")
        else:
            return super(Card,self).__repr__()

    @property
    def multiverse_id(self):
        return self._data['multiverseid']

    @property
    def name(self):
        return self._data['name']#.encode("utf8")

    @property
    def rarity(self):
        return self._data['rarity']

    @property
    def printings(self):
        return self._data['printings']

    @property
    def number(self):
        try:
            return self._data['number']
        except KeyError:
            return -1

    @property
    def colors(self):
        try:
            return self._data["colors"]
        except KeyError:
            return []

    @property
    def types(self):
        return self._data["types"]

    @property
    def subtypes(self):
        try:
            return self._data["subtypes"]
        except KeyError:
            return []

    @property
    def cmc(self):
        try:
            return self._data["cmc"]
        except KeyError:
            return 0

    @property
    def printings(self):
        return self._data["printings"]

    def _getJSONdata(self, value):
        query_url = "http://api.mtgdb.info/cards/%s" % quote(str(value))
        #print("Gathering card info for %s" % query_url)
        query_data = urlopen(query_url).read()
        try:
            query_data = json.loads(query_data)
        except:
            print(query_url)
            print(query_data)
            raise
            
        return query_data

    @property
    def imageURL(self):
        return r"http://gatherer.wizards.com/Handlers/Image.ashx?multiverseid=%s&type=card" % self.multiverse_id

    def getImage(self):
        if not self.image_data.isNull():
            log.debug("Image data for %s is null...", self)
            return self.image_data

        if "multiverseid" not in self._data.keys():
            log.warn("%s does not have a multiverseid, cannot download image.", self)
            return self.image_data

        CACHED_IMAGE = os.path.join(IMAGE_CACHE_FOLDER, "%s.png" % self.multiverse_id)

        log.debug("Checking image cache for %s.png", self.multiverse_id)
        if os.path.exists(CACHED_IMAGE) and os.path.getsize(CACHED_IMAGE) > 0:
            log.debug("Found %s.png", self.multiverse_id)
            log.debug("Size of %s.png is %s", self.multiverse_id, os.path.getsize(CACHED_IMAGE))
            image_data = QtGui.QImage(CACHED_IMAGE)
            #image_data = image_data.scaled(CARD_WIDTH, CARD_HEIGHT, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image_data.convertFromImage(image_data)
        else:
            log.debug("Did not found the correct %s.png", self.multiverse_id)

            log.debug("Downloading image data from %s", self.imageURL)
            data = urlopen(self.imageURL).read()

            log.debug("Writing image data to disk (%s)", CACHED_IMAGE)
            with open(CACHED_IMAGE, "wb+") as f:
                f.write(data)

            self.image_data.loadFromData( data )
            self.image_data = self.image_data.scaled(CARD_WIDTH, CARD_HEIGHT, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        return self.image_data

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QLabel
    from Database import CardDatabase

    def human(size):
        UNITS = ["B", "KB", "MB", "GB", "TB"]
        HUMANFMT = "%f %s"
        HUMANRADIX = 1024.

        for u in UNITS[:-1]:
            if size < HUMANRADIX: 
                return HUMANFMT % (size, u)
            size /= HUMANRADIX

        return HUMANFMT % (size,  UNITS[-1])

    app = QApplication(sys.argv)
    lbl = QLabel("test")
    lbl.show()
    
    db = CardDatabase()

    log.info("The size of the card database is %s", human(sys.getsizeof(db)))

    for card in db.findByName("Narset, Enlightened Master"):
        print(card)
        for k,v in card._data.items():
            print("%s:%s" % (k, v))
    
    image = card.getImage()

    lbl.setPixmap(image)
    lbl.resize(image.width(), image.height())

    sys.exit(app.exec_())
