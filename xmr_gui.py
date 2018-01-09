import json
import psutil
import re
import subprocess
import sys
import time
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QWidget, QMainWindow, QPushButton, QApplication, QLabel, QLineEdit, QTextEdit, QGridLayout, QInputDialog, QComboBox, QCompleter
from PyQt5.QtCore import QCoreApplication, QTimer, QEvent

class XMRGUIWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('XmrGui v0.1')
		self.setGeometry(300, 300, 300, 100)
		self.init_widgets()
		self.set_central_config()
		self.show()

	def init_widgets(self):
		self.config_widget = ConfigWidget(self)
		self.display_widget = DisplayWidget(self)

	# CENTRAL WIDGET SETTERS
	def set_central_config(self):
		#Set central widget to config
		self.setCentralWidget(self.config_widget)
		self.config_widget.show()
		self.display_widget.hide()

	def set_central_display(self):
		#Set to central widget to display
		self.setCentralWidget(self.display_widget)
		self.display_widget.show()
		self.config_widget.hide()
		#Start update loop
		self.timer = QTimer()
		self.timer.timeout.connect(self.display_widget.update)
		self.timer.start(6000)

	# MINER MANAGEMENT
	def start_miner(self, pool_address, wallet_address, pool_password):
		self.miner = Miner(pool_address, wallet_address, pool_password)
		self.miner.start()
		self.set_central_display()

class Miner():
	def __init__(self, pool_address, wallet_address, pool_password):
		self.pool_address = pool_address
		self.wallet_address = wallet_address
		self.pool_password = pool_password

		self.write_config()
		self.open_output()

	def write_config(self):
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
			'"prefer_ipv4" : true,' \
			''.format(self.pool_address, self.wallet_address, self.pool_password))
		config_file.write('')
		config_file.close()

	def open_output(self):
		self.output_file = open('xmr_output', 'r+')
		self.output_file.truncate()

	def start(self):
		popen_process = subprocess.Popen('xmr-stak.exe')
		self.wait_for_output()
		self.parent_process = psutil.Process(popen_process.pid)
		self.child_process = self.parent_process.children()[0]

	def wait_for_output(self):
		while True:
			time.sleep(1)
			if self.output_file.read():
				break

class ConfigWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.init_widgets()
		self.init_grid()
		self.check_for_existing_config()

	def init_widgets(self):	
		#Labels
		self.pool_address_label = QLabel('Pool Address:')
		self.wallet_address_label = QLabel('Wallet Address:')
		self.pool_password_label = QLabel('Pool Password')
		#Inputs
		#Pool address
		pool_addresses = ['', 'pool.minexmr.com:4444', 'fr.minexmr.com:4444', 'de.minexmr.com:4444', 'ca.minexmr.com:4444']
		self.pool_address_completer = QCompleter(pool_addresses)
		self.pool_address_edit = QComboBox()
		self.pool_address_edit.setCompleter(self.pool_address_completer)
		self.pool_address_edit.setEditable(True)
		for pool_address in pool_addresses:
			self.pool_address_edit.addItem(pool_address)
		#Wallet address
		self.wallet_address_edit = QLineEdit()
		#Pool password
		self.pool_password_edit = QLineEdit()
		#Start button
		self.start_button = QPushButton('Start Miner', self)
		self.start_button.clicked.connect(lambda: self.parent().start_miner(*self.get_current_config()))

	def init_grid(self):
		grid = QGridLayout()
		grid.setSpacing(10)

		grid.addWidget(self.pool_address_label, 1, 0)
		grid.addWidget(self.pool_address_edit, 1, 1)
		grid.addWidget(self.wallet_address_label, 2, 0)
		grid.addWidget(self.wallet_address_edit, 2, 1)
		grid.addWidget(self.pool_password_label, 3, 0)
		grid.addWidget(self.pool_password_edit, 3, 1)
		grid.addWidget(self.start_button, 5, 0, 1, 2)

		self.setLayout(grid)

	def check_for_existing_config(self):
		try:
			existing_config_file = open('config.txt', 'r')
			existing_config = json.loads('{' + existing_config_file.read()[:-1] + '}')

			existing_pool_address = existing_config['pool_list'][0]['pool_address']
			existing_wallet_address = existing_config['pool_list'][0]['wallet_address']
			existing_pool_password = existing_config['pool_list'][0]['pool_password']

			self.pool_address_edit.setCurrentText(existing_pool_address)
			self.wallet_address_edit.setText(existing_wallet_address)
			self.pool_password_edit.setText(existing_pool_password)
		except FileNotFoundError:
			pass

	def get_current_config(self):
		pool_address = self.pool_address_edit.currentText()
		wallet_address = self.wallet_address_edit.displayText()
		pool_password = self.pool_password_edit.displayText()
		return (pool_address, wallet_address, pool_password)

class DisplayWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		#Variables
		self.total = 0
		self.cpu_usage = 0
		#Labels
		self.total_label = QLabel('Total: Calculating...')
		self.cpu_usage_label = QLabel('CPU Usage: Calculating...')
		#Grid setup
		grid = QGridLayout()
		grid.setSpacing(10)
		#Add widgets to grid
		grid.addWidget(self.total_label, 0, 0)
		grid.addWidget(self.cpu_usage_label, 0, 1)
		self.setLayout(grid)

	def update(self):
		#Get variables
		self.total = self.get_hash_total()
		self.cpu_usage = self.get_cpu_usage()
		#Set labels
		self.total_label.setText('Total: {}'.format(self.total))
		self.cpu_usage_label.setText('CPU Usage: {}'.format(self.cpu_usage))

	def get_hash_total():
		output_file = open('xmr_output', 'r')
		hashrate_reports = re.findall('HASHRATE REPORT - CPU[\s\S]*?Highest:    [0-9]*.[0-9] H/s', output_file.read())
		if not hashrate_reports:
			return 'Calculating...'
		newest_stats = hashrate_reports[-1]
		ten_sec_total = re.search('(Totals:     )([0-9]*.[0-9])', newest_stats).group(2)
		return ten_sec_total

	def get_cpu_usage(self):
		xmr_processes = [process for process in psutil.process_iter()]
		print('parent', self.parent().parent_process.cpu_percent())
		print('child', self.parent().correct_process.cpu_percent() / psutil.cpu_count())

app = QApplication(sys.argv)
ex = XMRGUIWindow()
sys.exit(app.exec_())