import os

from lxml import etree, objectify
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex, QAbstractItemModel, QUrl, QAbstractListModel

try:
    from common import IMAGE_CACHE_FOLDER, CARD_WIDTH, CARD_HEIGHT
    #from mtg import *
except ImportError:
    import sys
    fpath, _ = os.path.split(__file__)
    sys.path.append(os.path.join(fpath, ".."))
    from common import IMAGE_CACHE_FOLDER, CARD_WIDTH, CARD_HEIGHT
    #from __init__ import *

QCardLocation = QNetworkRequest.User

class XPathModel(QAbstractListModel):
    def __init__(self, tree, xpath, parent=None):
        QAbstractListModel.__init__(self, parent=parent)
        self._tree=tree
        self._xpath=xpath

    def _allElements(self):
        if isinstance(self._xpath, str):
            self._xpath=etree.XPath(self._xpath)
            return self._allElements()
        else:
            return self._xpath(self._tree)

    def data(self, index, role):
        if not index.isValid():
            return None

        el = self._allElements()[index.row()]
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return self._displayRole(el)
        elif role == Qt.DecorationRole:
            return self._decorationRole(el)
        elif role == Qt.UserRole:
            return el
        elif role == Qt.CheckStateRole:
            return self._checkRole(el)

    def _displayRole(self, el):
        return el.tag
    
    def _decorationRole(self, el):
        pass
    
    def _checkRole(self, el):
        pass

    def rowCount(self, index=QModelIndex()):
        return len(self._allElements())

class GroupingModel(XPathModel):
    def __init__(self, parent, *args, **kwargs):
        QAbstractListModel.__init__(self, parent, *args, **kwargs)
        self._parent = parent
        self._xpath = "//grouping"

    @property
    def _tree(self):
        return self._parent._cubeData

    def rowCount(self, parent):
        if self._tree:
            return self._tree.xpath("count(%s)" % self._xpath )
        else:
            return 0
    
    def _displayRole(self, el):
        return el.attrib['name']
    
class CubeModel(QAbstractTableModel):
    def __init__(self, cubeFile, cubeDB, parent=None, *args, **kwargs):
        QAbstractTableModel.__init__(self, parent, *args, **kwargs)
        
        self._cubeFile = cubeFile
        self._cubeData = None
        self._cubeDB   = cubeDB

        self.manager = QNetworkAccessManager( parent=self )
        self.manager.finished.connect( self.downloadFinished )

    @property
    def xmldata(self):
        cached_group = u"guilds"
        #cached_group = str(self._parent.comboBox_Grouping.currentText())
        
        #if not cached_group:
        #    cached_group = self._parent.comboBox_Grouping.currentIndex() + 1

        #if not cached_group:
        #    return None

        if type(cached_group) == str:
            xpathcmd = "//grouping[@name='%s']" % cached_group
        elif type(cached_group) == int:
            xpathcmd = "//grouping[%s]" % (cached_group)
        else:
            xpathcmd = "//grouping"

        return self._cubeData.find(xpathcmd)

    @property
    def h_header(self):
        try:
            return self.xmldata.xpath("./headers/header/text()")
        except AttributeError:
            return []

    @property
    def v_header(self):
        try:
            return self.xmldata.xpath("./vheaders/vheader/text()")
        except AttributeError:
            return []

    def rowCount(self, parent=None):
        return len(self.v_header)

    def columnCount(self, parent=None):
        return len(self.h_header)

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.h_header[section])
            elif orientation == Qt.Vertical:
                return str(self.v_header[section])
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def flags(self, QModelIndex):
        flags = super(CubeModel, self).flags(QModelIndex)
        return flags | Qt.ItemIsEditable

    def data(self, index, role):
        if not index.isValid():
            return None

        row_key = self.v_header[index.row()]
        col_key = self.h_header[index.column()]

        data_key = self.xmldata.xpath("./cards/card[@row='%s'][@column='%s'][1]/text()" % (row_key, col_key))

        if not data_key:
            return None
        
        data_key = data_key[0]

        if role == Qt.DisplayRole:
            return str(data_key)
        elif role == Qt.DecorationRole:
            card = self._cubeDB.findByName(data_key)
            card = list(filter(lambda acard: acard._getImageFailed == False, card))
            try:
                card = card[0]
            except IndexError:
                return None

            if not card.image_data.isNull():
                return card.image_data
            
            card.getImage(networkAccessManager=self.manager)

        return None

    def downloadFinished(self, reply, *args):
        card = reply.attribute(QCardLocation)
                                       
        if reply.error() != QNetworkReply.NoError:
            # request probably failed
            print(reply.errorString())
            card._getImageFailed = True
            return

        data = reply.readAll()

        self.beginResetModel()
        card.image_data.loadFromData( data )
        #card.image_data = self.image_data.scaled(CARD_WIDTH, CARD_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.endResetModel()
        
        del data

        fp = os.path.join(IMAGE_CACHE_FOLDER, "%s.png" % card.multiverse_id)
        card.image_data.save(fp)

    def setData(self, index, value, role = Qt.EditRole):
        row_key = self.v_header[index.row()]
        col_key = self.h_header[index.column()]

        cards = self.xmldata.find("cards")
        if not len( cards ):
            cards = etree.Element("cards")
            self.xmldata.insert(0, cards)

        card = cards.xpath("./card[@row='%s'][@column='%s']" % (row_key, col_key))

        self.beginResetModel()
        if len(card) and card[0].text != str(value):
            card[0].text = str(value)
        else:
            c = etree.Element("card", row=row_key, column=col_key)
            c.text = str(value)
            cards.insert(0, c)
        self.endResetModel()

        if self._cubeFile:
            #self._parent._fileSave()
            pass

        return True

    def removeData(self, index):
        row_key = self.v_header[index.row()]
        col_key = self.h_header[index.column()]

        self.beginResetModel()
        tricol = self.xmldata.xpath("./cards/card[@row='%s'][@column='%s']" % (row_key, col_key))[0]
        tricol.getparent().remove(tricol)

        self.endResetModel()

        if self.cubeFile:
            #self._parent._fileSave()
            pass


if __name__ == "__main__":
    import sys

    from PyQt5.QtWidgets import QApplication, QTableView

    from mtg.Database import CardDatabase

    app = QApplication(sys.argv)

    db = CardDatabase()

    mdl = CubeModel(os.path.abspath(r".\MyCube.xml"), db, parent=app)
    mdl._cubeData = etree.parse(mdl._cubeFile)

    tbl = QTableView()
    tbl.setModel(mdl)
    tbl.resize(800, 600)

    for i in range(mdl.columnCount()):
        tbl.setColumnWidth(i, CARD_WIDTH)

    for i in range(mdl.rowCount()):
        tbl.setRowHeight(i, CARD_HEIGHT)

    tbl.show()

    sys.exit(app.exec_())