import asyncio
from enum import Enum
from typing import Any, Union
import sys
from ..API.OBDManager import OBDManager 
from ..UTILS.logger import Logger
from ..UTILS.config import config_instance as config
import threading
from bless import (  # type: ignore
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

logger = Logger("Bluetooth Server")

# NOTE: Some systems require different synchronization methods.
trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    trigger = threading.Event()
else:
    trigger = asyncio.Event()


class Request(Enum):
    HEALTHCHECK = "healthcheck"
    READ_INFO = "read_info"

class BluetoothServer:

	def __init__(self):
		self.server_name = config.get_bluetooth_server_name()
		self.service_uuid = config.get_bluetooth_service_uuid()
		self.char_uuid = config.get_bluetooth_char_uuid()
		
		self.server = None
		self.running = False
		
		# Start daemon thread
		self.thread = threading.Thread(target=self._run_daemon)
		self.thread.daemon = True
		self.thread.start()

	def _run_daemon(self):
		"""Run the BLE server in daemon thread"""
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		
		try:
			loop.run_until_complete(self.run(loop))
		except Exception as e:
			logger.error(f"Daemon error: {e}")
		finally:
			loop.close()
	

	async def run(self, loop):
		# Instantiate the server
		self.server = BlessServer(name=self.server_name, loop=loop)
		self.server.read_request_func = self.read_request
		self.server.write_request_func = self.write_request
		logger.debug("✅ BLE Server instance created")
		
		# Add Service
		await self.server.add_new_service(self.service_uuid)
		logger.debug(f"✅ BLE Service added: {self.service_uuid}")
		

		# Add a Characteristic to the service
		char_flags = (
			GATTCharacteristicProperties.read
			| GATTCharacteristicProperties.write
			| GATTCharacteristicProperties.indicate
		)
		permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
		await self.server.add_new_characteristic(
			self.service_uuid, self.char_uuid, char_flags, None, permissions
		)
		logger.debug(f"✅ BLE Characteristic added: {self.char_uuid}")
		await self.server.start()

		logger.debug("📡 BLE Server started - now advertising")
		logger.debug(f"🔗 Server 'Car Doctor' is ready for connections!")
		logger.debug(f"📝 Service UUID: {self.service_uuid}")
		logger.debug(f"📝 Characteristic UUID: {self.char_uuid}")
		logger.debug(f"💡 Write '0xF' to the advertised characteristic to stop server")

		# Keep server running until stopped
		while self.running:
			await asyncio.sleep(1)
		


	def read_request(self, characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
		logger.debug("📖 BLE READ REQUEST received from client")
		
		# Prepare response data
		if not characteristic.value:
			response_data = b"Hello from Car Doctor BLE Server"
			speed_data = str(OBDManager().get_speed())
			characteristic.value = speed_data.encode('utf-8')
			logger.debug("📖 No existing value, setting default response")
		
		try:
			decoded_response = characteristic.value.decode('utf-8') if isinstance(characteristic.value, (bytes, bytearray)) else str(characteristic.value)
			logger.debug(f"📤 SENDING RESPONSE to client: '{decoded_response}'")
		except:
			logger.debug(f"📤 SENDING RAW BYTES to client: {characteristic.value}")

		return characteristic.value


	def write_request(self, characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
		logger.debug("✍️ BLE WRITE REQUEST received from client")
		logger.debug(f"✍️ Received data: {value}")
		try:
			decoded_value = value.decode('utf-8') if isinstance(value, bytes) else str(value)
			logger.debug(f"✍️ Decoded message: '{decoded_value}'")
		except:
			logger.debug(f"✍️ Raw bytes: {value}")
		
		speed_data = str(OBDManager().get_speed())
		characteristic.value = speed_data.encode('utf-8')
		logger.debug(f"✍️ Characteristic value updated to: {characteristic.value}")
		
		if value == b"\x0f":
			logger.debug("🛑 SHUTDOWN TRIGGER received - stopping server")
			self.shutdown()

	def shutdown(self):
		"""Stop the daemon server"""
		logger.debug("🛑 Stopping BLE daemon server...")
		self.running = False


