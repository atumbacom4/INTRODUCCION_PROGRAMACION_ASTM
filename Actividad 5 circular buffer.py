class Buffer:
    def __init__(self, size, circular=False):
        self.size = size
        self.circular = circular
        self.buffer = []
        self.rejected_data = []

    def write(self, data):
        if len(self.buffer) < self.size:
            self.buffer.append(data)
            print(f"[✓] Dato '{data}' escrito en el buffer.")
        elif self.circular:
            overwritten = self.buffer.pop(0)
            self.buffer.append(data)
            print(f"[↺] Buffer lleno. '{overwritten}' sobrescrito con '{data}'.")
        else:
            self.rejected_data.append(data)
            print(f"[✗] Buffer lleno. Dato '{data}' rechazado.")

    def status(self):
        print("\n📦 Estado actual del buffer:")
        print("Contenido:", self.buffer)
        print("Rechazados:", self.rejected_data)

# --- Simulación ---

print("🔧 Iniciando simulación de buffer...")

# Crear un buffer de tamaño 5
buffer = Buffer(size=5, circular=False)

# Escribir datos
datos = ["A", "B", "C", "D", "E", "F", "G"]
for d in datos:
    buffer.write(d)

buffer.status()

# Probar con modo circular
print("\n🔁 Ahora con modo circular activado:\n")

buffer_circular = Buffer(size=5, circular=True)

for d in datos:
    buffer_circular.write(d)

buffer_circular.status()
