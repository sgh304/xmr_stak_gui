import sys
from PyQt5.QtWidgets import QApplication
from xmr_stak_gui.config_widget import ConfigWidget
from xmr_stak_gui.display_widget import DisplayWidget
from xmr_stak_gui.miner import Miner
from xmr_stak_gui.xmr_stak_gui_window import XMRStakGUIWindow

def run():
	app = QApplication(sys.argv)
	ex = XMRStakGUIWindow()
	sys.exit(app.exec_())