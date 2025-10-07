import socket
from enum import Enum
from ..UTILS.config import config_instance as config
from ..API.OBDManager import OBDManager
import threading

class Request(Enum):
    HEALTHCHECK = "healthcheck"
    READ_INFO = "read_info"

class BluetoothServer:

	def __init__(self):
		self.server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
		
		# Get configuration values
		mac_address = config.get_bluetooth_mac_address()
		channel = config.get_bluetooth_channel()
		
		self.server.bind((mac_address, channel))  # MAC Address and Channel from config
		self.server.listen(1)

		self.client = None
		self.addr = None
		self.thread = threading.Thread(target=self.wait_for_connection)
		self.thread.daemon = True  # Ensures the thread exits when the main program exits
		self.thread.start()


	def wait_for_connection(self):
		print("Waiting for bluetooth connection...")
		self.client, self.addr = self.server.accept()
		print(f"Accepted connection from {self.addr}")
		self.handle_connection()


	def generate_response(self, request: str) -> str:
		msg = "No answer matched"
		print(f"DEBUG: Comparing request '{request}' (length: {len(request)})")
		print(f"DEBUG: HEALTHCHECK value: '{Request.HEALTHCHECK.value}' (length: {len(Request.HEALTHCHECK.value)})")
		print(f"DEBUG: READ_INFO value: '{Request.READ_INFO.value}' (length: {len(Request.READ_INFO.value)})")
		print(f"DEBUG: request == HEALTHCHECK: {request == Request.HEALTHCHECK.value}")
		print(f"DEBUG: request == READ_info: {request == Request.READ_INFO.value}")
		fetcher = OBDManager()
		res = fetcher.get_speed()
		print(f"{res}")
		if request == Request.HEALTHCHECK.value:
			msg = f"{{'status': '1', 'message': '{res}' }}"
		elif request == Request.READ_INFO.value:
			msg = "{'status': '1', 'message': 'Info was requested'}"
		
		return msg

	def handle_connection(self):
		print("Handling connection...")
		buffer_size = config.get_buffer_size()
		try:
			while True:
				data = self.client.recv(buffer_size)
				if not data:
					break

				request = data.decode('utf-8').strip()
				print(f"Received request : {request}")

				answer = self.generate_response(request) 

				self.client.send(answer.encode('utf-8'))
				print(f"Sending answer : {answer}")
		except OSError:
			pass

		print("Disconnected")
		pass
	

	def close_connection(self):
		if self.client:
			self.client.close()
		self.server.close()
		print("Bluetooth server closed.")
