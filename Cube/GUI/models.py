import os

from lxml import etree, objectify
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex, QAbstractItemModel, QUrl, QAbstractListModel

from mtg.Card import IMAGE_CACHE_FOLDER

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
    
class CardsModel(QAbstractTableModel):
    CACHE_IMAGES = True

    def __init__(self, parent, *args, **kwargs):
        QAbstractTableModel.__init__(self, parent, *args, **kwargs)
        
        self._parent = parent

        self.manager = QNetworkAccessManager( parent=self )
        self.manager.finished.connect( self.downloadFinished )

    @property
    def xmldata(self):
        cached_group = str(self._parent.comboBox_Grouping.currentText())
        
        if not cached_group:
            cached_group = self._parent.comboBox_Grouping.currentIndex() + 1

        if not cached_group:
            return None

        if type(cached_group) == str:
            xpathcmd = "//grouping[@name='%s']" % cached_group
        elif type(cached_group) == int:
            xpathcmd = "//grouping[%s]" % (cached_group)
        else:
            xpathcmd = "//grouping"

        return self._parent._cubeData.find(xpathcmd)

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

    @property
    def cwFile(self):
        return self._parent._cubeFile

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
        flags = super(CardsModel, self).flags(QModelIndex)
        return flags | Qt.ItemIsEditable

    def data(self, index, role):
        if not index.isValid():
            #return QVariant()
            return None

        row_key = self.v_header[index.row()]
        col_key = self.h_header[index.column()]

        try:
            data_key = self.xmldata.xpath("./cards/card[@row='%s'][@column='%s'][1]/text()" % (row_key, col_key))
            data_key = data_key[0]
        except IndexError:
            #return QVariant()
            return None

        if role == Qt.DisplayRole:
            return str(data_key)
        elif role == Qt.DecorationRole:
            card = self._parent._card_database.findByName(data_key)
            card = list(filter(lambda acard: acard._getImageFailed == False, card))
            try:
                card = card[0]
                image_data = card.image_data
            except IndexError:
                return None

            if not image_data.isNull():
                return image_data
            
            self.downloadImage(card)

        return None

    def downloadImage(self, card):
        url = QUrl(card.imageURL)
        request = QNetworkRequest(url)
        cardloc = self._parent._card_database.index(card)
        
        if not cardloc:
            return
        
        reply = self.manager.get(request)
        reply.setAttribute(QCardLocation, cardloc)

    def downloadFinished(self, reply, *args):
        cardloc = reply.attribute(QCardLocation)
        card = self._parent._card_database[cardloc]
                                       
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
        
        if self.CACHE_IMAGES:
            fp = os.path.join(IMAGE_CACHE_FOLDER, "%s.jpg" % card.name)
            card.image_data.save(fp)

    def setData(self, row, column, value):
        row_key = self.v_header[row]
        col_key = self.h_header[column]
        changed = False

        card = self.xmldata.find("cards")
        if not card:
            card = etree.Element("cards")
            self.xmldata.insert(0, card)

        card = card.xpath("./card[@row='%s'][@column='%s']" % (row_key, col_key))

        self.beginResetModel()
        if card and card[0].text != str(value):
            card[0].text = str(value)
            changed = True
        else:
            c = etree.Element("card", row=row_key, column=col_key)
            c.text = str(value)
            self.xmldata.find("cards").insert(0, c)
            changed = True
            
        if changed and self.cwFile:
            self._parent._fileSave()

        self.endResetModel()

    def removeData(self, index):
        row = index.row()
        col = index.column()

        row_key = self.v_header[row]
        col_key = self.h_header[col]

        self.beginResetModel()
        tricol = self.xmldata.xpath("./cards/card[@row='%s'][@column='%s']" % (row_key, col_key))[0]
        tricol.getparent().remove(tricol)

        if self.cwFile:
            self._parent._fileSave()

        self.endResetModel()