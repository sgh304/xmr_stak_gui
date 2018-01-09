import psutil
import subprocess
import time

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
		self.output_file = open('xmr_output', 'w+')
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