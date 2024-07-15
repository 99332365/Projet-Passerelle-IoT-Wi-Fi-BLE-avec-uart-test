import ubinascii
from network import Bluetooth
import _thread
import time
from config import *
from mock_uart import send_data_via_uart  # Importer send_data_via_uart

class BLEServer:
    def __init__(self):
        self.connected_clients = {}
        self.clients_lock = _thread.allocate_lock()
        self.bluetooth = Bluetooth()
        self.setup_ble()

    def setup_ble(self):
        self.bluetooth.init()
        self.bluetooth.set_advertisement(name=BLE_DEVICE_NAME, service_uuid=ubinascii.unhexlify(BLE_SERVICE_UUID))
        self.bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.conn_cb)
        self.bluetooth.advertise(True)
        self.srv = self.bluetooth.service(uuid=ubinascii.unhexlify(BLE_SERVICE_UUID), isprimary=True, nbr_chars=1)
        self.chr = self.srv.characteristic(uuid=ubinascii.unhexlify(BLE_CHARACTERISTIC_UUID), value=b'')
        self.chr.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=self.chr_write_callback)
        print('BLE Server started')

    def format_mac_addr(self, mac_addr):
        return ':'.join(['%02x' % b for b in mac_addr])

    def update_client_status(self, mac_addr, status):
        mac_str = self.format_mac_addr(mac_addr)
        with self.clients_lock:
            self.connected_clients[mac_str] = status
        print("Connected clients: {}".format(self.connected_clients))

    def conn_cb(self, conn):
        try:
            events = conn.events()
            adv = self.bluetooth.get_adv()
            if adv:
                mac_addr = adv.mac
                if events & Bluetooth.CLIENT_CONNECTED:
                    print('Client connected (BLE): {}'.format(self.format_mac_addr(mac_addr)))
                    self.update_client_status(mac_addr, True)
                elif events & Bluetooth.CLIENT_DISCONNECTED:
                    print('Client disconnected (BLE): {}'.format(self.format_mac_addr(mac_addr)))
                    self.update_client_status(mac_addr, False)
        except Exception as e:
            print('Error in conn_cb: {}'.format(e))
            if adv:
                self.bluetooth.disconnect(adv.mac)
            print('Forced disconnection.')

    def chr_write_callback(self, chr, event):
        try:
            value = chr.value()
            mac_addr = self.bluetooth.get_adv().mac
            data = 'BLE {}: {}'.format(self.format_mac_addr(mac_addr), value.decode('utf-8'))
            print('Accelerometer Data received from (BLE): {}'.format(value.decode('utf-8')))
            send_data_via_uart(data)
        except Exception as e:
            print('Error in chr_write_callback: {}'.format(e))

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down BLEServer")

# Initialisation et démarrage du serveur BLE
ble_server = BLEServer()
_thread.start_new_thread(ble_server.run, ())
