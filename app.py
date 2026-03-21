from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto por algo seguro
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------
# Modelo de Usuario
# ---------------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'estudiante' o 'profesor'

# Crear la base de datos
with app.app_context():
    db.create_all()

# ---------------------------
# Decorador para rutas protegidas
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Rutas
# ---------------------------

@app.route('/')
def home():
    return render_template('index.html')

# Registro de usuarios
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        usuario_input = request.form['username']
        contrasena_input = request.form['password']
        rol_input = request.form['rol']

        if Usuario.query.filter_by(username=usuario_input).first():
            error = "El usuario ya existe"
        else:
            nuevo_usuario = Usuario(
                username=usuario_input,
                password=generate_password_hash(contrasena_input),
                rol=rol_input
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario_input = request.form['username']
        contrasena_input = request.form['password']
        user = Usuario.query.filter_by(username=usuario_input).first()

        if user and check_password_hash(user.password, contrasena_input):
            session['username'] = user.username
            session['rol'] = user.rol

            # Redirigir según rol
            if user.rol == 'estudiante':
                return redirect(url_for('dashboard_estudiante'))
            elif user.rol == 'profesor':
                return redirect(url_for('dashboard_profesor'))
            else:
                error = "Rol desconocido"
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template('login.html', error=error)

# Dashboards
@app.route('/dashboard_estudiante')
@login_required
def dashboard_estudiante():
    if session.get('rol') != 'estudiante':
        return "No tienes permiso para acceder a esta página"
    return render_template('dashboard_estudiante.html', username=session['username'])

@app.route('/dashboard_profesor')
@login_required
def dashboard_profesor():
    if session.get('rol') != 'profesor':
        return "No tienes permiso para acceder a esta página"
    return render_template('dashboard_profesor.html', username=session['username'])

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------------
# Ejecutar servidor
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)