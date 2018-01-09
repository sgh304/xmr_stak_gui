from xmr_stak_gui import ConfigWidget
from xmr_stak_gui import DisplayWidget
from xmr_stak_gui import Miner
from PyQt5.QtWidgets import QMainWindow

class XMRStakGUIWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('XMR-Stak GUI v0.3')
		self.setGeometry(300, 300, 300, 100)
		self.set_central_config()
		self.show()

	# CENTRAL WIDGET SETTERS
	def set_central_config(self):
		self.setCentralWidget(ConfigWidget(self))

	def set_central_display(self):
		self.setCentralWidget(DisplayWidget(self))
		self.menuBar().clear()

	# MINER MANAGEMENT
	def start_miner(self, pool_address, wallet_address, pool_password):
		self.miner = Miner(pool_address, wallet_address, pool_password)
		self.miner.start()
		self.set_central_display()