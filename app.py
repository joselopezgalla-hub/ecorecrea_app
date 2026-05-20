from flask import Flask, render_template, request, g, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'ecorecrea.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, correo TEXT UNIQUE, password TEXT)''')
        db.execute('''CREATE TABLE IF NOT EXISTS lugares (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, descripcion TEXT, lat REAL, lng REAL)''')
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['POST'])
def registro():
    nombre = request.form['nombre']
    correo = request.form['correo']
    password = request.form['password']
    db = get_db()
    try:
        db.execute('INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)', (nombre, correo, password))
        db.commit()
        return f'''
        <div style="text-align:center; font-family:sans-serif; margin-top:100px; color:#2e7d32;">
            <h1>¡Registro exitoso!</h1>
            <p>Bienvenido a ecorecrea, {nombre}.</p>
            <br>
            <a href="/" style="background-color:#66bb6a; color:white; padding:12px 25px; text-decoration:none; border-radius:25px; font-weight:bold;">Volver al inicio</a>
        </div>
        '''
    except sqlite3.IntegrityError:
        # Aquí se controla si el correo ya existe en la base de datos
        return f'''
        <div style="text-align:center; font-family:sans-serif; margin-top:100px; color:#c62828;">
            <h1>Error: Cuenta ya registrada</h1>
            <p>El correo electrónico <b>{correo}</b> ya se encuentra registrado en nuestra comunidad.</p>
            <br>
            <a href="/" style="background-color:#ef5350; color:white; padding:12px 25px; text-decoration:none; border-radius:25px; font-weight:bold;">Intentar de nuevo</a>
        </div>
        '''

@app.route('/agregar_lugar', methods=['POST'])
def agregar_lugar():
    nombre = request.form['nombre_lugar']
    descripcion = request.form['descripcion']
    lat = request.form['lat']
    lng = request.form['lng']
    db = get_db()
    db.execute('INSERT INTO lugares (nombre, descripcion, lat, lng) VALUES (?, ?, ?, ?)', (nombre, descripcion, float(lat), float(lng)))
    db.commit()
    return f"<h1>¡Centro Agregado!</h1><p>Todos los usuarios ahora pueden ver este punto en el mapa y saber cómo llegar.</p><a href='/'>Volver al mapa</a>"

@app.route('/api/lugares')
def get_lugares():
    db = get_db()
    lugares = db.execute('SELECT * FROM lugares').fetchall()
    return jsonify([dict(ix) for ix in lugares])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)