import bluetooth
import threading
import time

class BluetoothServer:

	def __init__(self):
		self.server_sock = None
		self.client_sock = None
		self.is_connected = False
		self.is_running = False
		self.thread = None

	def run(self):
		"""Start the Bluetooth server in a separate thread"""
		if self.is_running:
			print("Bluetooth server is already running")
			return
		
		self.thread = threading.Thread(target=self._start_server, daemon=True)
		self.thread.start()

	def _start_server(self):
		"""Internal method to start the Bluetooth server"""
		try:
			print("Creating Bluetooth socket...")
			self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

			print("Binding to Bluetooth port...")
			# Bind to any available Bluetooth adapter, and port 1 (commonly used)
			self.server_sock.bind(("", bluetooth.PORT_ANY))
			self.server_sock.listen(1)

			port = self.server_sock.getsockname()[1]
			print(f"Successfully bound to port {port}")

			print("Advertising Bluetooth service...")
			# Make the service discoverable
			try:
				# Fix: Remove the profiles parameter that's causing the KeyError
				bluetooth.advertise_service(
					self.server_sock,
					"OBD-Data-Server",
					service_classes=[bluetooth.SERIAL_PORT_CLASS]
				)
				print("Service advertisement successful")
			except Exception as adv_error:
				print(f"Service advertisement failed: {adv_error}")
				print("Trying minimal advertisement method...")
				try:
					# Alternative: minimal advertisement
					bluetooth.advertise_service(
						self.server_sock,
						"OBD-Data-Server"
					)
					print("Minimal service advertisement successful")
				except Exception as alt_error:
					print(f"All advertisement methods failed: {alt_error}")
					print("Continuing without service advertisement...")
					# We can continue without advertising - clients can still connect if they know the address

			print(f"Waiting for connection on RFCOMM channel {port}...")
			self.is_running = True

			self.client_sock, client_info = self.server_sock.accept()
			print(f"Accepted connection from {client_info}")
			self.is_connected = True

		except KeyError as e:
			print(f"Bluetooth KeyError: {e}")
			print("This might be due to missing Bluetooth service constants")
			print("Available constants in bluetooth module:")
			try:
				print(f"SERIAL_PORT_CLASS: {getattr(bluetooth, 'SERIAL_PORT_CLASS', 'NOT FOUND')}")
				print(f"SERIAL_PORT_PROFILE: {getattr(bluetooth, 'SERIAL_PORT_PROFILE', 'NOT FOUND')}")
			except:
				pass
			self.is_running = False
		except Exception as e:
			import errno
			print(f"Bluetooth server error: {e}")
			print(f"Error type: {type(e)}")
			if hasattr(e, 'errno'):
				print(f"Error number: {e.errno}")
				print(f"Error description: {errno.errorcode.get(e.errno, 'Unknown')}")
			self.is_running = False
		
	def send_data(self, data):
		"""Send data to connected client"""
		if self.is_connected and self.client_sock:
			try:
				message = str(data) + "\n"
				self.client_sock.send(message.encode())
				return True
			except Exception as e:
				print(f"Error sending data: {e}")
				self.is_connected = False
				return False
		return False

	def close_connection(self):
		"""Close the Bluetooth connection"""
		self.is_running = False
		self.is_connected = False
		
		if self.client_sock:
			try:
				self.client_sock.close()
			except:
				pass
		
		if self.server_sock:
			try:
				self.server_sock.close()
			except:
				pass
		
		print("Bluetooth connection closed")