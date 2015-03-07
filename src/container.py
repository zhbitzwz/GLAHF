# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from common import *
import cv2
import json
import lookdb
import analyse
import configdialog
import faceutil
import enlarge

PATH = './'
with open('settings.json') as jsonfile:
    PATH = json.load(jsonfile)['savedir']


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

LEFTPATH = None
FRONTALPATH = None
RIGHTPATH = None

LEFTIMG = None
FRONTALIMG = None
RIGHTIMG = None

LSCALE = None
FSCALE = None
RSCALE = None

class Ui_MainWindow(QtGui.QWidget):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1350, 700)
        self.linesArr = None

        png=QtGui.QPixmap(self)
        png.load("./sys/img/mbg.png")
        palette1 = QtGui.QPalette(self)
        palette1.setBrush(self.backgroundRole(), QtGui.QBrush(png))
        MainWindow.setPalette(palette1);
        MainWindow.setAutoFillBackground(True)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.analyseButton = QtGui.QPushButton(self.centralwidget)
        self.analyseButton.setEnabled(True)
        self.analyseButton.setGeometry(QtCore.QRect(70, 460, 210, 120))
        self.analyseButton.setObjectName(_fromUtf8("analyseButton"))
        self.dbButton = QtGui.QPushButton(self.centralwidget)
        self.dbButton.setEnabled(True)
        self.dbButton.setGeometry(QtCore.QRect(380, 460, 210, 120))
        self.dbButton.setObjectName(_fromUtf8("dbButton"))
        self.settingButton = QtGui.QPushButton(self.centralwidget)
        self.settingButton.setEnabled(True)
        self.settingButton.setGeometry(QtCore.QRect(710, 460, 210, 120))
        self.settingButton.setObjectName(_fromUtf8("settingButton"))
        self.exitButton = QtGui.QPushButton(self.centralwidget)
        self.exitButton.setEnabled(True)
        self.exitButton.setGeometry(QtCore.QRect(1020, 460, 210, 120))
        self.exitButton.setObjectName(_fromUtf8("exitButton"))
        self.leftLabel = QtGui.QLabel(self.centralwidget)
        self.leftLabel.setScaledContents(True)
        self.leftLabel.setGeometry(QtCore.QRect(80, 30, 250, 300))
        self.leftLabel.setObjectName(_fromUtf8("leftLabel"))
        self.frontalLabel = QtGui.QLabel(self.centralwidget)
        self.frontalLabel.setGeometry(QtCore.QRect(530, 30, 250, 300))
        self.frontalLabel.setObjectName(_fromUtf8("frontalLabel"))
        self.frontalLabel.setScaledContents(True)
        self.rightLabel = QtGui.QLabel(self.centralwidget)
        self.rightLabel.setGeometry(QtCore.QRect(980, 30, 250, 300))
        self.rightLabel.setObjectName(_fromUtf8("rightLabel"))
        self.rightLabel.setScaledContents(True)
        self.dectected_label =QtGui.QLabel(self.centralwidget)
        self.dectected_label.setGeometry(QtCore.QRect(730, 340, 40, 55))
        
        self.chooseLeftFace = QtGui.QPushButton(self.centralwidget)
        self.chooseLeftFace.setGeometry(QtCore.QRect(150, 350, 75, 23))
        self.chooseLeftFace.setObjectName(_fromUtf8("chooseLeftFace"))
        self.chooseFrontalFace = QtGui.QPushButton(self.centralwidget)
        self.chooseFrontalFace.setGeometry(QtCore.QRect(610, 350, 75, 23))
        self.chooseFrontalFace.setObjectName(_fromUtf8("chooseFrontalFace"))
        self.chooseRightFace = QtGui.QPushButton(self.centralwidget)
        self.chooseRightFace.setGeometry(QtCore.QRect(1080, 350, 75, 23))
        self.chooseRightFace.setObjectName(_fromUtf8("chooseRightFace"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1350, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.leftScale = QtGui.QSlider(MainWindow)
        self.leftScale.setGeometry(QtCore.QRect(100, 400, 160, 19))
        self.leftScale.setOrientation(QtCore.Qt.Horizontal)
        self.leftScale.setObjectName(_fromUtf8("leftScale"))
        self.leftScale.setRange(0, 3)
        self.leftScaleLabel = QtGui.QLabel(MainWindow)
        self.leftScaleLabel.setGeometry(QtCore.QRect(10, 400, 91, 16))
        self.leftScaleLabel.setObjectName(_fromUtf8("leftScaleLabel"))
        self.rightScale = QtGui.QSlider(MainWindow)
        self.rightScale.setRange(0, 3)
        self.rightScale.setGeometry(QtCore.QRect(1080, 400, 160, 19))
        self.rightScale.setOrientation(QtCore.Qt.Horizontal)
        self.rightScale.setObjectName(_fromUtf8("rightScale"))
        self.rightScaleLabel = QtGui.QLabel(MainWindow)
        self.rightScaleLabel.setGeometry(QtCore.QRect(990, 400, 91, 16))
        self.rightScaleLabel.setObjectName(_fromUtf8("rightScaleLabel"))
        self.leftlcdNum = QtGui.QLCDNumber(MainWindow)
        self.leftlcdNum.setGeometry(QtCore.QRect(270, 395, 64, 23))
        self.leftlcdNum.setObjectName(_fromUtf8("leftlcdNum"))
        self.rightlcdNum = QtGui.QLCDNumber(MainWindow)
        self.rightlcdNum.setGeometry(QtCore.QRect(1250, 395, 64, 23))
        self.rightlcdNum.setObjectName(_fromUtf8("rightlcdNum"))

        self.frontalScale = QtGui.QSlider(MainWindow)
        self.frontalScale.setGeometry(QtCore.QRect(590, 400, 160, 19))
        self.frontalScale.setOrientation(QtCore.Qt.Horizontal)
        self.frontalScale.setObjectName(_fromUtf8("leftScale"))
        self.frontalScale.setRange(0, 3)
        self.frontalScaleLabel = QtGui.QLabel(MainWindow)
        self.frontalScaleLabel.setGeometry(QtCore.QRect(500, 400, 91, 16))
        self.frontalScaleLabel.setObjectName(_fromUtf8("rightScaleLabel"))
        self.frontallcdNum = QtGui.QLCDNumber(MainWindow)
        self.frontallcdNum.setGeometry(QtCore.QRect(760, 395, 64, 23))
        self.frontallcdNum.setObjectName(_fromUtf8("rightlcdNum"))
        
        self.leftlcdNum.display(1.0)
        self.frontallcdNum.display(1.0)
        self.rightlcdNum.display(1.0)
        self.settingsdialog = configdialog.Ui_Dialog()
        self.dbdialog = lookdb.Ui_Table()
        self.connect(self.leftScale, QtCore.SIGNAL("valueChanged(int)"),self.leftSliderChange)
        self.connect(self.frontalScale, QtCore.SIGNAL("valueChanged(int)"),self.frontalSliderChange)
        self.connect(self.rightScale, QtCore.SIGNAL("valueChanged(int)"),self.rightSliderChange)
        self.connect(self.analyseButton,QtCore.SIGNAL('clicked()'),self.beginAnalyse)
        self.connect(self.dbButton,QtCore.SIGNAL('clicked()'),self.dbdialog.show)
        self.connect(self.settingButton,QtCore.SIGNAL('clicked()'),self.settingsdialog.show)
        self.connect(self.exitButton,QtCore.SIGNAL('clicked()'),QtGui.qApp,QtCore.SLOT('quit()'))
        self.connect(self.chooseLeftFace,QtCore.SIGNAL('clicked()'),self.getleft)
        self.connect(self.chooseFrontalFace,QtCore.SIGNAL('clicked()'),self.getfrontal)
        self.connect(self.chooseRightFace,QtCore.SIGNAL('clicked()'),self.getright)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "人脸灰度值定位", None))
        self.analyseButton.setText(_translate("MainWindow", "灰度值分析", None))
        self.dbButton.setText(_translate("MainWindow", "数据库", None))
        self.settingButton.setText(_translate("MainWindow", "设置", None))
        self.exitButton.setText(_translate("MainWindow", "退出", None))
        self.leftLabel.setText(_translate("MainWindow", "左脸", None))
        self.frontalLabel.setText(_translate("MainWindow", "正脸", None))
        self.rightLabel.setText(_translate("MainWindow", "右脸", None))
        self.chooseLeftFace.setText(_translate("MainWindow", "选择左脸", None))
        self.chooseFrontalFace.setText(_translate("MainWindow", "选择正脸", None))
        self.chooseRightFace.setText(_translate("MainWindow", "选择右脸", None))
        self.leftScaleLabel.setText(_translate("Dialog", "左脸缩放比例", None))
        self.rightScaleLabel.setText(_translate("Dialog", "右脸缩放比例", None))
        self.frontalScaleLabel.setText(_translate("Dialog", "正脸缩放比例", None))

        BtnStyle = "QPushButton{border-radius:5px;background:rgb(110, 190, 10);color:white}"\
            "QPushButton:hover{background:rgb(140, 220, 35)}"
        pixmap = QtGui.QPixmap("./sys/img/power.png")
        self.chooseLeftFace.setIcon(QtGui.QIcon(pixmap))
        self.chooseLeftFace.setIconSize(pixmap.size())
        self.chooseLeftFace.setFixedSize(100, 35)
        self.chooseLeftFace.setStyleSheet(BtnStyle)

        self.chooseFrontalFace.setIcon(QtGui.QIcon(pixmap))
        self.chooseFrontalFace.setIconSize(pixmap.size())
        self.chooseFrontalFace.setFixedSize(100, 35)
        self.chooseFrontalFace.setStyleSheet(BtnStyle)
        
        self.chooseRightFace.setIcon(QtGui.QIcon(pixmap))
        self.chooseRightFace.setIconSize(pixmap.size())
        self.chooseRightFace.setFixedSize(100, 35)
        self.chooseRightFace.setStyleSheet(BtnStyle)

        BtnStyle = "QPushButton{border:1px solid lightgray;background:rgb(230,230,230)}"\
            "QPushButton:hover{border-color:green;background:transparent}"
        self.analyseButton.setStyleSheet(BtnStyle)
        self.dbButton.setStyleSheet(BtnStyle)
        self.settingButton.setStyleSheet(BtnStyle)
        self.exitButton.setStyleSheet(BtnStyle)
        for idx in [self.analyseButton,self.dbButton,
                            self.settingButton,self.exitButton]:
            shadow = QtGui.QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(15)
            shadow.setOffset(2,2)
            idx.setGraphicsEffect(shadow)

        self.leftLabel.setPixmap(QtGui.QPixmap(INIT_LEFTIMG))
        self.frontalLabel.setPixmap(QtGui.QPixmap(INIT_FRONTALIMG))
        self.rightLabel.setPixmap(QtGui.QPixmap(INIT_RIGHTIMG))

    def leftSliderChange(self):
        global LSCALE
        value = self.leftScale.value()
        value = float(value)/10
        LSCALE = value/2
        self.leftlcdNum.display(value+1)
        LEFTTEMP = enlarge.enlargeimage(LEFTPATH,LSCALE,True)
        cv2.imwrite(LEFTTEMPPATH,LEFTTEMP)
        self.leftLabel.setPixmap(QtGui.QPixmap(LEFTTEMPPATH))

    def frontalSliderChange(self):
        global FSCALE
        value = self.frontalScale.value()
        value = float(value)/10
        FSCALE = value/2
        self.frontallcdNum.display(value+1)
        FRONTALTEMP = enlarge.enlargeimage(FACEAJUSTPATH,FSCALE,True)
        self.linesArr,counts = faceutil.markdetect(FRONTALTEMP)
        self.display_dectected_result(counts)
        cv2.imwrite(FRONTALTEMPPATH,FRONTALTEMP)
        self.frontalLabel.setPixmap(QtGui.QPixmap(FRONTALTEMPPATH))

    def rightSliderChange(self):
        global RSCALE
        value = self.rightScale.value()
        value = float(value)/10
        RSCALE = value/2
        self.rightlcdNum.display(value+1)
        RIGHTTEMP = enlarge.enlargeimage(RIGHTPATH,RSCALE,True)
        cv2.imwrite(RIGHTTEMPPATH,RIGHTTEMP)
        self.rightLabel.setPixmap(QtGui.QPixmap(RIGHTTEMPPATH))

    def getleft(self):
        global LEFTPATH
        global LEFTIMG
        LEFTPATH = unicode(self.showFileDialog())
        if LEFTPATH != "":
            LEFTPATH = LEFTPATH.encode('gbk')
            IMG = cv2.imread(LEFTPATH,0)
            cv2.imwrite(LEFTAJUSTPATH,IMG)
            LEFTIMG = QtGui.QPixmap(r''+LEFTAJUSTPATH)
            self.leftLabel.setPixmap(LEFTIMG)

    def getfrontal(self):
        global FRONTALPATH
        global FRONTALIMG
        FRONTALPATH = unicode(self.showFileDialog())
        if FRONTALPATH != "":
            FRONTALPATH = FRONTALPATH.encode('gbk')
            IMG = faceutil.adjustface(FRONTALPATH)
            self.linesArr,counts = faceutil.markdetect(IMG)
            self.display_dectected_result(counts)
            cv2.imwrite(FACEAJUSTPATH,IMG)
            FRONTALIMG = QtGui.QPixmap(r''+FACEAJUSTPATH)
            global FSCALE
            if FSCALE is not None and FSCALE >0:
                self.frontalSliderChange()
            else:
                self.frontalLabel.setPixmap(FRONTALIMG)

    def getright(self):
        global RIGHTPATH
        global RIGHTIMG
        RIGHTPATH = unicode(self.showFileDialog())
        if RIGHTPATH != "":
            RIGHTPATH = RIGHTPATH.encode('gbk')
            IMG = cv2.imread(RIGHTPATH,0)
            cv2.imwrite(RIGHTAJUSTPATH,IMG)
            RIGHTIMG = QtGui.QPixmap(r''+RIGHTAJUSTPATH)
            self.rightLabel.setPixmap(RIGHTIMG)

    def display_dectected_result(self, d):
        self.dectected_label.setText(_translate("MainWindow", \
                    "眼睛:%s\n鼻子:%s \n嘴:%s\n" %(d.get("eyes_count"), \
                                        d.get("noses_count"),d.get("mouths_count")),None))

    def showFileDialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,u'打开图片','./')
        return filename

    def beginAnalyse(self):
        d = faceutil.mergeImages(LEFTPATH,FRONTALPATH,RIGHTPATH,PATH,
                                    dict(LSCALE=LSCALE,FSCALE=FSCALE,RSCALE=RSCALE))

        if d is False:
            return
        else:
            arr = []
            try:
                import cPickle as pickle
            except ImportError:
                import pickle
            with open('db.pkl','rb') as pkl:
                try:
                    arr = pickle.load(pkl)
                except:
                    pass
            arr.append(d)
            with open('db.pkl','wb') as pkl:
                pickle.dump(arr,pkl)
            id = int(d.get('id'))-1
            self.dbdialog.insertRow(id)
            self.dbdialog.setRowData(id, d.get('date'), d.get('path'), str(d.get('units')))
        self.analysewindow = analyse.Ui_MainWindow(None,None,self.linesArr)
        self.analysewindow.show()
        self.analysewindow.setPreview(d.get('path'))

