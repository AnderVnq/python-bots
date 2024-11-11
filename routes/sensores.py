from flask import Blueprint, request, jsonify




sensores_bp = Blueprint('sensores_bp', __name__)




registros = []



@sensores_bp.route('/api/sensores', methods=['GET', 'POST'])
def manejar_datos():
    if request.method == 'POST':
        # Si es una solicitud POST, recibimos los datos de los sensores
        datos = request.get_json()

        if not datos:
            return jsonify({"error": "Datos no recibidos"}), 400

        # Validación de los tipos de datos
        try:
            sensor_humo = int(datos.get("sensorHumo"))
            sensor_fuego = int(datos.get("sensorFuego"))
            timestamp = str(datos.get("timestamp"))  # En este caso esperamos un timestamp como string
        except (ValueError, TypeError):
            return jsonify({"error": "Tipo de dato incorrecto"}), 400

        # Validación para asegurarnos de que los datos no sean nulos
        if sensor_humo is None or sensor_fuego is None or timestamp is None:
            return jsonify({"error": "Faltan datos de los sensores o timestamp"}), 400

        # Crear un diccionario con los datos de los sensores
        registro = {
            "sensorHumo": sensor_humo,
            "sensorFuego": sensor_fuego,
            "timestamp": timestamp
        }

        # Agregar el registro a la lista
        registros.append(registro)

        # Responder con un mensaje de éxito
        return jsonify({"status": "Datos recibidos correctamente"}), 200
    
    elif request.method == 'GET':
        # Si es una solicitud GET, devolvemos los registros almacenados
        return jsonify(registros), 200








