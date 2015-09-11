from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog, QTableWidgetItem
from UI.dialogue_CardChoice import Ui_Dialog

class CardSelectionDialog(QDialog, Ui_Dialog):
    def __init__(self, parent, data, host_index):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.data = data
        self.host_index = host_index

        for i, card in enumerate(data):
            self.tableWidget.insertRow(i)

            for j in range(self.tableWidget.columnCount()):
                header = self.tableWidget.horizontalHeaderItem(j).data(Qt.DisplayRole).toString()
                header = str(header)
                 
                try:
                    k = card._data[header]
                    if not k:
                        continue
                    #k = k.replace("\n", "<br>")
                    k = QTableWidgetItem(k)
                    self.tableWidget.setItem(i, j, k)
                except (AttributeError, KeyError, TypeError) as e:
                    print(e)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()

    def accept(self):        
        if self.tableWidget.selectionModel().selection().indexes():
            for i in self.tableWidget.selectionModel().selection().indexes():
                row = i.row()
            card = self.data[row]
            self.parent()._card_database.append(card)
            self.parent().tablemodel.setData(self.host_index.row(), self.host_index.column(), card.name)

        super(CardSelectionDialog, self).accept()