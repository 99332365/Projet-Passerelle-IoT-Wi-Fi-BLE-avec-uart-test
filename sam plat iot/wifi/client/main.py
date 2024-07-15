# # main.py -- put your code here!

# # Client.py

import network
import socket
import machine
import time
import ubinascii


def setup_wifi(client_ip):
    wlan = network.WLAN(mode=network.WLAN.STA)
    wlan.connect(ssid='dragino-227e3c', auth=(network.WLAN.WPA2, 'dragino+dragino'))
    while not wlan.isconnected():
        machine.idle()  # Attente passive de la connexion
   
    print("Connecté au WiFi")
    wlan.ifconfig(config=(client_ip, '255.255.0.0', '10.2.1.1', '10.2.1.1'))   # Configuration de l'adresse IP du client
    print(wlan.ifconfig())
   
    return wlan

def send_acceleration_data(receiver_ip, receiver_port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   
    try:
        sock.connect((receiver_ip, receiver_port))
        mac_address = ubinascii.hexlify(machine.unique_id()).decode('utf-8')
        sock.send(mac_address.encode('utf-8'))
       
        time.sleep(0.1)  # Attendre un peu avant d'envoyer les données
        sock.send(data.encode('utf-8'))
        response = sock.recv(1024)
        print("Réponse du serveur:", response.decode('utf-8'))
    except Exception as e:
        print("Erreur lors de l'envoi des données:", e)
    finally:
        sock.close()

# Liste pour stocker les adresses IP des clients connectés
client_ips = []
server_ip = "10.2.28.1"
server_port = 5000

wlan = network.WLAN(mode=network.WLAN.STA)

while True:
    if not wlan.isconnected():
        wlan.connect(ssid='dragino-227e3c', auth=(network.WLAN.WPA2, 'dragino+dragino'))
        while not wlan.isconnected():
            machine.idle()  # Attente passive de la connexion
        print("Connecté au WiFi")
        wlan.ifconfig(config=('10.2.28.' + str(machine.rng() % 253 + 2), '255.255.0.0', '10.2.1.1', '10.2.1.1'))
        print(wlan.ifconfig())

    client_ip = wlan.ifconfig()[0]

    if client_ip not in client_ips:
        client_ips.append(client_ip)
        print("Client Wi-Fi connecté:", client_ip)

    # Simulation de données d'accéléromètre pour chaque client
    acceleration_data = "AccelX={}, AccelY={}, AccelZ={}".format(
        machine.rng() % 200 - 100, machine.rng() % 200 - 100, machine.rng() % 200 - 100
    )
    send_acceleration_data(server_ip, server_port, acceleration_data)

    time.sleep(10)  # Attendre 10 secondes entre chaque envoi de données
