import sys
from PyQt5 import uic, Qt, QtGui
import sqlite3
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from base64 import b64encode as enc64
from base64 import b64decode as dec64
from io import BytesIO
from PIL import Image
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtGui import QPainter, QPen, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QPoint, QLineF


class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)
        self.mouse_press = None

    def mousePressEvent(self, event):

        if event.button() == QtCore.LeftButton:
            self.mouse_press = "mouse left press"
        elif event.button() == QtCore.RightButton:
            self.mouse_press = "mouse right press"
        elif event.button() == QtCore.MidButton:
            self.mouse_press = "mouse middle press"
        super(TableWidget, self).mousePressEvent(event)

    def row_column_clicked(self, row, column):
        # print(f'clicked: row={row}, column={column}')
        widget = self.tableWidget.cellWidget(row, 3)
        self.label.setPixmap(widget.pixmap())


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('PDDO.ui', self)

        self.s_rassczet.clicked.connect(self.s_ras) #площадь
        #столбцы таблицы
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(1, 150)
        self.tableWidget.setColumnWidth(2, 30)
        self.tableWidget.setHorizontalHeaderLabels(["Name", "View", "Image"])
        self.loaddata()
        self.le_search.setPlaceholderText("Введите текст...")
        self.bt_le_search.clicked.connect(self.OnSearch)
        self.dlina.setPlaceholderText("Введите высоту...")
        self.line.clicked.connect(self.pixmap_add)

        # Указанная строка и столбец - это ячейка, которая была нажата.
        #self.tableWidget.cellPressed[int, int].connect(self.clickedRowColumn)
        #self.pushButton_add.clicked.connect(self.on_add_record)  # "Добавить запись"))
        #self.pushButton_delete.clicked.connect(self.on_del_record)  # "Удалить запись"))
        '''self.label_3 = QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(500, 10, 771, 1021))
        pixm = QPixmap()
        size = QtCore.QSize(771, 1021)
        self.label_3.setPixmap(pixm.scaled(size, QtCore.Qt.KeepAspectRatio))
        self.show()
        self.pos = None'''
        #self.label_3.mousePressEvent = self.getPos
        #self.label_3.mouseReleaseEvent = self.getPos1
        #self.begin = QtCore.QPoint()
        #self.end = QtCore.QPoint()

        self.lines = []
        self.drawing = False
        self.startPoint = None
        self.endPoint = None
        self.pixelSpacing = 2


    #Подключение к бд
    def loaddata(self, pict=None):
        self.row_count = 1
        #self.table_index = 0
        sqlite_connection = sqlite3.connect('people.db')
        sqlite_connection.text_factory = bytes

        cursor = sqlite_connection.cursor()

        sqlite_select_query = """SELECT * FROM people"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        self.tableWidget.verticalHeader().setDefaultSectionSize(100)  # +++

        for i, row in enumerate(records):
            self.tableWidget.setRowCount(self.row_count)
            self.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(str((row[0]), 'utf-8')))
            self.tableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(str((row[1]), 'utf-8')))
            #self.tableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(row[2]))

            label_2 = QtWidgets.QLabel()
            label_2.setGeometry(QtCore.QRect(501, 11, 771, 1021))
            pix = QPixmap()
            pix.loadFromData(row[2])

            _size = QtCore.QSize(771, 1021)
            label_2.setPixmap(pix.scaled(_size, QtCore.Qt.KeepAspectRatio))

            #self.tableWidget.setItem(self.table_index, 2, QtWidgets.QTableWidgetItem(row[2]))
            self.tableWidget.setCellWidget(i, 2, label_2)

            #self.table_index += 1
            self.row_count += 1
        cursor.close()
        sqlite_connection.close()
        self.tableWidget.cellClicked.connect(self.row_column_clicked)



    def row_column_clicked(self, row, column):
        print(f'clicked: row={row}, column={column}')
        widget = self.tableWidget.cellWidget(row, 2)
        self.label_2.setPixmap(widget.pixmap())


#Линии
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #            self.drawing = True
            #            self.LastPoint = event.pos()
            #
            self.drawing = True
            self.startPoint = event.pos()
            self.update()


    def mouseMoveEvent(self, event):
        if self.startPoint:  # +++
            self.endPoint = event.pos()  # +++
            self.update()

    def mouseReleaseEvent(self, event):
            if self.startPoint and self.endPoint:
                line = QLineF(self.startPoint, self.endPoint)  # !!! QLineF
                self.lines.append({
                    'points': line,
                    'distance': round(line.length(), 2) * self.pixelSpacing,
                })
                self.startPoint = self.endPoint = None
                self.drawing = False
                self.update()

    def pixmap_add(self):
        label_3 = QtWidgets.QLabel()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Image", "",
                                                            "Image Files (*.png *.jpg *.jpeg *.bmp)")
        pixmap = QPixmap(fileName)
        label_3.setGeometry(QtCore.QRect(500, 10, 771, 1021))
        size = QtCore.QSize(771, 1021)
        label_3.setPixmap(pixmap.scaled(size, QtCore.Qt.KeepAspectRatio))

    def paintEvent(self, event):
#////ТУТ

        painter = QPainter(self)
        #painter.drawPixmap(self.rect(), self.pixmap)
        painter.setRenderHints(QPainter.Antialiasing)

        if self.startPoint and self.endPoint:
            painter.drawLine(self.startPoint, self.endPoint)
            painter.end()

        linePen = QPen(Qt.red, 2.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)

        for lineData in self.lines:
            line = lineData['points']
            painter.setPen(linePen)
            painter.drawLine(line.p1(), line.p2())
            painter.setPen(Qt.blue)
            painter.drawText(line.p2() + QPoint(0, 10),
                '{} mm'.format(lineData['distance']))




#Поиск в бд
    def OnSearch(self):
        word = self.le_search.text()
        if word:
            for row in range(self.tableWidget.rowCount()):
                match = False
                for cols in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(row, cols)
                    if item is not None and item.text() == word:
                        match = True
                        break
                self.tableWidget.setRowHidden(row, not match)
        else:
            for row in range(self.tableWidget.rowCount()):
                self.tableWidget.setRowHidden(row, False)

#Добавление записи в бд


#клик по бд
    '''def clickedRowColumn(self, row, cols):
       self.tableWidget = TableWidget()
        print("{}: row={}, column={}".format(self.tableWidget.mouse_press, row, cols))'''


    def s_ras(self):

        l = self.dlina.text()
        print('Dlina=', l)
        s = float(l) + 1
        s1 = s * 0.2646

        print('Dlina=', s1)
        self.ploshad.setText(str(s1))

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = App()
    ex.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')






