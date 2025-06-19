import datetime
import os
from functools import wraps
import re
import jwt
from flask import Flask, request, jsonify, send_from_directory, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'miclavesecreta123'

# Usuarios permitidos
USUARIOS = {
    "admin": "1234",
    "usuario": "abcd"
}

# Plantilla HTML completa con login y prueba de recurso protegido
HTML_LOGIN = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login - API JWT</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 2em 0;
            margin: 0;
        }

        .container {
            background-color: #fff;
            padding: 2em 2.5em;
            border-radius: 10px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }

        h1, h2 {
            text-align: center;
            margin-bottom: 1em;
            color: #333;
        }

        label {
            display: block;
            margin: 1em 0 0.3em;
            font-weight: bold;
            color: #444;
        }

        input, textarea {
            width: 100%;
            padding: 0.7em;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 1em;
            box-sizing: border-box;
        }

        textarea {
            resize: vertical;
            font-family: monospace;
        }

        button {
            margin-top: 1.5em;
            width: 100%;
            padding: 0.8em;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.3s;
        }

        button:hover {
            background-color: #0056b3;
        }

        .error, .success {
            margin-top: 1em;
            font-size: 0.95em;
            white-space: pre-wrap;
        }

        .error { color: #d9534f; }
        .success { color: #28a745; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Login</h1>
        <form id="loginForm" autocomplete="off" novalidate>
            <label for="usuario">Usuario</label>
            <input type="text" id="usuario" name="usuario" autocomplete="off" required>

            <label for="clave">Clave</label>
            <input type="password" id="clave" name="clave" autocomplete="new-password" required>

            <button type="submit">Iniciar Sesión</button>
        </form>
        <div id="resultado"></div>

        <hr>

        <h2>Probar recurso protegido</h2>
        <label for="tokenInput">Token:</label>
        <textarea id="tokenInput" rows="5" cols="60" placeholder="Pega aquí tu token JWT"></textarea><br><br>
        <button onclick="probarRecurso()">Acceder a recurso protegido</button>
        <div id="respuestaProtegido"></div>
    </div>

    <script>
        // Función para manejar login
        document.getElementById('loginForm').addEventListener('submit', async function(event) {
            event.preventDefault();
            const usuario = document.getElementById('usuario').value.trim();
            const clave = document.getElementById('clave').value.trim();
            const resultadoDiv = document.getElementById('resultado');
            resultadoDiv.textContent = '';

            if (!usuario || !clave) {
                resultadoDiv.innerHTML = '<p class="error">Por favor, completa todos los campos.</p>';
                return;
            }

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ usuario, clave })
                });

                const data = await response.json();

                if (response.ok) {
                    resultadoDiv.innerHTML = '<p class="success">Login exitoso. Token JWT:</p>' +
                        '<textarea rows="5" readonly>' + data.token + '</textarea>';
                    // También copia automáticamente el token al textarea para probar recurso protegido
                    document.getElementById('tokenInput').value = data.token;
                } else {
                    resultadoDiv.innerHTML = '<p class="error">Error: ' + (data.mensaje || 'Desconocido') + '</p>';
                }
            } catch (e) {
                resultadoDiv.innerHTML = '<p class="error">No se pudo conectar al servidor.</p>';
            }
        });

        // Función para probar recurso protegido con el token
        async function probarRecurso() {
            const token = document.getElementById('tokenInput').value.trim();
            const respuestaDiv = document.getElementById('respuestaProtegido');
            respuestaDiv.textContent = '';

            if (!token) {
                respuestaDiv.innerHTML = '<p class="error">Por favor, ingresa un token JWT para probar.</p>';
                return;
            }

            try {
                const response = await fetch('/recurso-protegido', {
                    method: 'GET',
                    headers: {
                        'x-access-token': token
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    respuestaDiv.innerHTML = '<p class="success">' + data.mensaje + '</p>';
                } else {
                    respuestaDiv.innerHTML = '<p class="error">Error: ' + (data.mensaje || 'Desconocido') + '</p>';
                }
            } catch (e) {
                respuestaDiv.innerHTML = '<p class="error">No se pudo conectar al servidor.</p>';
            }
        }
    </script>
</body>
</html>
"""


# Validación de formato de usuario y clave
def validar_usuario_clave(usuario: str, clave: str):
    if not usuario or not clave:
        return False, "Usuario y clave no pueden estar vacíos."
    if usuario.strip() != usuario or clave.strip() != clave:
        return False, "Usuario y clave no deben tener espacios al inicio o final."
    patron = r'^\w+$'
    if not re.match(patron, usuario):
        return False, "Usuario contiene caracteres inválidos. Solo letras, números y guion bajo permitidos."
    if not re.match(patron, clave):
        return False, "Clave contiene caracteres inválidos. Solo letras, números y guion bajo permitidos."
    return True, ""


# Ruta principal: muestra formulario
@app.route('/')
def inicio():
    return render_template_string(HTML_LOGIN)


# Favicon opcional
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Ruta de login
# noinspection PyDeprecation
@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json() if request.is_json else request.form
    usuario = datos.get('usuario')
    clave = datos.get('clave')

    if not usuario or not clave:
        return jsonify({"mensaje": "Faltan datos obligatorios: usuario y clave", "error": "missing_data"}), 400

    valido, mensaje_error = validar_usuario_clave(usuario, clave)
    if not valido:
        return jsonify({"mensaje": mensaje_error, "error": "invalid_format"}), 400

    if USUARIOS.get(usuario) != clave:
        return jsonify({"mensaje": "Credenciales incorrectas", "error": "invalid_credentials"}), 401

    token = jwt.encode({
        'usuario': usuario,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    if isinstance(token, bytes):
        token = token.decode('utf-8')

    return jsonify({"token": token})


# Decorador para proteger rutas
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({"mensaje": "Token es requerido para acceder", "error": "token_missing"}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            usuario = data['usuario']
        except jwt.ExpiredSignatureError:
            return jsonify({"mensaje": "Token expirado, por favor loguéate de nuevo", "error": "token_expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"mensaje": "Token inválido", "error": "token_invalid"}), 401
        return f(usuario, *args, **kwargs)

    return decorated


# Ruta protegida con JWT
@app.route('/recurso-protegido')
@token_required
def recurso_protegido(usuario):
    return jsonify({"mensaje": f"Hola {usuario}, accediste a un recurso protegido."})


# Iniciar servidor
if __name__ == '__main__':
    app.run(debug=True)
