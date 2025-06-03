import socket

def verificar_conexion(host: str, puerto: int, timeout: float = 3.0):
    try:
        with socket.create_connection((host, puerto), timeout=timeout):
            print(f"✅ Conexión exitosa a {host}:{puerto}")
            return True
    except (socket.timeout, socket.error) as e:
        print(f"❌ No se pudo conectar a {host}:{puerto} - Error: {e}")
        return False

# Ejemplo de uso:
verificar_conexion("www.google.com", 80)
