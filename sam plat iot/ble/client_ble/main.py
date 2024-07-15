
from network import Bluetooth
import time
from LIS2HH12 import LIS2HH12  # Assurez-vous que le fichier LIS2HH12.py est dans le même répertoire

# Initialisation du Bluetooth
bluetooth = Bluetooth()
bluetooth.init()

# UUIDs pour le service et la caractéristique
SERVICE_UUID = 0xec00
CHARACTERISTIC_UUID = 0xec0e

# Initialisation de l'accéléromètre
accelerometer = LIS2HH12()

# Fonction pour se connecter au serveur et envoyer un message
def connect_to_server():
    bluetooth.start_scan(-1)
    try:
        while True:
            adv = bluetooth.get_adv()
            if adv and bluetooth.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) == 'FiPy Server':
                conn = bluetooth.connect(adv.mac)
                mac_addr = ":".join("{:02x}".format(x) for x in adv.mac)
                print('Connecté au serveur FiPy', mac_addr)

                # Lire la valeur de la caractéristique pour chaque client
                services = conn.services()
                for service in services:
                    if service.uuid() == SERVICE_UUID:
                        chars = service.characteristics()
                        for char in chars:
                            if char.uuid() == CHARACTERISTIC_UUID:
                                # Envoyer les données d'accélération au serveur
                                #for _ in range(10):  # Envoyer 10 fois les données
                                    x, y, z = accelerometer.acceleration()
                                    data = '{:.2f},{:.2f},{:.2f}'.format(x, y, z)
                                    char.write(data)
                                    print("Données d'accélération envoyées:", data)
                                    time.sleep(1)  # Attendre 1 seconde entre chaque envoi

                # Déconnecter après interaction
                conn.disconnect()
                print('Déconnecté du serveur', mac_addr)
                break

    finally:
        bluetooth.stop_scan()

# Appeler la fonction pour se connecter au serveur
connect_to_server()
