import os
import sys
from json import loads

import gspread
from lxml import etree
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from GUI.models import CardsModel, GroupingModel
from GUI.delegates import CardsDelegate
from GUI.dialog import CardSelectionDialog

from common import *
from mtg.Card import Card, CARD_HEIGHT, CARD_WIDTH
from mtg.Database import CardDatabase


if __name__ == '__main__':
    if not getattr(sys, 'frozen', False):
        from UI import compile

        compile()

from UI.app_MainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    _card_database  = []
    _cubeData       = None
    _cubeFile       = None

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.errorMessageDialog = QErrorMessage(parent=self)
        self.errorMessageDialog.setWindowModality(Qt.ApplicationModal)

        self.grouping_model = GroupingModel(parent=self)
        self.tablemodel     = CardsModel(parent=self)

        self.comboBox_Grouping.setModel(self.grouping_model)

        self.tableView.setModel(self.tablemodel)
        self.tableView.setItemDelegate(CardsDelegate(self))
        self.tableView.setEditTriggers(QAbstractItemView.DoubleClicked)

        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.contextMenuEvent)

        QTimer.singleShot(500, lambda: self._initCont(*sys.argv))
    
    def _initCont(self, *args):
        self.loadDatabase()

        if len(args) > 1:
            self.errorMessage(args[1])
            self._fileLoad(args[1])

    # ------------------------------- Read-Only Properties --------------------------------

    #placehodler

    # ------------------------------- ??? --------------------------------

    def errorMessage(self, msg, block=False):
        self.errorMessageDialog.showMessage(str(msg))
        if block:
            self.errorMessageDialog.exec_()

    def loadDatabase(self):
        print("loading db")

        #TODO: Decide if a local copy should be used
        #TODO: download the file if it doesn't exist locally
        #TODO: update the file if it exits locally
        try:
            self._card_database = CardDatabase()
        except Exception as e:
            self.errorMessage("Failed to load card database (%s)\r\nExiting..." % str(e), block=True)
            print(e)
            sys.exit(1)

    # ------------------------------- FILE Actions --------------------------------
    
    FILE_EXT_FORMATS = 'Cube Data File (*.cube);;XML File (*.xml);;All Files (*)'    

    def fileOpen(self):
        options = QFileDialog.Options()

        cubeFile = QFileDialog.getOpenFileName(self,
                                               "Open Cube Data file",
                                               self._cubeFile,
                                               self.FILE_EXT_FORMATS, 
                                               options=options)
        
        if cubeFile:
            self._fileLoad(cubeFile)
            
    def fileSave(self):
        options = QFileDialog.Options()

        cubeFile = QFileDialog.getSaveFileName(self,
                                               "Save Cube Data File",
                                               self._cubeFile,
                                               self.FILE_EXT_FORMATS,
                                               options=options)
        
        if cubeFile:
            self._fileSave(cubeFile)

    def _fileLoad(self, cubeFile):
        print("Parsing {0}".format(cubeFile))
        try:
            data = etree.parse(cubeFile)
            self._cubeData = data
            self.grouping_model.reset()
            self._cubeFile = cubeFile
        except Exception as e:
            self.errorMessage("Failed to load file " + str(e))
            print(e)

    def _fileSave(self, cubeFile=None):
        if cubeFile == None:
            cubeFile = self._cubeFile

        if not cubeFile:
            self.fileSave()
            return

        self._cubeData.write(cubeFile,
                             pretty_print=True,
                             method="xml",
                             encoding="UTF-8",
                             xml_declaration=True)

    # ------------------------------- HELP Actions --------------------------------
        
    def helpAbout(self):
        QMessageBox.about(self,
                          "About %s" % __appname__, 
                          __doc__.strip())

    # ------------------------------- ??? Actions --------------------------------

    def resetTable(self):
        self.tablemodel.reset()
        for i in range(self.tablemodel.columnCount()):
            self.tableView.setColumnWidth(i, CARD_WIDTH)

        for i in range(self.tablemodel.rowCount()):
            self.tableView.setRowHeight(i, CARD_HEIGHT)

    # ------------------------------- EXPORT Actions --------------------------------

    def exportToGoogleSpreadSheet(self, username, password, sheetname):
        # Login with your Google account
        gc = gspread.login(username, password)

        # Open a worksheet from spreadsheet with one shot
        sh = gc.open(sheetname)

        wks = sh.worksheet(self.comboBox_Grouping.currentText())


        for i, vhead in enumerate(self.tablemodel.v_header):
            wks.update_cell(i+2, 1, vhead)
            for j, hhead in enumerate(self.tablemodel.h_header):
                wks.update_cell(1, j+2, hhead)

                d = self.tablemodel.index(i, j).data(Qt.DisplayRole).toPyObject()
                if d:
                    cell_data = r'=IMAGE("%s", 4, %s, %s)' % (quote(self._card_database.findByName(d)[0].imageURL), CARD_HEIGHT, CARD_WIDTH)
                else:
                    cell_data = r''
                wks.update_cell(i+2, j+2, cell_data)

        # Fetch a cell range
        #cell_list = wks.range('A1:B7')
        #print cell_list
        print("DONE!")

    # ------------------------------- Table Helpers --------------------------------

    def contextMenuEvent(self, event):
        if self.tableView.selectionModel().selection().indexes():
            for i in self.tableView.selectionModel().selection().indexes():
                row, column = i.row(), i.column()

            self.menu = QMenu(self)
            renameAction = QAction('Rename', self)
            renameAction.triggered.connect(lambda: self.renameSlot(i))
            self.menu.addAction(renameAction)

            #queryAction = QAction('Query Cards', self)
            #queryAction.triggered.connect(lambda: self.querySlot(i))
            #self.menu.addAction(queryAction)

            deleteAction = QAction('Delete Card', self)
            deleteAction.triggered.connect(lambda: self.deleteSlot(i))
            self.menu.addAction(deleteAction)
            
            self.menu.popup(QCursor.pos())

    def renameSlot(self, i):
        prev_text = i.data(Qt.DisplayRole).toString()
        text, ok = QInputDialog.getText(self,
                                        'Input Dialog',
                                        'Enter card name:',
                                        text=prev_text)
        
        if ok:
            self.tablemodel.setData(i.row(), i.column(), text)

    #TODO: Fix querying since mtgdb got shut down
    #def querySlot(self, i):
    #    row = i.row()
    #    col = i.column()

    #    row = self.tablemodel.v_header[row]
    #    col = self.tablemodel.h_header[col]

    #    tricol = self.tablemodel.xmldata
    #    rowElem = tricol.xpath(".//vheader[text()='%s']" % row)
    #    colElem = tricol.xpath(".//header[text()='%s']" % col)

    #    try:
    #        query = rowElem[0].attrib["query"]
    #    except KeyError:
    #        query = ''

    #    try:
    #        c_query = colElem[0].attrib["query"]
    #        if query and c_query:
    #            query = query + " AND " + c_query
    #        elif c_query:
    #            query = c_query
    #    except KeyError:
    #        #query = ''
    #        pass

    #    z = dict(rowElem[0].attrib)
    #    z.update(dict(colElem[0].attrib))
    #    query = query.format(**z)

    #    url = SEARCH_URL + quote(query).replace("//","%%2F")
        
    #    print("Querying %s" % url)
    #    try:
    #        url_data = urlopen(url).read()
    #        url_data = loads(url_data)
    #    except Exception as e:
    #        self.errorDialogue(str(e))
    #        return

    #    x = [ Card(d) for d in url_data ]

    #    if not x:
    #        raise Exception

    #    reply = CardSelectionDialog(self, x, i)
    #    reply = reply.exec_()

    #def deleteSlot(self, i):
    #    self.tablemodel.removeData(i)



if __name__=="__main__":
    app = QApplication(sys.argv)
    
    table = MainWindow()
    table.show()
    
    sys.exit(app.exec_())
