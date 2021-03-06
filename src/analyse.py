# -*- coding: utf-8 -*-

from dragline import *
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
import faceutil
import json
import threading
import util

DICT = {chr(i-1+ord('A')):i for i in xrange(1,27)}

def create_arr():
    arr = [chr(i-1+ord('A')) for i in xrange(1,27)]
    for i in xrange(1,27):
        char = chr(i-1+ord('A'))
        for j in xrange(1,27):
            arr.append(char+chr(j-1+ord('A')))
    return arr

ARR = create_arr()

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

class Ui_MainWindow(QtGui.QMainWindow):
    FOCUS = "start"
    gafSig = QtCore.pyqtSignal(str)
    
    def __init__(self
            ,parent=None, units=None, linesArr=None):
        super(Ui_MainWindow, self).__init__(parent)
        
        Ui_MainWindow.FOCUS = "start"
        self.imgpath = None
        self.spliced_img = None
        self.threshold = None
        self.vis = None
        self.__linesArr = linesArr
        self.__vDraglines = []
        self.__hDraglines = []
        self.units = units
        self.gafSig.connect(self.display_gaf)
        self.setupUi(self)
        self.retranslateUi(self)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        screen = QtGui.QDesktopWidget().screenGeometry()
        GLOBAL_WIDTH = screen.width()
        GLOBAL_HEIGHT = screen.height()
        self.resize(GLOBAL_WIDTH, GLOBAL_HEIGHT)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Microsoft YaHei"))
        self.setStyleSheet("QLineEdit{margin-left:20%;margin-right:30%;height:50%;font-size:18px;}")

        self.PREIVIEW_H = GLOBAL_HEIGHT*0.55
        self.PREIVIEW_W = GLOBAL_WIDTH*0.8
        self.PREIVIEW_TOTOP = 20
        self.PREIVIEW_TOLEFT = GLOBAL_WIDTH*0.1

        if self.units is None:
            with open('settings.json') as jsonfile:
                config = json.load(jsonfile)
            V = int(config["vposcount"])
            H = int(config["hposcount"])
        else:
            H = int(self.units[0])
            V = int(self.units[1])

        global ARR
        voffset = float(self.PREIVIEW_H)/V
        hoffset = float(self.PREIVIEW_W)/H
        for i in xrange(1,V+1):
            label = QtGui.QLabel(self.centralwidget)
            label.setGeometry(QtCore.QRect(self.PREIVIEW_TOLEFT-25, 12+i*voffset, 15, 10))
            label.setText(str(i))
        else:
            self.X_VAXIS = str(i)

        for i in xrange(0,H+1):
            label = QtGui.QLabel(self.centralwidget)
            label.setGeometry(QtCore.QRect(self.PREIVIEW_TOLEFT+i*hoffset, 0, 12, 15))
            label.setText(str(ARR[i]))
        else:
            self.X_HAXIS = str(ARR[i])

        QLE_BGSTYLE = "QLineEdit{background: %s;}"
        # 自动输入
        def AutoSetText(hpos,vpos):
            global ARR
            _self = self
            pos = vpos+ARR[int(hpos)]
            if Ui_MainWindow.FOCUS is not None:
                _self.setCursor(Qt.CrossCursor)
                color = 'red'
                if Ui_MainWindow.FOCUS == 'start':
                    _self.startpointInput.setText(pos)
                    _self.startpointInput.setStyleSheet(QLE_BGSTYLE %color)
                else:
                    _self.endpointInput.setText(pos)
                    _self.endpointInput.setStyleSheet(QLE_BGSTYLE %color)
                    
        def AutoSetBack():
            _self = self
            if Ui_MainWindow.FOCUS is not None:
                _self.setCursor(Qt.ArrowCursor)
                color = 'white'
                if Ui_MainWindow.FOCUS == 'start':
                    _self.startpointInput.setStyleSheet(QLE_BGSTYLE %color)
                else:
                    _self.endpointInput.setStyleSheet(QLE_BGSTYLE %color)

        class PreviewLabel(QtGui.QLabel):
            def __init(self, parent):
                QtGui.QLabel.__init__(self, parent)
                self.hpos = None
                self.vpos = None

            def mousePressEvent(self, ev):
                x = ev.x()
                y = ev.y()
                hpos = int(round(x/float(hoffset)))
                vpos = int(round(y/float(voffset)))
                AutoSetText(str(hpos),str(vpos))

            def mouseReleaseEvent(self, ev):
                AutoSetBack()

            def getpos(self):
            	return (self.hpos, self.vpos)

        class InputEdit(QtGui.QLineEdit):
            def __init(self, parent):
                QtGui.QLineEdit.__init__(self,parent)

            @property
            def key(self):
                return self._key
            @key.setter
            def key(self, value):
                self._key = value

            def mousePressEvent(self, ev):
                Ui_MainWindow.FOCUS = self._key

        # 底部布局
        self.bottomLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.bottomLayoutWidget.setGeometry(QtCore.QRect(0, GLOBAL_HEIGHT*0.6, GLOBAL_WIDTH-10, GLOBAL_HEIGHT*0.3))
        self.bottomLayoutWidget.setObjectName(_fromUtf8("bottomLayoutWidget"))
        self.bottomLayout = QtGui.QHBoxLayout(self.bottomLayoutWidget)
        self.bottomLayout.setObjectName(_fromUtf8("bottomLayout"))

        # 预览标签
        self.label = PreviewLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(self.PREIVIEW_TOLEFT, self.PREIVIEW_TOTOP
                                        ,self.PREIVIEW_W, self.PREIVIEW_H))
        self.label.setScaledContents(True)
        self.label.setObjectName(_fromUtf8("label"))

        # 自动获取标签
        self.autogetLabel = QtGui.QLabel(self.centralwidget)
        font.setPointSize(18)
        self.autogetLabel.setFont(font)

        self.area_12af_Label = QtGui.QLabel(self.centralwidget)
        self.area_12af_Color = QtGui.QLabel(self.centralwidget)

        self.area_34ef_Label = QtGui.QLabel(self.centralwidget)
        self.area_34ef_Color = QtGui.QLabel(self.centralwidget)

        self.area_45bc_Label = QtGui.QLabel(self.centralwidget)
        self.area_45bc_Color = QtGui.QLabel(self.centralwidget)

        self.area_45de_Label = QtGui.QLabel(self.centralwidget)
        self.area_45de_Color = QtGui.QLabel(self.centralwidget)

        self.area_45ef_Label = QtGui.QLabel(self.centralwidget)
        self.area_45ef_Color = QtGui.QLabel(self.centralwidget)

        self.area_56ef_Label = QtGui.QLabel(self.centralwidget)
        self.area_56ef_Color = QtGui.QLabel(self.centralwidget)

        self.area_all_Label = QtGui.QLabel(self.centralwidget)
        self.area_all_Color = QtGui.QLabel(self.centralwidget)

        # 框线
        frameStyle = "border:1px solid lightgray;border-radius:5px;opacity:0.5;"
        self.frameLabel1 = QtGui.QWidget(self.centralwidget)
        self.frameLabel1.setStyleSheet(frameStyle)
        self.frameLabel2 = QtGui.QWidget(self.centralwidget)
        self.frameLabel2.setStyleSheet(frameStyle)
        self.frameLabel3 = QtGui.QWidget(self.centralwidget)
        self.frameLabel3.setStyleSheet(frameStyle)

        self.autoLayout = QtGui.QGridLayout()
        self.autoLayout.setObjectName(_fromUtf8("autoLayout"))
        self.autoLayout.addWidget(self.frameLabel1, 0, 0, 11, 3)
        self.autoLayout.addWidget(self.autogetLabel, 1, 0, 2, 1)

        self.autogetLabel.setMargin(5)
        self.area_12af_Label.setMargin(5)
        self.area_34ef_Label.setMargin(5)
        self.area_45bc_Label.setMargin(5)
        self.area_45de_Label.setMargin(5)
        self.area_45ef_Label.setMargin(5)
        self.area_56ef_Label.setMargin(5)
        self.autoLayout.addWidget(self.area_12af_Label, 3, 0)
        self.autoLayout.addWidget(self.area_12af_Color, 3, 1)
        self.autoLayout.addWidget(self.area_34ef_Label, 4, 0)
        self.autoLayout.addWidget(self.area_34ef_Color, 4, 1)
        self.autoLayout.addWidget(self.area_45bc_Label, 5, 0)
        self.autoLayout.addWidget(self.area_45bc_Color, 5, 1)
        self.autoLayout.addWidget(self.area_45de_Label, 6, 0)
        self.autoLayout.addWidget(self.area_45de_Color, 6, 1)
        self.autoLayout.addWidget(self.area_45ef_Label, 7, 0)
        self.autoLayout.addWidget(self.area_45ef_Color, 7, 1)
        self.autoLayout.addWidget(self.area_56ef_Label, 8, 0)
        self.autoLayout.addWidget(self.area_56ef_Color, 8, 1)
        self.autoLayout.addWidget(self.area_all_Label, 9, 0)
        self.area_all_Label.setStyleSheet("margin-left:10px;")

        self.bottomLayout.addLayout(self.autoLayout)

        # 平均灰度值标签
        self.grayValueLabel = QtGui.QLabel(self.centralwidget)
        self.grayValueLabel.setGeometry(QtCore.QRect(1040, 480, 250, 61))
        font.setPointSize(25)
        self.grayValueLabel.setFont(font)
        self.grayValueLabel.setObjectName(_fromUtf8("grayValueLabel"))
        # 灰度值结果标签
        self.resultLabel = QtGui.QLabel(self.centralwidget)
        self.resultLabel.setGeometry(QtCore.QRect(1080, 550, 240, 80))
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.resultLabel.setFont(font)
        self.resultLabel.setText(_fromUtf8(""))
        self.resultLabel.setObjectName(_fromUtf8("resultLabel"))
        # 灰度结果
        self.area_sp_Color = QtGui.QLabel(self.centralwidget)

        # 坐标输入
        self.positionLabel = QtGui.QLabel(self.centralwidget)
        font.setPointSize(18)
        self.positionLabel.setFont(font)
        self.positionLabel.setObjectName(_fromUtf8("positionLabel"))

        # 开始坐标标签
        self.startpointLabel = QtGui.QLabel(self.centralwidget)
        font.setPointSize(12)
        self.startpointLabel.setFont(font)
        self.startpointLabel.setObjectName(_fromUtf8("startpointLabel"))
        # 结束坐标标签
        self.endpointLabel = QtGui.QLabel(self.centralwidget)
        self.endpointLabel.setFont(font)
        self.endpointLabel.setObjectName(_fromUtf8("endpointLabel"))
        # 开始坐标输入
        self.startpointInput = InputEdit(self.centralwidget)
        self.startpointInput.setObjectName(_fromUtf8("startpointInput"))
        self.startpointInput.key = "start"
        # 结束坐标输入
        self.endpointInput = InputEdit(self.centralwidget)
        self.endpointInput.setObjectName(_fromUtf8("endpointInput"))
        self.endpointInput.key = "end"

        # 提示标签
        self.tipLabel = QtGui.QLabel(self.centralwidget)
        self.tipLabel.setFont(font)
        self.tipLabel.setText(_fromUtf8(""))
        self.tipLabel.setObjectName(_fromUtf8("tipLabel"))
        
        # 确定输入按钮
        self.okButton = QtGui.QPushButton(self.centralwidget)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        font.setPointSize(10)
        self.okButton.setFont(font)

        self.inputLayout = QtGui.QGridLayout()
        self.inputLayout.setObjectName(_fromUtf8("inputLayout"))
        self.inputLayout.setSpacing(10)
        self.positionLabel.setMargin(10)
        self.startpointLabel.setMargin(10)
        self.endpointLabel.setMargin(10)
        self.inputLayout.addWidget(self.frameLabel2, 0, 0, 5, 3)
        self.inputLayout.addWidget(self.positionLabel, 0, 0, 2, 1)
        self.inputLayout.addWidget(self.tipLabel, 0, 1, 2, 1)
        self.inputLayout.addWidget(self.startpointLabel, 2, 0, 1, 1)
        self.inputLayout.addWidget(self.endpointLabel, 3, 0, 1, 1)
        self.inputLayout.addWidget(self.startpointInput, 2, 1, 1, 1)
        self.inputLayout.addWidget(self.endpointInput, 3, 1, 1, 1)
        self.inputLayout.addWidget(self.okButton, 4, 1, 1, 1)

        self.bottomLayout.addLayout(self.inputLayout)

        # 退出按钮
        self.exitButton = QtGui.QPushButton(self.centralwidget)
        font.setPointSize(12)
        self.exitButton.setFont(font)
        self.exitButton.setObjectName(_fromUtf8("exitButton"))
        # 分析按钮
        self.lookAnalyseButton = QtGui.QPushButton(self.centralwidget)
        
        self.rightLayout = QtGui.QGridLayout()
        self.rightLayout.setObjectName(_fromUtf8("rightLayout"))
        self.rightLayout.addWidget(self.frameLabel3, 0, 0, 4, 2)
        self.rightLayout.addWidget(self.lookAnalyseButton, 0, 0, 1, 1)
        self.rightLayout.addWidget(self.exitButton, 1, 0, 1, 1)

        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.addWidget(self.grayValueLabel)
        self.verticalLayout.addWidget(self.resultLabel)
        self.verticalLayout.addWidget(self.area_sp_Color)
        self.rightLayout.addLayout(self.verticalLayout, 0, 1, 2, 1)

        self.bottomLayout.addLayout(self.rightLayout)
        self.bottomLayout.setStretch(0,1)
        self.bottomLayout.setStretch(1,1)
        self.bottomLayout.setStretch(2,1)


        self.lookAnalyseButton.setFont(font)
        self.lookAnalyseButton.setObjectName(_fromUtf8("lookAnalyseButton"))
        MainWindow.setCentralWidget(self.centralwidget)

        self.connect(self.exitButton,QtCore.SIGNAL('clicked()'),self.returnTo)
        self.connect(self.okButton,QtCore.SIGNAL('clicked()'),self.getPosition)
        self.connect(self.lookAnalyseButton,QtCore.SIGNAL('clicked()'),self.getanalyse)
        self.setAcceptDrops(True)

        if self.__linesArr is not None and len(self.__linesArr) != 0:
            VLines = [i for i in self.__linesArr if i.get('y')==0]
            HLines = [i for i in self.__linesArr if i.get('x')==0]
            VLines = sorted(VLines,key=lambda item:item.get('x'))
            HLines = sorted(HLines,key=lambda item:item.get('y'))

            VKey = [str(i) for i in range(1,len(VLines)+1)]
            HKey = [chr(i-1+ord('a')) for i in range(1,len(HLines)+1)]

            self.LINE_WEIGHT = 5
            for line,key in zip(VLines,VKey):
                pos = line.get('x')*self.PREIVIEW_W + self.PREIVIEW_TOLEFT
                dragline = DragLine('', self, 'V')
                dragline.setText(key)
                dragline.info = key
                dragline.callback = self.__closeline_callback
                dragline.xpos = round((pos-self.PREIVIEW_TOLEFT+self.LINE_WEIGHT/2)/float(self.PREIVIEW_W),3)
                dragline.setGeometry(pos, self.PREIVIEW_TOTOP, self.LINE_WEIGHT, self.PREIVIEW_H)
                dragline.setStyleSheet("background-color:red;color:white;")
                self.__vDraglines.append(dragline)

            for line,key in zip(HLines,HKey):
                pos = line.get('y')*self.PREIVIEW_H + self.PREIVIEW_TOTOP
                dragline = DragLine('', self, 'H')
                dragline.setText(key)
                dragline.info = key
                dragline.callback = self.__closeline_callback
                dragline.ypos = round((pos-self.PREIVIEW_TOTOP+self.LINE_WEIGHT/2)/float(self.PREIVIEW_H),3)
                dragline.setGeometry(self.PREIVIEW_TOLEFT, pos, self.PREIVIEW_W, self.LINE_WEIGHT)
                dragline.setStyleSheet("background-color:red;color:white;")
                self.__hDraglines.append(dragline)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def __closeline_callback(self,key):
        def deal_with_line(linesArr):
            __finded = False
            __last_key = None
            __deleted_line = None
            for line in linesArr:
                if __finded is True:
                    line.info = __last_key
                    line.setText(__last_key)
                    __last_key = chr(ord(__last_key)+1)
                if line.info == key and __finded is False:
                    __finded = True
                    __last_key = key
                    __deleted_line = line
            else:
                if __deleted_line in linesArr:
                    linesArr.remove(__deleted_line)
                    return

        deal_with_line(self.__vDraglines)
        deal_with_line(self.__hDraglines)

    def display_gaf(self, text):
        self.area_all_Label.setText(_translate("MainWindow","平均灰度值:%s" %text, None))

    def get_all_face_graylv(self):
        if self.threshold is not None:
            graylv = faceutil.fave_avg_glv(self.imgpath)
            self.threshold = None
            self.gafSig.emit(str(graylv))

    def get_auto_results(self):
        # from left to right
        f = self.get_auto_grayvalue
        v_12af = f('1','2','a','f')
        pesudo = faceutil.grayToPseudo(int(v_12af))
        self.area_12af_Label.setText("12af:"+str(v_12af))
        self.area_12af_Color.setStyleSheet("background-color:rgb%s;" %str(pesudo))

        v_34ef = f('3','4','e','f')
        pesudo = faceutil.grayToPseudo(int(v_34ef))
        self.area_34ef_Label.setText("34ef:"+str(v_34ef))
        self.area_34ef_Color.setStyleSheet("background-color:rgb%s;" %str(pesudo))

        v_45bc = f('4','5','b','c')
        pesudo = faceutil.grayToPseudo(int(v_45bc))
        self.area_45bc_Label.setText("45bc:"+str(v_45bc))
        self.area_45bc_Color.setStyleSheet("background-color:rgb%s;" %str(pesudo))

        v_45de = f('4','5','d','e')
        pesudo = faceutil.grayToPseudo(int(v_45de))
        self.area_45de_Label.setText("45de:"+str(v_45de))
        self.area_45de_Color.setStyleSheet("background-color:rgb%s;" %str(pesudo))
        v_45ef = f('4','5','e','f')

        pesudo = faceutil.grayToPseudo(int(v_45ef))
        self.area_45ef_Label.setText("45ef:"+str(v_45ef))
        self.area_45ef_Color.setStyleSheet("background-color:rgb%s;" %str(pesudo))

        v_56ef = f('5','6','e','f')
        pesudo = faceutil.grayToPseudo(int(v_56ef))
        self.area_56ef_Label.setText("56ef:"+str(v_56ef))
        self.area_56ef_Color.setStyleSheet("background-color:rgb%s;" %str(pesudo))
        # threshold
        if self.threshold == None:
            self.threshold = (v_45ef+v_45de+v_56ef)/3

    def get_auto_grayvalue(self,l_line,r_line,up_line,dn_line):
        v_left = None
        v_right = None
        h_up = None
        h_down = None
        for line in self.__vDraglines:
            key = str(line)
            if key == l_line:
                v_left = line
            elif key == r_line:
                v_right = line
        for line in self.__hDraglines:
            key = str(line)
            if key == up_line:
                h_up = line
            elif key == dn_line:
                h_down = line
        if v_left and v_right and h_up and h_down:
            return self.get_sp_grayvalue(v_left,v_right,h_up,h_down)

    def get_sp_grayvalue(self,v_left,v_right,h_up,h_down):
        start_x = v_left.xpos
        end_x = v_right.xpos
        start_y = h_up.ypos
        end_y = h_down.ypos
        grayvalue = faceutil.roi_grayvalue(self.imgpath, start_x, end_x, start_y, end_y)
        return grayvalue

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        dragline = e.source()
        position = e.pos()
        if position.x() < self.PREIVIEW_TOLEFT:
            position.setX(self.PREIVIEW_TOLEFT)
        elif position.x() > self.PREIVIEW_W+self.PREIVIEW_TOLEFT:
            position.setX(self.PREIVIEW_W+self.PREIVIEW_TOLEFT)
        if position.y() < self.PREIVIEW_TOTOP:
            position.setY(self.PREIVIEW_TOTOP)
        elif position.y() > self.PREIVIEW_H+self.PREIVIEW_TOTOP:
            position.setY(self.PREIVIEW_H+self.PREIVIEW_TOTOP)
            
        if dragline.TYPE == 'V':
            position.setY(self.PREIVIEW_TOTOP)
            pos = (((2*position.x()+self.LINE_WEIGHT)/2)-self.PREIVIEW_TOLEFT)
            dragline.xpos = pos/float(self.PREIVIEW_W)
        elif dragline.TYPE == 'H':
            position.setX(self.PREIVIEW_TOLEFT)
            pos = (((2*position.y()+self.LINE_WEIGHT)/2)-self.PREIVIEW_TOTOP)
            dragline.ypos = pos/float(self.PREIVIEW_H)
        else:
            raise Exception
        dragline.move(position)
        self.get_auto_results()
        e.setDropAction(QtCore.Qt.MoveAction)
        e.accept()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "灰度值分析", None))
        self.label.setText(_translate("MainWindow", "", None))
        self.autogetLabel.setText(_translate("MainWindow", "自动获取", None))
        self.positionLabel.setText(_translate("MainWindow", "坐标输入", None))
        self.startpointLabel.setText(_translate("MainWindow", "开始坐标", None))
        self.endpointLabel.setText(_translate("MainWindow", "结束坐标", None))
        self.grayValueLabel.setText(_translate("MainWindow", "区域灰度值:", None))
        self.resultLabel.setText(_translate("MainWindow", "点确定以获取结果", None))
        self.exitButton.setText(_translate("MainWindow", "返回", None))
        self.lookAnalyseButton.setText(_translate("MainWindow", "查看分析", None))
        self.okButton.setText(_translate("MainWindow", "确定", None))
        self.tipLabel.setText(_translate("MainWindow", "", None))
        self.area_all_Label.setText(_translate("MainWindow", "灰度值计算中...", None))

        self.okButton.setStyleSheet("QPushButton{border:1px solid lightgray;height:100%;\
            margin-bottom:10px;background:rgb(230,230,230)}"\
            "QPushButton:hover{border-color:green;background:transparent}")
        self.exitButton.setStyleSheet("QPushButton{border-radius:5px;height:80%;margin:10px;\
            background:rgb(220, 20, 60);color:white}"\
            "QPushButton:hover{background:rgb(205, 92, 92)}")
        self.lookAnalyseButton.setStyleSheet("QPushButton{border-radius:5px;height:80%;\
            margin:10px;background:rgb(70,130,180);color:white}"\
            "QPushButton:hover{background:rgb(95, 158, 160)}")

    def setPreview(self,path):
        self.startpointInput.setPlaceholderText("0A")
        self.endpointInput.setPlaceholderText("3C")
        self.imgpath = path
        self.vis = QtGui.QPixmap(r''+path[:-4]+'_preview.jpg')
        self.label.setPixmap(self.vis)
        self.get_auto_results()
        t = threading.Thread(target=self.get_all_face_graylv)
        t.setDaemon(True)
        t.start()

    @staticmethod
    def dealWithInp(string):
        def gval(str):
            global DICT
            result = 0
            for idx,char in enumerate(str[::-1]):
                c = DICT.get(char)
                result += c*26*idx if idx!=0 else c
            return result

        for i in string:
            if i.isalpha():
                idx = string.index(i)
                b = int(string[0:idx])
                e = gval(string[idx:])-1
                return (str(e),str(b))
        return None

    def getPosition(self):
        config = {}
        lowbound = -1
        with open('settings.json') as jsonfile:
            config = json.load(jsonfile)
        starttext = unicode(self.startpointInput.text())
        endtext = unicode(self.endpointInput.text())
        if starttext=='':
            starttext = '0A'
        if endtext=='':
            endtext = '3C'

        import re
        regexp = '^[\d]{1,2}[\A-Z]{1,2}$'
        c = re.compile(regexp)
        if len(re.findall(c,starttext))==0 or len(re.findall(c,endtext))==0:
            tip = "输入格式有误,坐标格式:[纵坐标+横坐标(大写字母)],如5U,28AA"
            self.tipLabel.setText(_translate("MainWindow", tip, None))
            return

        startpoint = Ui_MainWindow.dealWithInp(starttext)
        endpoint = Ui_MainWindow.dealWithInp(endtext)

        if int(startpoint[0]) < int(endpoint[0]) <= int(config['hposcount']) and\
                                int(startpoint[1]) < int(endpoint[1]) <= int(config['vposcount']):
            pass
        else:
            tip = "请输入合理范围，横坐标(A~%s)，纵坐标(0~%s)" %(self.X_HAXIS,self.X_VAXIS)
            self.tipLabel.setText(_translate("MainWindow", tip, None))
            return

        if self.units is not None:
            self.spliced_img,value =\
                    faceutil.getavggrayvalue(self.imgpath,startpoint,endpoint,self.units)
        else:
            self.spliced_img,value =\
                    faceutil.getavggrayvalue(self.imgpath,startpoint,endpoint)

        self.resultLabel.setText(str(value))
        pesudo = faceutil.grayToPseudo(int(value))
        self.area_sp_Color.setStyleSheet("margin:20px 10px;background-color:rgb%s;" %str(pesudo))

        self.tipLabel.setText("")

    def getanalyse(self):
        if self.spliced_img is not None:
            faceutil.showplt(self.spliced_img)

    def returnTo(self):
        self.units = None
        self.close()

    @pyqtSlot() 
    def showMax(self):
        if not self.isMaximized():
            self.showMaximized()
        else:
            self.showNormal()