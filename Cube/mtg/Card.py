from PyQt5 import QtGui, QtCore
import os
import json
from collections import defaultdict

try:
    from common import urlopen, quote, QString
    from mtg import *
except ImportError:
    import sys
    fpath, _ = os.path.split(__file__)
    sys.path.append(os.path.join(fpath, ".."))
    from common import urlopen, quote, QString
    from __init__ import *

#CARD_HEIGHT = 310
#CARD_WIDTH  = 223
CARD_WIDTH, CARD_HEIGHT = (312, 445)

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
        elif type(name_or_multiverse_id) in [str, QString]:
            data = self._getJSONdata(name_or_multiverse_id)
            if data:
                self._data.update(data[0])
        elif type(name_or_multiverse_id) in [dict]:
            if name_or_multiverse_id:
                self._data = name_or_multiverse_id
        else:
            raise Exception("Unhandled type %s!"  % type(name_or_multiverse_id))

        return super(Card, self).__init__(*args, **kwargs)

    def __repr__(self):
        if self.name:
            return "<Card(%s)>" % self.name.encode("utf8")
        else:
            return super(Card,self).__repr__()

    @property
    def multiverse_id(self):
        return self._data['id'] if 'id' in self._data.keys() else self._data['multiverseid']

    @property
    def name(self):
        return self._data['name']#.encode("utf8")

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
        set = self.printings[0].lower()

        #WA: Apocolypse set  is AP under magiccards.info
        if set == "apc":
            set = "ap"

        return PIC_BY_SETID.format(set=set,
                                   language="en",
                                   cardnum=self.number)

    def getImage(self):
        if not self.image_data.isNull():
            return self.image_data

        CACHED_IMAGE = os.path.join(IMAGE_CACHE_FOLDER, "%s.jpg" % self.name)

        if os.path.exists(CACHED_IMAGE):
            image_data = QtGui.QImage(CACHED_IMAGE)
            image_data = image_data.scaled(CARD_WIDTH, CARD_HEIGHT, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.image_data.convertFromImage(image_data)
        else:
            data = urlopen(self.imageURL).read()

            with open(CACHED_IMAGE, "wb+") as f:
                f.write(data)

            self.image_data.loadFromData( data )
            self.image_data = self.image_data.scaled(CARD_WIDTH, CARD_HEIGHT, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        return self.image_data

if __name__ == "__main__":
    from PyQt5.QtGui import QApplication, QLabel
    from pprint import pprint
    import sys

    try:
        from mtg.Database import CardDatabase
    except ImportError:
        from Database import CardDatabase

    app = QApplication(sys.argv)
    lbl = QLabel("test")
    lbl.show()
    
    db = CardDatabase()

    card = db.findByName("Narset, Enlightened Master")[-1]
    print(card)
    #pprint(card._data.keys())
    #print(card.printings)
    #print(card.number)
    
    image = card.getImage()
    print(image.height())
    print(image.width())

    lbl.setPixmap(image)
    lbl.resize(image.width(), image.height())

    sys.exit(app.exec_())
