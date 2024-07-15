#main client server.py 
from network import Bluetooth 
import time

# Initialisation du Bluetooth
bluetooth = Bluetooth()
bluetooth.init()

# UUID pour le service et la caractéristique
SERVICE_UUID = 0xec00
CHARACTERISTIC_UUID = 0xec0e

# Dictionnaire pour stocker les connexions clients actives
connected_clients = {}

# Dictionnaire pour stocker les clients initialement connectés
initial_connected_clients = {}

def format_mac_addr(mac_addr):
    """Formatte l'adresse MAC en chaîne lisible."""
    return ":".join("{:02x}".format(x) for x in mac_addr)

def update_client_status(mac_addr, status):
    """Met à jour le statut du client connecté ou déconnecté."""
    mac_addr_str = format_mac_addr(mac_addr)
    if status:
        connected_clients[mac_addr_str] = {"type": "BLE", "status": status}
    else:
        connected_clients.pop(mac_addr_str, None)
    print("Connected clients:", connected_clients)

    """ Callback de connexion/déconnexion du client"""
 
def conn_cb(conn):
    events = conn.events()
    adv = bluetooth.get_adv()
    if adv:
        mac_addr = adv.mac
        if events & Bluetooth.CLIENT_CONNECTED:
            print('Client connecté')
            # Enregistrer les clients initialement connectés
            if mac_addr not in initial_connected_clients:
                initial_connected_clients[mac_addr] = True
            update_client_status(mac_addr, True)
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print('Client déconnecté')
            update_client_status(mac_addr, False)

# Callback de lecture/écriture de caractéristique
def chr_write_callback(chr, event):
    if event == Bluetooth.CHAR_READ_EVENT:##***** a voir 
        v = chr.value()
        print("Données d'accélération reçues:", v)
        # Exemple de réponse au client (optionnel)
        chr.write("Request Acceleration Data")
    else:
        print("absence d evenement d ecriture", chr.value())

# Configuration de l'annonce du service BLE
bluetooth.set_advertisement(name='FiPy Server', service_uuid=SERVICE_UUID)

# Callbacks pour les événements de connexion et déconnexion
bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)

# Démarrage de l'annonce BLE
bluetooth.advertise(True)

# Création du service BLE
srv = bluetooth.service(uuid=SERVICE_UUID, isprimary=True, nbr_chars=1)

# Création de la caractéristique BLE
chr = srv.characteristic(uuid=CHARACTERISTIC_UUID, value='')

# Callback pour les événements d'écriture de la caractéristique
chr.callback(trigger=Bluetooth.CHAR_WRITE_EVENT, handler=chr_write_callback)

print('Serveur BLE démarré')
try:
    while True:
        time.sleep(1)
finally:
    bluetooth.stop_advertising()
    print('Liste des clients connectés à la fin de l\'exécution:')
    print(connected_clients)

    # # Comparer les clients initialement connectés et ceux actuellement connectés
    # initial_connected_clients_str = {format_mac_addr(mac): True for mac in initial_connected_clients}
    # lost_clients = [client for client in initial_connected_clients_str if client not in connected_clients]
    # print('Liste des clients perdus:')
    # print(lost_clients)
    # Convertir les adresses MAC en chaînes formatées
    initial_connected_clients_str = {format_mac_addr(mac): True for mac in initial_connected_clients}
    currently_connected_clients_str = {format_mac_addr(mac): True for mac in connected_clients}

# Identifier les clients perdus
    lost_clients = [client for client in initial_connected_clients_str if client not in currently_connected_clients_str]

# Afficher la liste des clients perdus
    print('Liste des clients perdus:')
    print(lost_clients)
