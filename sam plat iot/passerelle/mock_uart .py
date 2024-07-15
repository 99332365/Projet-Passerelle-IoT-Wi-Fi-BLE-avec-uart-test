import time

class MockUART:
    def __init__(self):
        self.tx_buffer = []
        self.rx_buffer = []

    def write(self, data):
        self.tx_buffer.append(data)
        # Simuler que les données sont immédiatement disponibles dans le buffer de réception
        self.rx_buffer.append(data)

    def any(self):
        return len(self.rx_buffer) > 0

    def read(self):
        if self.any():
            return self.rx_buffer.pop(0).encode('utf-8')
        return None

# Utiliser la classe MockUART à la place de machine.UART pour les tests
uart = MockUART()

def send_data_via_uart(data):
    uart.write(data)

def read_data_via_uart():
    if uart.any():
        return uart.read().decode('utf-8')
    return None

# Exemple d'utilisation
if __name__ == "__main__":
    while True:
        data = "Hello from FiPy\n"
        send_data_via_uart(data)
        print("Data sent: ", data)
        time.sleep(1)

        received_data = read_data_via_uart()
        if received_data:
            print("Data received: ", received_data)
        time.sleep(1)
