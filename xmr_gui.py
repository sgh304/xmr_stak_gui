import subprocess
import time
import json
import re
import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QPushButton, QApplication, QLabel, QLineEdit, QTextEdit, QGridLayout
from PyQt5.QtCore import QCoreApplication, QTimer, QEvent

#Back-end
def create_config(pool_address, wallet_address, pool_password):
	config_file = open('config.txt', 'w')
	config_file.write(
		'"pool_list" : [' \
			'{{"pool_address" : "{}",' \
			'"wallet_address" : "{}",' \
			'"pool_password" : "{}",' \
			'"use_nicehash" : false,' \
			'"use_tls" : false,' \
			'"tls_fingerprint" : "",' \
			'"pool_weight" : 1 }}' \
		'],' \
		'"currency" : "monero",' \
		'"call_timeout" : 10,' \
		'"retry_time" : 30,' \
		'"giveup_limit" : 0,' \
		'"verbose_level" : 4,' \
		'"print_motd" : true,' \
		'"h_print_time" : 60,' \
		'"aes_override" : null,' \
		'"use_slow_memory" : "warn",' \
		'"tls_secure_algo" : true,' \
		'"daemon_mode" : false,' \
		'"flush_stdout" : true,' \
		'"output_file" : "xmr_output",' \
		'"httpd_port" : 0,' \
		'"http_login" : "",' \
		'"http_pass" : "",' \
		'"prefer_ipv4" : true' \
		''.format(pool_address, wallet_address, pool_password))
	config_file.write('')
	config_file.close()

def start_miner():
	p = subprocess.Popen('xmr-stak.exe')

def get_stats():
	output_file = open('xmr_output', 'r')
	hashrate_report_exp = re.compile('HASHRATE REPORT - CPU[\s\S]*?Highest:    [0-9]*.[0-9] H/s')
	hashrate_report_matches = hashrate_report_exp.findall(output_file.read())
	if not hashrate_report_matches:
		return 0
	newest_stats = hashrate_report_matches[-1]
	totals_exp = re.compile('Totals:     [0-9]*.[0-9]')
	raw_totals_string = totals_exp.search(newest_stats).group(0)
	ten_sec_total = raw_totals_string.replace('Totals:     ', '')
	return ten_sec_total

#Front-end
class XMRGUIWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('XmrGui v0.1')
		self.setGeometry(300, 300, 300, 100)
		self.init_widgets()
		self.set_to_config()
		self.show()

	def init_widgets(self):
		self.config_widget = ConfigWidget(self)
		self.display_widget = DisplayWidget(self)

	def set_to_config(self):
		#Set central widget to config
		self.setCentralWidget(self.config_widget)
		self.config_widget.show()
		self.display_widget.hide()

	def set_to_display(self):
		#Set to central widget to display
		self.setCentralWidget(self.display_widget)
		self.display_widget.show()
		self.config_widget.hide()
		#Start update loop
		self.timer = QTimer()
		self.timer.timeout.connect(self.display_widget.update)
		self.timer.start(60000)

class ConfigWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		#Labels
		self.pool_address_label = QLabel('Pool Address:')
		self.wallet_address_label = QLabel('Wallet Address:')
		self.pool_password_label = QLabel('Pool Password')
		#Line edits
		self.pool_address_edit = QLineEdit()
		self.wallet_address_edit = QLineEdit()
		self.pool_password_edit = QLineEdit()
		#Check for existing config
		try:
			existing_config_file = open('config.txt', 'r')
			existing_config = json.loads('{' + existing_config_file.read() + '}')
			existing_pool_address = existing_config['pool_list'][0]['pool_address']
			existing_wallet_address = existing_config['pool_list'][0]['wallet_address']
			existing_pool_password = existing_config['pool_list'][0]['pool_password']
			self.pool_address_edit.setText(existing_pool_address)
			self.wallet_address_edit.setText(existing_wallet_address)
			self.pool_password_edit.setText(existing_pool_password)
		except FileNotFoundError:
			pass
		#Start button
		self.start_button = QPushButton('Start Miner', self)
		self.start_button.clicked.connect(self.start_miner)
		#Grid setup
		grid = QGridLayout()
		grid.setSpacing(10)
		#Add widgets to grid
		grid.addWidget(self.pool_address_label, 1, 0)
		grid.addWidget(self.pool_address_edit, 1, 1)
		grid.addWidget(self.wallet_address_label, 2, 0)
		grid.addWidget(self.wallet_address_edit, 2, 1)
		grid.addWidget(self.pool_password_label, 3, 0)
		grid.addWidget(self.pool_password_edit, 3, 1)
		grid.addWidget(self.start_button, 5, 0, 1, 2)
		#Set layout
		self.setLayout(grid)

	def start_miner(self):
		#Get config
		pool_address = self.pool_address_edit.displayText()
		wallet_address = self.wallet_address_edit.displayText()
		pool_password = self.pool_password_edit.displayText()
		#Write config
		create_config(pool_address, wallet_address, pool_password)
		#Open miner process
		p = subprocess.Popen('xmr-stak.exe')
		#Display widget
		self.parent().set_to_display()

class DisplayWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		#Variables
		self.total = 0
		#Labels
		self.total_label = QLabel('Total: Calculating...')
		#Grid setup
		grid = QGridLayout()
		grid.setSpacing(10)
		#Add widgets to grid
		grid.addWidget(self.total_label, 1, 0)
		self.setLayout(grid)

	def update(self):
		#Variables
		self.total = get_stats()
		#Labels
		self.total_label.setText('Total: {}'.format(self.total))

app = QApplication(sys.argv)
ex = XMRGUIWindow()
sys.exit(app.exec_())