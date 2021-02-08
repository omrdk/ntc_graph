import os
import sys
import math
import numpy
from PyQt5 import QtWidgets, QtGui, uic, QtCore
from pyqtgraph import PlotWidget, plot
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QFileDialog
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi('mainwindow.ui', self)
        self.setWindowTitle("NTC Calculation")
        self.setFixedSize(640,200)

        self.reset()

        self.btn_rst.clicked.connect(self.reset)
        self.btn_plot.clicked.connect(self.plot)
        self.btn_const.clicked.connect(self.savefile)

        # First values
    def reset(self):
        self.line_Vref.setText("1.16")
        self.line_Rntc.setText("10000")
        self.line_Rv.setText("2000")
        self.line_Bn.setText("3950")
        self.line_Rp.setText("0")
        self.line_adc.setText("15")
        self.line_ix.setText("1024")
        # NTC table
    def const(self):
        global strx
        strx = ''
        global Rx_list
        Rx_str_convert = [str(x) for x in Rx_list]                              # int list to str list
        cnt = 1
        col = 16
        for i in Rx_str_convert:
            s = i.rjust(len(Rx_str_convert[len(Rx_str_convert)-2]),' ') + ', '  # number of digits of the last resistor value in ntc_list
            if cnt % col == 0:
                s = s + '\n'
            strx = strx + s
            cnt = cnt + 1
        strx = "const I16 NTC_Table[" + str(len(Rx_list)) + "] = {\n" + strx + "};"
        #Rx_str ="const I16 NTC_Table["+ str(len(Rx_list)) +"] = " + "{\n " + ", ".join(repr(e) for e in Rx_align) + " } "

    def savefile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save file", "","Text Files (*.txt);;All Files (*)", options=options) #(*.mp3 *.ogg *.wav *.m4a)
        if fileName:
            print(fileName)
        self.const()
        global strx
        ntc_table_txt = open(fileName,'w')
        ntc_table_txt.write(strx)
        ntc_table_txt.close()

    def plot(self): # btn_plot a bsıldığında Graph class'ını görüntüler. (YENI PENCERE)
        # Get values from line edit
        Vref = float(self.line_Vref.text())
        Rntc = int(self.line_Rntc.text())
        Rv   = int(self.line_Rv.text())
        Bn   = int(self.line_Bn.text())
        Rp   = int(self.line_Rp.text())
        Adc  = int(self.line_adc.text())
        ix   = int(self.line_ix.text())
        Tn = 1./298.
        # max. LSB value and step
        Adc = 2**Adc

        ix_list = [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
        if (ix in ix_list):
            step = Adc / ix
        # Fill step_list (0 to max LSB)
        LSB_step = 0                                                            # index (ix) - başlangıç değeri 0
        step_list = []                                                          # step list 1024 adet (ix adım aralığı ile max LSB değerine kadar)
        for i in range(0,ix,1):
            step_list.append(LSB_step)
            LSB_step = int(LSB_step + step)
        global Rx_list
        global Tx_list
        Rx_list = []
        Tx_list = []
        for i in range(0,ix,1):
            if i == 0:                                                          # log0 tanımsız olduğu için 0'ı eledik
                Rx = 0
                Rx_list.append(Rx)
                Tx = 500            # 0 yapınca grafikte de 0 a düşüyor.
                Tx_list.append(Tx)
            else:
                Rx = (Rv*step_list[i])/(Adc-step_list[i])
                Rx_Round = round(Rx)
                Rx_list.append(Rx_Round)
                Tx = 1.0/(((math.log(Rx)-math.log(Rntc)))/Bn+Tn)-273            # log değeri 0 veya daha az old için geçersiz oluyor
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

        styles = {'color':'#fff', 'font-size':'20px'}                           # Axis labels 8bit rgb
        self.graphWidget.setLabel('left', 'Resistance c', **styles)
        self.graphWidget.setLabel('bottom', 'Temperature (°C)', **styles)

        self.graphWidget.showGrid(x=True, y=True)
        #self.graphWidget.setXRange(-100, 500, padding=0)                       # set axis limit, first min, second max
        #self.graphWidget.setYRange(-0, 100000, padding=0)
        self.graphWidget.setLimits(xMin=-60, xMax=100, yMin=-150000, yMax=1000000)

        pen = pg.mkPen(color=(255, 255, 255), width=1, style=QtCore.Qt.SolidLine)   # plot line with dashes anad configure width
        self.graphWidget.plot(Tx_list, Rx_list, pen=pen)                            # plot data: x, y values

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
