

Ce projet implémente une passerelle IoT (Internet of Things) combinant les technologies Bluetooth Low Energy (BLE) et Wi-Fi pour permettre la collecte et la transmission de données d'accélération provenant de capteurs. Les données sont partagées via une interface UART, et des clients Wi-Fi et BLE peuvent interagir avec la passerelle pour envoyer et recevoir des informations.

Le projet inclut les serveurs Wi-Fi et BLE, ainsi qu'un client BLE capable de communiquer avec la passerelle.
Fonctionnalités

    Wi-Fi Server : Permet la connexion de clients Wi-Fi pour envoyer des données d'accélération.
    BLE Server : Permet la connexion de clients BLE pour envoyer des données d'accélération.
    UART Communication : Envoie les données reçues via BLE ou Wi-Fi à travers une interface UART simulée (MockUART).
    Gestion des connexions : Suivi des clients connectés, mise à jour des statuts des connexions pour les clients Wi-Fi et BLE.
    Client BLE : Capte les données d'accélération à partir d'un capteur intégré (LIS2HH12) et les envoie à la passerelle BLE.
