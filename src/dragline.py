from PyQt4 import QtGui
from PyQt4 import QtCore

class DragLine(QtGui.QLabel):
    def __init__(self, title, parent, TYPE='V'):
        super(DragLine, self).__init__(title, parent)
        self.TYPE = TYPE
        self._xpos = self._ypos = 0
        self._info = None

    @property
    def info(self):
        return self._info
    @info.setter
    def info(self, value):
        self._info = value

    @property
    def xpos(self):
        return self._xpos
    @xpos.setter
    def xpos(self, value):
        self._xpos = value

    @property
    def ypos(self):
        return self._ypos
    @ypos.setter
    def ypos(self, value):
        self._ypos = value

    def mouseMoveEvent(self, e):
        if e.buttons() != QtCore.Qt.LeftButton:
            return
        mimeData = QtCore.QMimeData()
        pixmap = QtGui.QPixmap.grabWidget(self)

        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        dropAction = drag.start(QtCore.Qt.MoveAction)

    def mousePressEvent(self, e):
        if e.buttons() == QtCore.Qt.RightButton:
            self.close()

    def mouseReleaseEvent(self, e):
        pass

    def __str__(self):
        return self.info

    __repr__ = __str__