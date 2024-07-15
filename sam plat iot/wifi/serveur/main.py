# main.py -- put your code here!
# import network
# import socket
# import machine
# import time
# import ubinascii
# import _thread


# # Verrou pour protéger l'accès à la liste des clients
# clients_lock = _thread.allocate_lock()


# # Dictionnaire pour stocker les adresses IP et les adresses MAC des clients connectés
# clients = {}


# def setup_wifi():
#     wlan = network.WLAN(mode=network.WLAN.STA)
#     wlan.connect(ssid='dragino-227e3c', auth=(network.WLAN.WPA2, 'dragino+dragino'))
#     while not wlan.isconnected():
#         machine.idle()  # Attente passive de la connexion


#     print("Connecté au WiFi")
#     wlan.ifconfig(config=('10.2.28.1', '255.255.0.0', '10.2.1.1', '10.2.1.1'))   # Configuration de l'adresse IP du FiPy
#     print(wlan.ifconfig())
   
#     return wlan


# def receive_data(client_sock, client_addr):
#     try:
#         mac_address = client_sock.recv(1024).decode('utf-8')
#         print('Adresse MAC du client:', mac_address)
#         with clients_lock:
#             clients[client_addr[0]] = mac_address
#         data = client_sock.recv(1024).decode('utf-8')
#         print("Données reçues de", client_addr, ":", data)
#         client_sock.send(b"Acknowledgement: Donnees recues")
#     except Exception as e:
#         print("Erreur lors de la réception des données:", e)
#     finally:
#         client_sock.close()


# wlan = setup_wifi()
# receiver_ip = wlan.ifconfig()[0]
# print("Adresse IP du serveur:", receiver_ip)
# receiver_port = 5000


# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.bind((receiver_ip, receiver_port))
# sock.listen(5)  # Accepter jusqu'à 5 connexions simultanées


# print("En attente de connexions...")


# try:
#     while True:
#         client_sock, client_addr = sock.accept()
#         print('Client connecté:', client_addr)
#         _thread.start_new_thread(receive_data, (client_sock, client_addr))
# except KeyboardInterrupt:
#     print("Arrêt du serveur...")
#     sock.close()


import network
import socket
import machine
import time
import ubinascii
import _thread

# Verrou pour protéger l'accès à la liste des clients
clients_lock = _thread.allocate_lock()

# Dictionnaire pour stocker les adresses IP et les adresses MAC des clients connectés
clients = {}

def setup_wifi():
    wlan = network.WLAN(mode=network.WLAN.STA)
    wlan.connect(ssid='dragino-227e3c', auth=(network.WLAN.WPA2, 'dragino+dragino'))
    while not wlan.isconnected():
        machine.idle()  # Attente passive de la connexion

    print("Connecté au WiFi")
    wlan.ifconfig(config=('10.2.28.1', '255.255.0.0', '10.2.1.1', '10.2.1.1'))   # Configuration de l'adresse IP du serveur Wi-Fi
    print(wlan.ifconfig())
   
    return wlan

def receive_data(client_sock, client_addr):
    try:
        mac_address = client_sock.recv(1024).decode('utf-8')
        print('Adresse MAC du client Wi-Fi:', mac_address)
        with clients_lock:
            clients[client_addr[0]] = mac_address
        data = client_sock.recv(1024).decode('utf-8')
        print("Données d'accéléromètre reçues de", client_addr, ":", data)
        # Ici vous pouvez ajouter le traitement des données d'accéléromètre reçues
        client_sock.send("Acknowledgement: Données reçues")
    except Exception as e:
        print("Erreur lors de la réception des données Wi-Fi:", e)
    finally:
        client_sock.close()

wlan = setup_wifi()
receiver_ip = wlan.ifconfig()[0]
print("Adresse IP du serveur Wi-Fi:", receiver_ip)
receiver_port = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((receiver_ip, receiver_port))
sock.listen(5)  # Accepter jusqu'à 5 connexions simultanées

print("En attente de connexions...")

try:
    while True:
        client_sock, client_addr = sock.accept()
        print('Client Wi-Fi connecté:', client_addr)
        _thread.start_new_thread(receive_data, (client_sock, client_addr))
except KeyboardInterrupt:
    print("Arrêt du serveur Wi-Fi...")
    sock.close()
