import ubinascii
from network import Bluetooth
import network
import socket
import machine
import _thread
import time
from config import *

# MockUART class and functions
class MockUART:
    def __init__(self):
        self.tx_buffer = []
        self.rx_buffer = []

    def write(self, data):
        self.tx_buffer.append(data)
        self.rx_buffer.append(data)

    def any(self):
        return len(self.rx_buffer) > 0

    def read(self):
        if self.any():
            return self.rx_buffer.pop(0).encode('utf-8')
        return None

uart = MockUART()

def send_data_via_uart(data):
    uart.write(data)

def read_data_via_uart():
    if uart.any():
        return uart.read().decode('utf-8')
    return None

# BLEServer class
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
            mac_addr = self.format_mac_addr(self.bluetooth.get_adv().mac)
            print('Accelerometer Data received from (BLE): {}'.format(value.decode('utf-8')))
            uart_message = 'BLE:{}:{}'.format(mac_addr, value.decode('utf-8'))
            send_data_via_uart(uart_message)
            print('UART message sent: {}'.format(uart_message))
        except Exception as e:
            print('Error in chr_write_callback: {}'.format(e))

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down BLEServer")

# WiFiServer class
class WiFiServer:
    def __init__(self):
        self.clients = {}
        self.clients_lock = _thread.allocate_lock()
        self.sock = None
        self.setup_wifi()

    def setup_wifi(self):
        wlan = network.WLAN(mode=network.WLAN.STA)
        wlan.connect(ssid=WIFI_SSID, auth=(network.WLAN.WPA2, WIFI_PASSWORD))
        while not wlan.isconnected():
            machine.idle()
        print("Connected to WiFi")
        wlan.ifconfig(config=(WIFI_IP, WIFI_NETMASK, WIFI_GATEWAY, WIFI_DNS))
        print("WLAN Config:{}".format(wlan.ifconfig()))
        self.wlan = wlan
        self.setup_socket()

    def setup_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.wlan.ifconfig()[0], WIFI_PORT))
        self.sock.listen(5)
        print("Wi-Fi Server listening on {}:{}".format(self.wlan.ifconfig()[0], WIFI_PORT))

    def receive_data(self, client_sock, client_addr):
        try:
            mac_address = client_sock.recv(1024).decode('utf-8')
            print("Client MAC Address (Wi-Fi): {}".format(mac_address))
            with self.clients_lock:
                self.clients[client_addr[0]] = mac_address
            data = client_sock.recv(1024).decode('utf-8')
            print('Accelerometer Data received from {} (Wi-Fi): {}'.format(client_addr, data))
            uart_message = 'WiFi:{}:{}'.format(mac_address, data)
            send_data_via_uart(uart_message)
            print('UART message sent: {}'.format(uart_message))
            client_sock.send("Acknowledgement: Data received (Wi-Fi)")
        except Exception as e:
            print("Error receiving Wi-Fi data: {}".format(e))
        finally:
            client_sock.close()

    def run(self):
        try:
            while True:
                client_sock, client_addr = self.sock.accept()
                print("Client connected (Wi-Fi):{}".format(client_addr))
                _thread.start_new_thread(self.receive_data, (client_sock, client_addr))
                time.sleep(1)
        except Exception as e:
            print("Error in Wi-Fi server: {}".format(e))
        finally:
            self.sock.close()
            print("Wi-Fi Server stopped")

# Main function
def start_servers():
    ble_server = BLEServer()
    wifi_server = WiFiServer()

    _thread.start_new_thread(wifi_server.run, ())
    ble_server.run()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping servers")

start_servers()
