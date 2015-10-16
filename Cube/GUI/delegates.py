from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QItemDelegate
from mtg.Card import Card

#XDK

class CardsDelegate(QItemDelegate):
    #def drawDisplay(self, painter, option, rect, text):
    #    print painter
    #    print option
    #    print rect
    #    print text

    def paint(self, painter, option, index):
        value = index.data(Qt.DecorationRole)
        
        if value == None or (hasattr(value, "isNull") and value.isNull()):
            value = index.data(Qt.DisplayRole)
            if hasattr(value, "toString"):
                value = value.toString()

            painter.save()
            painter.drawText(option.rect, 0, value)
            painter.restore()
            return

        if hasattr(value, "toPyObject"):
            value = value.toPyObject()

        #tableView = self.parent().tableView
        #height = value.height()
        #width = value.width()

        #if tableView.rowHeight(index.row()) != height:
        #    tableView.setRowHeight(index.row(), height)

        #if tableView.columnWidth(index.column()) != width:
        #    tableView.setColumnWidth(index.column(), width)

        painter.save()
        painter.drawPixmap(option.rect, value)
        painter.restore()

    def setEditorData(self, editor, index):
        #print "editing mode?"
        value = index.data(Qt.DisplayRole).toString()
        #num = self.items.index(value)
        #editor.setCurrentIndex(num)

    def setModelData(self, editor, model, index):
        value = editor.text()

        model.setData(index.row(), index.column(), value)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
