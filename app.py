from flask import Flask, render_template, request, jsonify
import os
import psycopg2
from psycopg2.extras import DictCursor

app = Flask(__name__)

# 🔑 PEGA AQUÍ TU ENLACE URI DE SUPABASE (Recuerda cambiar [YOUR-PASSWORD] por tu contraseña real)
DATABASE_URL = "postgresql://postgres:TU_CONTRASEÑA_DE_SUPABASE@db.xxxxxx.supabase.co:5432/postgres"

def get_db():
    """Establece la conexión con la base de datos PostgreSQL en la nube."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    return conn

def inicializar_base_de_datos():
    """Crea la tabla en la nube automáticamente si no existe al encender el servidor."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lugares (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                lat REAL NOT NULL,
                lng REAL NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("Base de datos en la nube inicializada correctamente.")
    except Exception as e:
        print(f"Error al conectar con la base de datos de la nube: {e}")

# Ejecutamos la creación de tablas al arrancar la app
inicializar_base_de_datos()

@app.route('/')
def index():
    # Renderiza tu mapa principal (busca index.html dentro de la carpeta templates)
    return render_template('index.html')

@app.route('/registro')
def registro():
    # Muestra el formulario para registrar un nuevo punto
    return render_template('registro.html')

@app.route('/agregar_lugar', methods=['POST'])
def agregar_lugar():
    nombre = request.form['nombre_lugar']
    descripcion = request.form['descripcion']
    lat = float(request.form['lat']) # Convertimos a número decimal
    lng = float(request.form['lng']) # Convertimos a número decimal
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # En PostgreSQL de la nube se usa %s en lugar de ? para insertar valores
        cursor.execute(
            'INSERT INTO lugares (nombre, descripcion, lat, lng) VALUES (%s, %s, %s, %s)', 
            (nombre, descripcion, lat, lng)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return "<h1>¡Centro Agregado con Éxito!</h1><p>Los datos ya están guardados seguros en la nube de Supabase. Ya puedes cerrar esta pestaña.</p>"
    except Exception as e:
        return f"<h1>Error al guardar en la nube</h1><p>{str(e)}</p>"

@app.route('/api/lugares')
def get_lugares():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM lugares')
        lugares_raw = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Convertimos los resultados a un formato JSON limpio que Leaflet entienda
        lugares = []
        for ix in lugares_raw:
            lugares.append({
                "id": ix["id"],
                "nombre": ix["nombre"],
                "descripcion": ix["descripcion"],
                "lat": ix["lat"],
                "lng": ix["lng"]
            })
            
        return jsonify(lugares)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
