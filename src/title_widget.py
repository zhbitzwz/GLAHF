#!/usr/bin/python  
#-*-coding:utf-8-*-
			
from push_button import PushButton

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *

class TitleWidget(QWidget):
	def __init__(self, parent=None):
		super(TitleWidget, self).__init__(parent)
		
		self.min_button = PushButton(self)
		self.max_button = PushButton(self)
		self.close_button = PushButton(self)
		self.button_list = []
	
		self.min_button.loadPixmap("./sys/img/min_button.png")
		self.max_button.loadPixmap("./sys/img/max_button.png")
		self.close_button.loadPixmap("./sys/img/close_button.png")

		title_layout = QHBoxLayout()
		title_layout.addStretch()
		title_layout.addWidget(self.min_button, 0, Qt.AlignTop)
		title_layout.addWidget(self.max_button, 0, Qt.AlignTop)
		title_layout.addWidget(self.close_button, 0, Qt.AlignTop)
		title_layout.setSpacing(0)
		title_layout.setContentsMargins(0, 0, 15, 0)

		button_layout = QHBoxLayout()
		signal_mapper = QSignalMapper(self)
		
		self.connect(signal_mapper, SIGNAL("mapped()"), self, SLOT("turnPage()"))
	
		button_layout.addStretch()
		button_layout.setSpacing(8)
		button_layout.setContentsMargins(15, 0, 0, 0)
	
		main_layout = QVBoxLayout()
		main_layout.addLayout(title_layout)
		main_layout.addLayout(button_layout)
		main_layout.setSpacing(0)
		main_layout.setContentsMargins(0, 0, 0, 0)
	
		self.translateLanguage()

		self.setLayout(main_layout)
		self.setFixedHeight(100)

	def translateLanguage(self):
		self.min_button.setToolTip(u"minimize")
		self.max_button.setToolTip(u"maximize")
		self.close_button.setToolTip(u"close")

	@pyqtSlot()
	def turnPage(self, current_page):	
		current_index = current_page
		for i in range(len(self.button_list)):
			self.tool_button = self.button_list[i]
			if(current_index == i):
				self.tool_button.setMousePress(True)			
			else:
				self.tool_button.setMousePress(False)
		


