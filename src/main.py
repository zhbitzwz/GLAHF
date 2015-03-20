import FileDialog
import sys
import util
from PyQt4.Qt import *

util.init_config()

from PyQt4 import QtCore, QtGui

import container

class Ui(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(Ui, self).__init__(parent)
		self.ui = container.Ui_MainWindow()
		self.setMouseTracking(True)
		self.ui.setupUi(self)
		self.showMax()

	def mouseDoubleClickEvent(self, e):
		self.showMax()
		self.emit(SIGNAL("showMax()"))

	@pyqtSlot()	
	def showMax(self):
		if not self.isMaximized():
			self.showMaximized()
		else:
			self.showNormal()

util.update_db()
app = QtGui.QApplication(sys.argv)
window = Ui()
window.show()
sys.exit(app.exec_())
