import psutil
import re
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt5.QtCore import QTimer

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