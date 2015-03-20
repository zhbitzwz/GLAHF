# -*- coding: utf-8 -*-

from common import *
from PyQt4 import QtCore, QtGui
import analyse
import configdialog
import cv2
import enlarge
import faceutil
import json
import lookdb
import threading
import time
import util

SAVEPATH = './'
with open('settings.json') as jsonfile:
    SAVEPATH = json.load(jsonfile)['savedir']

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

FACEPATH = None
FACEIMG = None

class Ui_MainWindow(QtGui.QWidget):
    slideSig = QtCore.pyqtSignal(str)
    statusSig = QtCore.pyqtSignal(bool)

    def __init__(self
                    ,parent=None):
        super(Ui_MainWindow,self).__init__(parent)
        self.slideSig.connect(self.setImg)
        self.statusSig.connect(self.display_dectected_result)
        self.filename = ""
        self.has_img = False
        self.ready = False
        self.linesArr = None
        self.FSCALE = None
        self.success_png = QtGui.QPixmap(SUCCESS_STATUS_IMG)
        self.fail_png = QtGui.QPixmap(FAIL_STATUS_IMG)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        screen = QtGui.QDesktopWidget().screenGeometry()
        GLOBAL_WIDTH = screen.width()
        GLOBAL_HEIGHT = screen.height()
        self.resize(GLOBAL_WIDTH, GLOBAL_HEIGHT)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei"))

        self.movie = QtGui.QMovie(LOADING_GIF, QtCore.QByteArray(), self)
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.dbdialog = lookdb.Ui_Table()
        self.settingsdialog = configdialog.Ui_Dialog()

        png = QtGui.QPixmap(self)
        png.load(BG_IMG)
        palette = QtGui.QPalette(self)
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(png))
        MainWindow.setPalette(palette);
        MainWindow.setAutoFillBackground(True)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        font.setPointSize(12)
        # 灰度值分析按钮
        self.analyseButton = QtGui.QPushButton(self.centralwidget)
        self.analyseButton.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.1, GLOBAL_HEIGHT*0.6, 210, 120))
        self.analyseButton.setObjectName(_fromUtf8("analyseButton"))
        self.analyseButton.setFont(font)
        # 数据库按钮
        self.dbButton = QtGui.QPushButton(self.centralwidget)
        self.dbButton.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.3, GLOBAL_HEIGHT*0.6, 210, 120))
        self.dbButton.setObjectName(_fromUtf8("dbButton"))
        self.dbButton.setFont(font)
        # 设置按钮
        self.settingButton = QtGui.QPushButton(self.centralwidget)
        self.settingButton.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.5, GLOBAL_HEIGHT*0.6, 210, 120))
        self.settingButton.setObjectName(_fromUtf8("settingButton"))
        self.settingButton.setFont(font)
        # 退出按钮
        self.exitButton = QtGui.QPushButton(self.centralwidget)
        self.exitButton.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.7, GLOBAL_HEIGHT*0.6, 210, 120))
        self.exitButton.setObjectName(_fromUtf8("exitButton"))
        self.exitButton.setFont(font)
        # 预览框
        self.faceLabel = QtGui.QLabel(self.centralwidget)
        self.faceLabel.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.12, GLOBAL_HEIGHT*0.05, 400, 360))
        self.faceLabel.setObjectName(_fromUtf8("faceLabel"))
        self.faceLabel.setScaledContents(True)
        # 识别状态
        self.dectected_png =QtGui.QLabel(self.centralwidget)
        self.dectected_png.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.6, GLOBAL_HEIGHT*0.35, 120, 120))
        self.dectected_label =QtGui.QLabel(self.centralwidget)
        self.dectected_label.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.63, GLOBAL_HEIGHT*0.5, 80, 40))
        # 选择图片按钮
        self.chooseFace = QtGui.QPushButton(self.centralwidget)
        self.chooseFace.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.6, GLOBAL_HEIGHT*0.08, 280, 100))
        self.chooseFace.setObjectName(_fromUtf8("chooseFace"))
        font.setPointSize(18)
        self.chooseFace.setFont(font)

        MainWindow.setCentralWidget(self.centralwidget)
        # 缩放滑动条
        self.scaleSliderLabel = QtGui.QLabel(MainWindow)
        self.scaleSliderLabel.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.6, GLOBAL_HEIGHT*0.3, 60, 16))
        self.scaleSliderLabel.setObjectName(_fromUtf8("rightScaleLabel"))
        self.scaleSlider = QtGui.QSlider(MainWindow)
        self.scaleSlider.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.6+70, GLOBAL_HEIGHT*0.29, 160, 40))
        self.scaleSlider.setOrientation(QtCore.Qt.Horizontal)
        self.scaleSlider.setObjectName(_fromUtf8("leftScale"))
        self.scaleSlider.setRange(0, 3)
        font.setPointSize(10)
        self.scaleSliderLabel.setFont(font)
        self.scaleLcd = QtGui.QLCDNumber(MainWindow)
        self.scaleLcd.setGeometry(QtCore.QRect(GLOBAL_WIDTH*0.6+250, GLOBAL_HEIGHT*0.3, 64, 23))
        self.scaleLcd.setObjectName(_fromUtf8("rightlcdNum"))
        self.scaleLcd.display(1.0)

        self.connect(self.scaleSlider, QtCore.SIGNAL("valueChanged(int)"),self.SliderChange)
        self.connect(self.analyseButton,QtCore.SIGNAL('clicked()'),self.beginAnalyse)
        self.connect(self.dbButton,QtCore.SIGNAL('clicked()'),self.dbdialog.show)
        self.connect(self.settingButton,QtCore.SIGNAL('clicked()'),self.settingsdialog.show)
        self.connect(self.exitButton,QtCore.SIGNAL('clicked()'),QtGui.qApp,QtCore.SLOT('quit()'))
        self.connect(self.chooseFace,QtCore.SIGNAL('clicked()'),self.getface)
        self.lock = threading.Lock()
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "人脸灰度值定位", None))
        self.analyseButton.setText(_translate("MainWindow", "灰度值分析", None))
        self.dbButton.setText(_translate("MainWindow", "数据库", None))
        self.settingButton.setText(_translate("MainWindow", "设置", None))
        self.exitButton.setText(_translate("MainWindow", "退出", None))
        self.faceLabel.setText(_translate("MainWindow", "正脸", None))
        self.chooseFace.setText(_translate("MainWindow", "选择正脸", None))
        self.scaleSliderLabel.setText(_translate("Dialog", "缩放比例", None))

        BtnStyle = "QPushButton{border-radius:5px;background:rgb(110, 190, 10);color:white}"\
            "QPushButton:hover{background:rgb(140, 220, 35)}"
        pixmap = QtGui.QPixmap("./sys/img/power.png")
        self.chooseFace.setIcon(QtGui.QIcon(pixmap))
        self.chooseFace.setIconSize(pixmap.size())
        self.chooseFace.setFixedSize(280, 100)
        self.chooseFace.setStyleSheet(BtnStyle)

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

        self.faceLabel.setPixmap(QtGui.QPixmap(INIT_FACEIMG))

    def loading(self):
        self.faceLabel.setMovie(self.movie)
        self.movie.start()

    def SliderChange(self):
        self.ready = False
        FACETEMP = None
        value = self.scaleSlider.value()
        value = float(value)/10
        self.FSCALE = value/2
        self.scaleLcd.display(value+1)
        if self.has_img == False:
            return
        FACETEMP = enlarge.enlargeimage(FACE_ADJ_PATH,self.FSCALE,True)
        
        def deal_job():
            self.lock.acquire()
            try:
                self.linesArr,status = faceutil.markdetect(FACETEMP)
                cv2.imwrite(FACE_TEMP_PATH,FACETEMP)
                self.statusSig.emit(status)
                self.slideSig.emit(FACE_TEMP_PATH)
            finally:
                self.ready = True
                self.lock.release()
        self.loading()
        threading.Thread(target=deal_job).start()

    def setImg(self, path):
        self.faceLabel.setPixmap(QtGui.QPixmap(path))

    def getface(self):
        global FACEPATH
        global FACEIMG
        FACEPATH = unicode(self.showFileDialog())
        if FACEPATH != "":
            self.has_img = True
            FACEPATH = FACEPATH.encode('gbk')
            IMG = faceutil.adjustface(FACEPATH)
            self.linesArr,status = faceutil.markdetect(IMG)
            if status == False:
                self.linesArr = util.get_memory()
            self.display_dectected_result(status)
            cv2.imwrite(FACE_ADJ_PATH,IMG)
            FACEIMG = QtGui.QPixmap(r''+FACE_ADJ_PATH)
            self.ready = True
            if self.FSCALE is not None and self.FSCALE >0:
                self.SliderChange()
            else:
                self.faceLabel.setPixmap(FACEIMG)

    def display_dectected_result(self, status):
        if status is True:
            self.display_status(True, "识别成功")
        else:
            self.display_status(False, "识别失败")

    def display_status(self, status, word):
        if status is True:
            self.dectected_png.setPixmap(self.success_png)
        else:
            self.dectected_png.setPixmap(self.fail_png)
        self.dectected_label.setText(_translate("MainWindow",word,None))


    def showFileDialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,u'打开图片','./')
        if len(filename) != 0:
            self.filename = filename
            return filename
        return self.filename

    def beginAnalyse(self):
        if self.ready is False:
            self.display_status(False, "请选择图片")
        d = faceutil.dealImages(FACEPATH,SAVEPATH,
                                    dict(FSCALE=self.FSCALE))

        if d is False:
            return
        else:
            d['linesArr'] = self.linesArr
            util.insert_to_db(d)
            id = int(d.get('id'))-1
            self.dbdialog.insertRow(id)
            self.dbdialog.setRowData(id, d.get('date'), d.get('path'), d.get('units'), d.get('linesArr'))
        self.analysewindow = analyse.Ui_MainWindow(linesArr=self.linesArr)
        self.analysewindow.show()
        self.analysewindow.setPreview(d.get('path'))

