import json
import psutil
import re
import subprocess
import sys
import time
from PyQt5.QtWidgets import QWidget, QMainWindow, QPushButton, QApplication, QLabel, QLineEdit, QTextEdit, QGridLayout, QInputDialog, QComboBox, QCompleter, QAction
from PyQt5.QtCore import QTimer

class XMRStakGUIWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle('XMR-Stak GUI v0.2')
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
			('"pool_list" : [{{"pool_address" : "{}", "wallet_address" : "{}", "pool_password" : "{}",'
			'"use_nicehash" : false, "use_tls" : false, "tls_fingerprint" : "", "pool_weight" : 1 }}],'
			'"currency" : "monero", "call_timeout" : 10, "retry_time" : 30, "giveup_limit" : 0, "verbose_level" : 4,'
			'"print_motd" : true, "h_print_time" : 60, "aes_override" : null, "use_slow_memory" : "warn",'
			'"tls_secure_algo" : true, "daemon_mode" : false, "flush_stdout" : true, "output_file" : "xmr_output",'
			'"httpd_port" : 0, "http_login" : "", "http_pass" : "", "prefer_ipv4" : true,'
			''.format(self.pool_address, self.wallet_address, self.pool_password)))
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
		self.init_labels()
		self.init_inputs()
		self.init_menubar()
		self.init_start_button()

	def init_labels(self):
		self.pool_address_label = QLabel('Pool Address:')
		self.wallet_address_label = QLabel('Wallet Address:')

	def init_inputs(self):
		#Pool address
		pool_addresses = ['', 'pool.minexmr.com:4444', 'fr.minexmr.com:4444', 'de.minexmr.com:4444', 'ca.minexmr.com:4444']
		self.pool_address_edit = QComboBox()
		for pool_address in pool_addresses:
			self.pool_address_edit.addItem(pool_address)
		self.pool_address_edit.setCompleter(QCompleter(pool_addresses))
		self.pool_address_edit.setEditable(True)
		#Wallet address
		self.wallet_address_edit = QLineEdit()

	def init_menubar(self):
		self.menu_bar = self.parent().menuBar()
		self.options_menu = self.menu_bar.addMenu('Options')
		#Pool password
		self.pool_password = ''
		self.pool_password_action = QAction('Set Pool Password')
		def pool_password_prompt():
			self.pool_password = QInputDialog.getText(self, 'Input Dialog', 'Enter pool password:')[0]
		self.pool_password_action.triggered.connect(pool_password_prompt)
		self.options_menu.addAction(self.pool_password_action)

	def init_start_button(self):
		self.start_button = QPushButton('Start Miner', self)
		self.start_button.clicked.connect(lambda: self.parent().start_miner(*self.get_current_config()))

	def init_grid(self):
		grid = QGridLayout()
		grid.setSpacing(10)

		grid.addWidget(self.pool_address_label, 1, 0)
		grid.addWidget(self.pool_address_edit, 1, 1)
		grid.addWidget(self.wallet_address_label, 2, 0)
		grid.addWidget(self.wallet_address_edit, 2, 1)
		grid.addWidget(self.start_button, 3, 0, 1, 2)

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
		except FileNotFoundError:
			pass

	def get_current_config(self):
		self.pool_address = self.pool_address_edit.currentText()
		self.wallet_address = self.wallet_address_edit.displayText()
		return (self.pool_address, self.wallet_address, self.pool_password)

class DisplayWidget(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		#Miner
		self.miner = self.parent().miner
		#Labels
		self.pool_address_label = QLabel('Pool address: {}'.format(self.miner.pool_address))
		self.wallet_address_label = QLabel('Wallet address: ...{}'.format(self.miner.wallet_address[-34:]))
		self.hashrate_label = QLabel('Hashrate: Calculating...')
		self.cpu_usage_label = QLabel('CPU Usage: Calculating...')
		#Grid setup
		grid = QGridLayout()
		grid.setSpacing(10)
		#Add widgets to grid
		grid.addWidget(self.hashrate_label, 0, 0)
		grid.addWidget(self.cpu_usage_label, 0, 1)
		grid.addWidget(self.wallet_address_label, 1, 0, 1, 2)
		grid.addWidget(self.pool_address_label, 2, 0)
		self.setLayout(grid)
		#Start timer
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(6000)

	def update(self):
		self.update_hashrate()
		self.update_cpu_usage()

	def update_hashrate(self):
		hashrate_reports = re.findall('HASHRATE REPORT - CPU[\S\s]*?H/s', self.miner.output_file.read())
		if hashrate_reports:
			newest_stats = hashrate_reports[-1]
			hashrate = re.search('(Totals:     )([0-9]*.[0-9])', newest_stats).group(2)
			self.hashrate_label.setText('Hashrate: {} H/s'.format(hashrate))

	def update_cpu_usage(self):
		cpu_usage = self.miner.child_process.cpu_percent() / psutil.cpu_count()
		if cpu_usage == 0.0:
			cpu_usage = 'Calculating...'
		else:
			cpu_usage = '{:.2f}%'.format(cpu_usage)
		self.cpu_usage_label.setText('CPU Usage: {}'.format(cpu_usage))

app = QApplication(sys.argv)
ex = XMRStakGUIWindow()
sys.exit(app.exec_())