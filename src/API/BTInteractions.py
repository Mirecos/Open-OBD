import asyncio
from email.mime import message
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
import json

logger = Logger("Bluetooth Server")

# NOTE: Some systems require different synchronization methods.
trigger: Union[asyncio.Event, threading.Event]
if sys.platform in ["darwin", "win32"]:
    trigger = threading.Event()
else:
    trigger = asyncio.Event()


class Request(Enum):
    HEALTHCHECK = "healthcheck"
    GET_SPEED = "get_speed"
    GET_RPM = "get_rpm"
    GET_COOLANT_TEMP = "get_coolant_temp"
    GET_THROTTLE_POSITION = "get_throttle_position"
    GET_DTC = "get_dtc"
	


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

		try:
			decoded_response = characteristic.value.decode('utf-8') if isinstance(characteristic.value, (bytes, bytearray)) else str(characteristic.value)
			logger.debug(f"📤 SENDING RESPONSE to client: '{decoded_response}'")
		except:
			logger.debug(f"📤 SENDING RAW BYTES to client: {characteristic.value}")

		return characteristic.value


	def write_request(self, characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
		logger.debug(f"✍️ BLE WRITE REQUEST received :  Received request : {value}")
		response = None
		try:
			# Handle both bytes and bytearray
			if isinstance(value, (bytes, bytearray)):
				decoded_value = value.decode('utf-8')
			else:
				decoded_value = str(value)
			logger.debug(f"✍️ Decoded request: '{decoded_value}'")
			response = self.handle_request(decoded_value)
		except Exception as e:
			logger.error(f"✍️ Failed to decode request: {e}")
			response = self.generate_response(False, {}, "Failed to decode request")
		
		# Encode the response string to bytes for BLE characteristic
		characteristic.value = response.encode('utf-8')
		logger.debug(f"✍️ Characteristic value updated to: {characteristic.value}")


	def generate_response(self, success: bool, data: Any, message: str = None) -> Any:
		return json.dumps({
			"status": "1" if success else "0",
			"data": data,
			"message": message if message else "No message specified",
		}, separators=(',', ':'))

	def handle_request(self, request: str) -> Any:
		print("Handling request:", str(request))
		match str(request):
			case Request.HEALTHCHECK.value:
				return self.generate_response(True, {}, "Server is healthy !")
			case Request.GET_SPEED.value:
				speed_data = str(OBDManager().get_speed())
				return self.generate_response(True, speed_data, "Fetched current speed.")
			case Request.GET_RPM.value:
				rpm_data = str(OBDManager().get_rpm())
				return self.generate_response(True, rpm_data, "Fetched current RPM.")
			case Request.GET_COOLANT_TEMP.value:
				coolant_temp_data = str(OBDManager().get_coolant_temp())
				return self.generate_response(True, coolant_temp_data, "Fetched current coolant temperature.")
			case Request.GET_THROTTLE_POSITION.value:
				throttle_position_data = str(OBDManager().get_throttle_pos())
				return self.generate_response(True, throttle_position_data, "Fetched current throttle position.")
			case Request.GET_DTC.value:
				dtc_data = str(OBDManager().get_dtc())
				return self.generate_response(True, dtc_data, "Fetched current DTC.")

		return self.generate_response(False, {}, "Unknown request")


	def shutdown(self):
		"""Stop the daemon server"""
		logger.debug("🛑 Stopping BLE daemon server...")
		self.running = False


