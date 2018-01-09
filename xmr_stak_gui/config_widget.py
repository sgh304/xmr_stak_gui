import json
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QInputDialog, QComboBox, QCompleter, QAction

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
			self.pool_password = QInputDialog.getText(self, 'Pool Password', 'Enter pool password:')[0]
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