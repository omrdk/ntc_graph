import os
import sys
import math
import numpy
from PyQt5 import QtWidgets, QtGui, uic, QtCore
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi('mainwindow.ui', self)
        self.setWindowTitle("NTC Calculation")
        self.setFixedSize(640,200)

        self.reset()
        # Button definitions
        self.btn_plot = self.findChild(QPushButton, "btn_plot")
        self.btn_rst = self.findChild(QPushButton, "btn_rst")
        self.btn_const = self.findChild(QPushButton, "btn_const")
        self.btn_rst.clicked.connect(self.reset)
        self.btn_plot.clicked.connect(self.plot)
        self.btn_const.clicked.connect(self.const)
        # Label definitions
        self.line_Vref  = self.findChild(QLabel,    "lbl_Vref")
        self.line_Rntc  = self.findChild(QLabel,    "lbl_Rntc")
        self.line_Rv  = self.findChild(QLabel,      "lbl_Rv")
        self.line_Bn  = self.findChild(QLabel,      "lbl_Bn")
        self.line_Rp  = self.findChild(QLabel,      "lbl_Rp")
        self.line_adc  = self.findChild(QLabel,  "lbl_adc")
        self.lbl_Rx = self.findChild(QLabel, "lbl_Rx")
        self.lbl_Tx = self.findChild(QLabel, "lbl_Tx")
        # LineEdit definitions
        self.line_Vref  = self.findChild(QLineEdit,    "line_Vref")
        self.line_Rntc  = self.findChild(QLineEdit,    "line_Rntc")
        self.line_Rv  = self.findChild(QLineEdit,      "line_Rv")
        self.line_Bn  = self.findChild(QLineEdit,      "line_Bn")
        self.line_Rp  = self.findChild(QLineEdit,      "line_Rp")
        self.line_adc  = self.findChild(QLineEdit,  "line_adc")

        # First values
    def reset(self):
        self.line_Vref.setText("1.16")
        self.line_Rntc.setText("10000")
        self.line_Rv.setText("66000")
        self.line_Bn.setText("3950")
        self.line_Rp.setText("0")
        self.line_adc.setText("15")
        self.lbl_Rx.setText("0.0")
        self.lbl_Tx.setText("0.0")

    def const(self):
        print("LİNE")

    def plot(self): # btn_plot a bsıldığında Graph class'ını görüntüler. (YENI PENCERE)
        # Get values from line edit
        Vref = float(self.line_Vref.text())
        Rntc = int(self.line_Rntc.text())
        Rv   = int(self.line_Rv.text())
        Bn   = int(self.line_Bn.text())
        Rp   = int(self.line_Rp.text())
        Adc  = int(self.line_adc.text())
        Tn = 1./298.
        # max. LSB value and step
        Adc = 2**Adc
        step= Adc//1024
        # Fill step_list (0 to max LSB)
        LSB_step = 0                                                            # index (ix) - başlangıç değeri 0
        step_list = []                                                          # step list 1024 adet (ix adım aralığı ile max LSB değerine kadar)
        for i in range(0,1024,1):
            step_list.append(LSB_step)
            LSB_step = int(LSB_step + step)
        global Rx_list
        global Tx_list
        Rx_list = []
        Tx_list = []
        for i in range(0,1024,1):
            if i == 0:                                                          # log0 tanımsız olduğu için 0'ı eledik
                Rx = 0
                Rx_list.append(Rx)
                Tx = 250            # 0 yapınca grafikte de 0 a düşüyor.
                Tx_list.append(Tx)
            else:
                Rx = int((Rv*step_list[i])/(Adc-step_list[i]))
                Rx_list.append(Rx)
                Tx = 1.0/(((math.log(Rx)-math.log(Rntc)))/Bn+Tn)-273   # log değeri 0 veya daha az old için geçersiz oluyor
                Tx_Round = round(Tx,1)
                Tx_list.append(Tx_Round)

        main = Graph()
        main.move(650,326)
        main.show()
        sys.exit(exec_())               #!!!! PROBLEM

class Graph(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(Graph, self).__init__(*args, **kwargs)

        global Rx_list
        global Tx_list

        self.setWindowTitle("NTC Table")

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.graphWidget.setBackground((0,0,0))
        #self.graphWidget.setTitle("NTC Table", color="w", size="20pt")

        styles = {'color':'#fff', 'font-size':'20px'}          # Axis labels 8bit rgb
        self.graphWidget.setLabel('left', 'Resistance c', **styles)
        self.graphWidget.setLabel('bottom', 'Temperature (°C)', **styles)

        self.graphWidget.showGrid(x=True, y=True)
        #self.graphWidget.setXRange(-100, 500, padding=0)        # set axis limit, first min, second max
        #self.graphWidget.setYRange(-0, 100000, padding=0)
        self.graphWidget.setLimits(xMin=Tx_list[1023]-30, xMax=Tx_list[1], yMin=-150000, yMax=1000000)

        pen = pg.mkPen(color=(255, 255, 255), width=1, style=QtCore.Qt.SolidLine)   # plot line with dashes anad configure width
        self.graphWidget.plot(Tx_list, Rx_list, pen=pen)             # plot data: x, y values

        # mouse event (koordinatlar)
        self.curve = pg.TextItem(text="Tx: {} \nRx: {}".format(0, 0))
        self.graphWidget.addItem(self.curve)
        self.curve.scene().sigMouseMoved.connect(self.onMouseMoved)
    def onMouseMoved(self, point):
        p = self.graphWidget.plotItem.vb.mapSceneToView(point)
        self.curve.setHtml(
            "<p style='color:yellow'>Tx: {:.1f}°C <br> Rx: {:.0f}Ω</p>".\
            format(p.x(), p.y()))


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.move(650,100)
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
