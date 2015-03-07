# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from push_button import PushButton
import json

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

class Ui_Dialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(Ui_Dialog, self).__init__(parent)
        self.config = {}
        with open('settings.json') as jsonfile:
            self.config = json.load(jsonfile)
        self.setupUi(self)
        self.retranslateUi(self)
        self.mouse_press = False
        self.is_change = False
    
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
    
        self.initTitle()

    def initTitle(self):
    
        self.title_label =  QLabel(self)
        self.title_icon_label =  QLabel(self)
        self.close_button =  PushButton(self)
    
        self.close_button.loadPixmap("./sys/img/close_button.png")
        self.title_label.setFixedHeight(30)
    
        self.title_layout =  QHBoxLayout()
        self.title_layout.addWidget(self.title_icon_label, 0, Qt.AlignVCenter)
        self.title_layout.addWidget(self.title_label, 0, Qt.AlignVCenter)
        self.title_layout.addStretch()
        self.title_layout.addWidget(self.close_button, 0, Qt.AlignTop)
        self.title_layout.setSpacing(5)
        self.title_layout.setContentsMargins(10, 0, 5, 0)
        self.initTitle
    
        self.title_label.setStyleSheet("color:white")
        self.connect(self.close_button, SIGNAL("clicked()"), SLOT("close()"))
        
    def paintEvent(self,event):
    
        if(~self.is_change):
            pass

        self.skin_name = QString("./sys/img/mbg.png")
        painter = QPainter (self)
        painter.drawPixmap(self.rect(), QPixmap(self.skin_name))
    
        painter2 = QPainter (self)
        linear2 = QLinearGradient(QPointF(self.rect().topLeft()), QPointF(self.rect().bottomLeft()))
        linear2.setColorAt(0, Qt.white)
        linear2.setColorAt(0.5, Qt.white)
        linear2.setColorAt(1, Qt.white)
        painter2.setPen(Qt.white) #设定画笔颜色，到时侯就是边框颜色
        painter2.setBrush(linear2)
        painter2.drawRect(QRect(0, 30, self.width(), self.height()-30))
    
        painter3 = QPainter (self)
        painter3.setPen(Qt.gray)
        painter3.drawPolyline(QPointF(0, 30), QPointF(0, self.height()-1), QPointF(self.width()-1, self.height()-1), QPointF(self.width()-1, 30))

    def mousePressEvent(self,event ):
        if(event.button() == Qt.LeftButton): 
            self.mouse_press = True
        
        self.move_point = event.globalPos() - self.pos() 
    
    
    def mouseReleaseEvent(self,event):
        self.mouse_press = False
    
    
    def mouseMoveEvent(self,event):
    
        if(self.mouse_press):   
            self.move_pos = event.globalPos()
            self.move(self.move_pos - self.move_point)   

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.saveDirLabel = QtGui.QLabel(Dialog)
        self.saveDirLabel.setGeometry(QtCore.QRect(10, 40, 71, 16))
        self.saveDirLabel.setObjectName(_fromUtf8("saveDirLabel"))
        self.hposCountLabel = QtGui.QLabel(Dialog)
        self.hposCountLabel.setGeometry(QtCore.QRect(10, 70, 91, 16))
        self.hposCountLabel.setObjectName(_fromUtf8("hposCountLabel"))
        self.vposCountLabel = QtGui.QLabel(Dialog)
        self.vposCountLabel.setGeometry(QtCore.QRect(10, 100, 91, 16))
        self.vposCountLabel.setObjectName(_fromUtf8("vposCountLabel"))
        self.clearVoice = QtGui.QCheckBox(Dialog)
        self.clearVoice.setGeometry(QtCore.QRect(10, 130, 71, 16))
        self.clearVoice.setObjectName(_fromUtf8("clearVoice"))
        self.lockEyes = QtGui.QCheckBox(Dialog)
        self.lockEyes.setGeometry(QtCore.QRect(10, 160, 71, 16))
        self.lockEyes.setObjectName(_fromUtf8("lockEyes"))

        self.hposCount = QtGui.QSlider(Dialog)
        self.hposCount.setGeometry(QtCore.QRect(90, 70, 250, 20))
        self.hposCount.setOrientation(QtCore.Qt.Horizontal)
        self.hposCount.setObjectName(_fromUtf8("hposCount"))
        self.hposCount.setRange(2, 50)

        self.vposCount = QtGui.QSlider(Dialog)
        self.vposCount.setGeometry(QtCore.QRect(90, 100, 250, 20))
        self.vposCount.setOrientation(QtCore.Qt.Horizontal)
        self.vposCount.setObjectName(_fromUtf8("hposCount"))
        self.vposCount.setRange(2, 50)

        self.hposCountLcd = QtGui.QLineEdit(Dialog)
        self.hposCountLcd.setGeometry(QtCore.QRect(350, 70, 40, 20))
        self.vposCountLcd = QtGui.QLineEdit(Dialog)
        self.vposCountLcd.setGeometry(QtCore.QRect(350, 100, 40, 20))

        self.saveDir = QtGui.QLineEdit(Dialog)
        self.saveDir.setGeometry(QtCore.QRect(90, 40, 221, 20))
        self.saveDir.setObjectName(_fromUtf8("saveDir"))
        self.chooseSaveDir = QtGui.QPushButton(Dialog)
        self.chooseSaveDir.setGeometry(QtCore.QRect(320, 40, 75, 23))
        self.chooseSaveDir.setObjectName(_fromUtf8("chooseSaveDir"))

        self.retranslateUi(Dialog)
        self.connect(self.hposCount, QtCore.SIGNAL("valueChanged(int)"),self.hposCountChange)
        self.connect(self.vposCount, QtCore.SIGNAL("valueChanged(int)"),self.vposCountChange)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.connect(self.chooseSaveDir,QtCore.SIGNAL("clicked()"),self.chooseDir)
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.ok)
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"),self.cancel)

        self.flashValue()

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "设置", None))
        self.saveDirLabel.setText(_translate("Dialog", "图片存放路径", None))
        self.hposCountLabel.setText(_translate("Dialog", "水平坐标数量", None))
        self.vposCountLabel.setText(_translate("Dialog", "垂直坐标数量", None))
        self.clearVoice.setText(_translate("Dialog", "背景去噪", None))
        self.lockEyes.setText(_translate("Dialog", "瞳孔锁定", None))
        self.chooseSaveDir.setText(_translate("Dialog", "选择路径", None))

    def ok(self):
        hpcount = unicode(self.hposCount.value())
        vpcount = unicode(self.vposCount.value())
        if hpcount.isdigit():
            self.config['hposcount'] = hpcount
        if vpcount.isdigit():
            self.config['vposcount'] = vpcount
        self.config['denoise'] = self.clearVoice.isChecked()
        self.config['lockeyes'] = self.lockEyes.isChecked()
        self.config['savedir'] = str(self.saveDir.text())
        with open('settings.json','w') as settings:
            json.dump(self.config, settings)
        with open('settings.json') as jsonfile:
            self.config = json.load(jsonfile)

    def cancel(self):
        self.flashValue()

    def chooseDir(self):
        dirname = unicode(self.showFileDialog())
        self.saveDir.setText(dirname)

    def showFileDialog(self):
        savedir = QtGui.QFileDialog.getExistingDirectory(self,u'选择图片保存目录','./')
        return savedir

    def hposCountChange(self):
    	value = self.hposCount.value()
    	self.hposCountLcd.setText(str(value))

    def vposCountChange(self):
    	value = self.vposCount.value()
    	self.vposCountLcd.setText(str(value))

    def flashValue(self):
        self.saveDir.setText(self.config['savedir'])
        self.hposCount.setValue(int(self.config['hposcount']))
        self.vposCount.setValue(int(self.config['vposcount']))
        self.clearVoice.setChecked(self.config['denoise'])
        self.lockEyes.setChecked(self.config['lockeyes'])
