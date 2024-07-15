import network
import socket
import machine
import _thread
import time
from config import *
from mock_uart import send_data_via_uart  # Importer send_data_via_uart

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

            uart_data = 'WiFi {}: {}'.format(mac_address, data)
            send_data_via_uart(uart_data)

            client_sock.send("Acknowledgement: Data received (Wi-Fi)")
        except Exception as e:
            print(f"Error receiving Wi-Fi data: {e}")
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
            print(f"Error in Wi-Fi server: {e}")
        finally:
            self.sock.close()
            print("Wi-Fi Server stopped")

