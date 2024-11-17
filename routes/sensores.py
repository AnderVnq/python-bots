from flask import Blueprint, request, jsonify,current_app
from datetime import datetime
import sqlite3



sensores_bp = Blueprint('sensores_bp', __name__)




registros = []




@sensores_bp.route('/api/sensores', methods=['GET', 'POST'])
def manejar_datos():
    conn = current_app.config['db_connection']
    cursor = conn.cursor()

    if request.method == 'POST':
        datos = request.get_json()
        if not datos:
            return jsonify({"status": False, "message": "Datos no recibidos"}), 400

        try:
            dato1 = int(datos.get("dato1"))
            dato2 = int(datos.get("dato2"))
            fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return jsonify({"status": False, "message": "Tipo de dato incorrecto"}), 400

        cursor.execute("INSERT INTO registros (dato1, dato2, fecha) VALUES (?, ?, ?)",
                       (dato1, dato2, fecha_hora_actual))
        conn.commit()

        return jsonify({"status": True, "message": "Datos recibidos correctamente"}), 200

    elif request.method == 'GET':
        cursor.execute("SELECT dato1, dato2, fecha FROM registros")
        registros = cursor.fetchall()
        registros_json = [{"dato1": row[0], "dato2": row[1], "fecha": row[2]} for row in registros]
        return jsonify(registros_json), 200







