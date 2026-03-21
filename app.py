from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de usuario
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'estudiante' o 'profesor'

    def __repr__(self):
        return f'<Usuario {self.username}>'

# Crear la base de datos
with app.app_context():
    db.create_all()

# Página de inicio
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        usuario_input = request.form['username']
        contrasena_input = request.form['password']
        rol_input = request.form['rol']

        # Verificar si usuario ya existe
        if Usuario.query.filter_by(username=usuario_input).first():
            error = "El usuario ya existe"
        else:
            # Guardar usuario con contraseña encriptada
            nuevo_usuario = Usuario(
                username=usuario_input,
                password=generate_password_hash(contrasena_input),
                rol=rol_input
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)
# NUEVO login funcional con base de datos
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario_input = request.form['username']
        contrasena_input = request.form['password']
        
        # Buscar usuario en la base de datos
        user = Usuario.query.filter_by(username=usuario_input).first()
        
        # Verificar contraseña hasheada
        if user and check_password_hash(user.password, contrasena_input):
            session['username'] = user.username
            session['rol'] = user.rol
            return redirect(url_for('home'))
        else:
            error = "Usuario o contraseña incorrectos"
            
    return render_template('login.html', error=error)

if __name__ == "__main__":
    app.run(debug=True)