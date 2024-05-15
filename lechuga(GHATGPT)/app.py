#app.py
from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2 
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime
#from tasks import generar_datos_parametros
import json
import time

#Nuevas importaciones para mandar correo de confirmacion de registro
from flask import Flask
from flask_mail import Mail


app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'loverslettuce@gmail.com'
app.config['MAIL_PASSWORD'] = 'xdqt fogx wskz hzzv'

mail = Mail(app)

 
conn = psycopg2.connect(host="jelani.db.elephantsql.com",
                        database="fygsjtmb",
                        user="fygsjtmb",
                        password="mhqTJ1XBfKHqXfE5i_FAk76kusx-Wozd")


def check_password_strength(password):
    
  digit_pattern = r"\d"
  symbol_pattern = r"[!@#$%^&*()_+\-={}\|;:'\",<.>/?]"
  uppercase_pattern = r"[A-Z]"
  lowercase_pattern = r"[a-z]"

  if len(password) < 8:
    return False

  num_digits = sum(1 for char in password if re.match(digit_pattern, char))
  num_symbols = sum(1 for char in password if re.match(symbol_pattern, char))
  num_uppercase = sum(1 for char in password if re.match(uppercase_pattern, char))
  num_lowercase = sum(1 for char in password if re.match(lowercase_pattern, char))

  return num_digits >= 2 and num_symbols >= 1 and num_uppercase >= 1 and num_lowercase >= 1

def validate_email(email):
    """
    Función para validar direcciones de correo electrónico utilizando expresiones regulares.

    Args:
    - email (str): Dirección de correo electrónico a validar.

    Returns:
    - bool: True si la dirección de correo electrónico es válida, False de lo contrario.
    """
    # Patrón de expresión regular para validar direcciones de correo electrónico
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Comprobación de la dirección de correo electrónico con el patrón
    if re.match(email_pattern, email):
        return True
    else:
        return False
    
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario, asunto, mensaje):
    # Verificar si se proporcionaron datos válidos
    if not destinatario or not asunto or not mensaje:
        return False  # Datos incorrectos o faltantes, no se realiza ninguna acción

    # Configuración del servidor SMTP
    servidor_smtp = 'smtp.example.com'
    puerto = 587
    usuario = 'tu_correo@example.com'
    contraseña = 'tu_contraseña'

    # Crear mensaje
    msg = MIMEMultipart()
    msg['From'] = usuario
    msg['To'] = destinatario
    msg['Subject'] = asunto

    # Añadir cuerpo del mensaje
    msg.attach(MIMEText(mensaje, 'plain'))

    # Iniciar sesión en el servidor SMTP
    servidor = smtplib.SMTP(servidor_smtp, puerto)
    servidor.starttls()
    servidor.login(usuario, contraseña)

    # Enviar correo electrónico
    servidor.send_message(msg)

    # Cerrar conexión
    servidor.quit()

    return True  # Correo electrónico enviado correctamente

    
@app.route('/')
def home():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
 
 
@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)
 
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result

        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                session['id_rol'] = account['id_rol']
                email = account['email']  # Retrieve email from the database

                if account['id_rol'] == 1:
                    # Redirect to admin view
                    return redirect(url_for('admin_view'))
                else:
                     # Continue to home page for non-admin roles
                    # Send confirmation email
                    msg = Message('Inicio de sesión', sender='your-email@example.com', recipients=[email])
                    msg.body = f'Hola {account["username"]},\n\nHas iniciado sesión con éxito en nuestro sitio web!'
                    mail.send(msg)

                    session['email'] = account['email']
                
                    # Continue to home page for non-admin roles
                    return redirect(url_for('home'))

            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')
 
    return render_template('login.html')
  
#nuevo para correos 
from flask_mail import Message

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    
        _hashed_password = generate_password_hash(password)
 
        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
                                                                       #MANUELITA WAS HERE
        if not username or not password or not email:
            flash('Please fill out the form!')
        elif account:
            # flash('Account already exists!')
            flash('Account already exists!', category='danger')

        #AÑADIDO
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not check_password_strength(password):
            flash('Password does not meet security requirements!', category='danger') 
            flash ('-Minimum length: 8 characters       -Minimum numeric characters: 2      -Minimum symbols: 1         -Minimum uppercase letters: 1       -Minimum lowercase letters: 1', category='danger')  # Updated message
        
        elif not username or not password or not email:
            flash('Please fill out the form!', category='danger')
        #AÑADIDO
    
        elif not re.match(r'^[A-Za-z0-9\s]+$', username):
            flash('Username must contain only characters, numbers, and spaces!', category='danger')


        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)", (fullname, username, _hashed_password, email))
            conn.commit()

             #nuevo para correos 
             # Set registration_successful to True after successful registration
            registration_successful = True
            # Send confirmation email
            msg = Message('Confirmacion de Creacion de Usuario', sender='your-email@example.com', recipients=[email])
            msg.body = f'Hola {fullname},\n\nTe has registrado con exito en nuestro website!'
            mail.send(msg)


            #print('New user registered successfully!')
            flash('You have successfully registered!', 'success') #MANUELITA ESTUVO AQUI
            return render_template('login.html')

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')
   
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))
  

@app.route('/profile')
def profile(): 
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
   
    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/admin_view', methods=["GET", "POST"])
def admin_view():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if 'loggedin' in session:
        if request.method == "GET":
            # Si la solicitud es GET, muestra la vista administrativa
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            return render_template("admin_view.html", rows=rows ,admin_view=True)
        
        elif request.method == "POST":
            edited_data = request.form
            
            # Obtener datos del formulario
            username = edited_data['username']
            email = edited_data['email']
            id_rol = edited_data['id_rol']
            
            # Actualizar en la base de datos
            cur.execute("UPDATE users SET email = %s, id_rol = %s WHERE username = %s", (email, id_rol, username))
            conn.commit()
            
            flash("Base de datos actualizada exitosamente", "success")

        
            
        return redirect(url_for('admin_view'))  # Redirige de vuelta a la vista administrativa después de editar
    else:
        # Manejo de sesión no iniciada, redirigir o manejar de alguna manera
        # Por ejemplo, podrías redirigir al usuario a la página de inicio de sesión
        return redirect(url_for('login'))
    



@app.route('/delete_btn', methods=["GET", "POST"])
def delete():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if 'loggedin' in session:
        if request.method == "GET":
            # Si la solicitud es GET, muestra la vista administrativa
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            return render_template("admin_view.html", rows=rows)
        
        elif request.method == "POST":



                           # Si se presionó el botón de eliminación
                username_to_delete = request.form['username']
                
                # Eliminar el registro de la base de datos
                cur.execute("DELETE FROM users WHERE username = %s", (username_to_delete,))
                conn.commit()
                
                flash("Registro eliminado exitosamente", "success")
                return redirect(url_for('admin_view'))  # Redirige de vuelta a la vista administrativa después de eliminar
        
            
        return redirect(url_for('admin_view'))  # Redirige de vuelta a la vista administrativa después de editar
    else:
        # Manejo de sesión no iniciada, redirigir o manejar de alguna manera
        # Por ejemplo, podrías redirigir al usuario a la página de inicio de sesión
        return redirect(url_for('login'))
    



# _______CULTIVO____________
from psycopg2 import sql
import re

@app.route('/crear_cultivo', methods=['GET', 'POST'])
def crear_cultivo():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nombre_cultivo = request.form['nombre_cultivo']
        tipo_cultivo = request.form['tipo_cultivo']
        ubicacion_cultivo = request.form['ubicacion_cultivo']
        id_sensor = request.form['id_sensor']
        id_usuario = session['id']  # Esta función debería obtener el ID del usuario actualmente logueado

        # Verifica si 'id' y 'email' están en la sesión
        if 'id' in session and 'email' in session:
            id_usuario = session['id']
            email = session['email']  # Recupera el correo electrónico de la sesión
        else:
            flash('Inicia sesión para crear un cultivo', 'error')
            return redirect(url_for('login'))  # Redirige al usuario al inicio de sesión si no está autenticado
        
        cursor = conn.cursor()


        # Insertar los datos en la tabla 'cultivos'
        cursor.execute("INSERT INTO cultivos (nombre_cultivo, tipo_cultivo, ubicacion_cultivo,id_sensor, id_usuario) VALUES (%s, %s, %s, %s,%s) RETURNING id_cultivo", (nombre_cultivo, tipo_cultivo, ubicacion_cultivo,id_sensor ,id_usuario))
        id_cultivo = cursor.fetchone()[0]

         # Limpiar el identificador del sensor para que sea válido como nombre de tabla en SQL
        id_sensor_cleaned = re.sub(r'\W+', '_', id_sensor)

        sql_create_table = """
        CREATE TABLE IF NOT EXISTS {} (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP NOT NULL,
            temperatura INT NOT NULL,
            ph INT NOT NULL,
            presion INT NOT NULL,
            humedad INT NOT NULL,
            sustrato INT NOT NULL,
            electroresistencia INT NOT NULL
        );
        """.format(id_sensor_cleaned)
        cursor.execute(sql_create_table)  # Ejecutar la consulta para crear la tabla del sensor

    
        #nuevo para correos 
        # Set registration_successful to True after successful registration
        cultvio_successful = True
        # Send confirmation email
        msg = Message('Creacion de Cultivo', sender='your-email@example.com', recipients=[email])
        msg.body = f'Se ha creado el cultivo "{nombre_cultivo}"'
        mail.send(msg)

        conn.commit()
        cursor.close()

        
        return render_template('home.html')
    
    return render_template('crear_cultivo.html')



@app.route('/mis_cultivos')
def mis_cultivos():

    id_usuario = session['id']  # Obtener el ID del usuario actualmente logueado

    cursor = conn.cursor()
    # Consultar los cultivos del usuario actual
    cursor.execute("SELECT * FROM cultivos WHERE id_usuario = %s", (id_usuario,))
    cultivos = cursor.fetchall()
    cursor.close()


    return render_template('mis_cultivos.html', cultivos=cultivos)

@app.route('/eliminar_cultivo/<int:id_cultivo>', methods=['POST'])
def eliminar_cultivo(id_cultivo):

    # Verifica si 'id' y 'email' están en la sesión
    if 'id' in session and 'email' in session:
        id_usuario = session['id']
        email = session['email']  # Recupera el correo electrónico de la sesión

    else:
        flash('Inicia sesión para crear un cultivo', 'error')
        return redirect(url_for('login'))  # Redirige al usuario al inicio de sesión si no está autenticado
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Consulta para obtener el nombre del cultivo antes de eliminarlo
    cursor.execute("SELECT nombre_cultivo FROM cultivos WHERE id_cultivo = %s", (id_cultivo,))
    nombre_cultivo = cursor.fetchone()[0]  # Obtiene el nombre del cultivo



    cursor.execute("Delete FROM cultivos WHERE id_cultivo = %s", (id_cultivo,))
    print("Registro eliminado exitosamente")

    cultviodelete_successful = True
    # Send confirmation email
    msg = Message('Eliminacion de Cultivo', sender='your-email@example.com', recipients=[email])
    msg.body = f'Se a eliminado el cultivo "{nombre_cultivo}" '
    mail.send(msg)
    

    return redirect(url_for('mis_cultivos'))




import datetime

@app.route('/ver_datos_cultivo/<int:id_cultivo>', methods=['GET', 'POST'])
def ver_datos_cultivo(id_cultivo):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Obtener el ID del sensor asociado al cultivo
    cursor.execute("SELECT id_sensor FROM cultivos WHERE id_cultivo = %s", (id_cultivo,))
    id_sensor = cursor.fetchone()[0]

    # Construir la consulta SQL para seleccionar los datos del sensor asociado
    tabla_sensor = str(id_sensor)
    
    # Obtener la fecha actual
    fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
    
    # Determinar la fecha seleccionada por el usuario
    fecha_seleccionada = request.form.get('fecha')

    # Establecer la fecha a utilizar en la consulta (usar la fecha seleccionada si está disponible, de lo contrario, usar la fecha actual)
    fecha_consulta = fecha_seleccionada if fecha_seleccionada else fecha_actual
    
    # Consulta SQL para seleccionar los datos correspondientes a la fecha seleccionada
    sql_select_data = f"SELECT fecha, temperatura, ph, presion, humedad, sustrato, electroresistencia FROM {tabla_sensor} WHERE DATE(fecha) = '{fecha_consulta}'"

    # Verificar si se envió un formulario y aplicar el filtro correspondiente
    if request.method == 'POST':
        fecha = request.form.get('fecha')
        mes = request.form.get('mes')
        if fecha:
            # Consulta SQL para obtener datos para una fecha específica
            sql_select_data = f"""
                SELECT fecha, temperatura, ph, presion, humedad, sustrato, electroresistencia 
                FROM {tabla_sensor} 
                WHERE DATE(fecha) = '{fecha}'
            """
        elif mes:
            # Consulta SQL para obtener datos para un mes específico
            sql_select_data = f"""
                SELECT DATE(fecha) AS fecha, MAX(temperatura) AS max_temperatura, MIN(temperatura) AS min_temperatura,
                MAX(ph) AS max_ph, MIN(ph) AS min_ph, MAX(presion) AS max_presion, MIN(presion) AS min_presion,
                MAX(humedad) AS max_humedad, MIN(humedad) AS min_humedad, MAX(sustrato) AS max_sustrato, MIN(sustrato) AS min_sustrato,
                MAX(electroresistencia) AS max_electroresistencia, MIN(electroresistencia) AS min_electroresistencia
                FROM {tabla_sensor} 
                WHERE DATE_PART('month', fecha) = {mes}
                GROUP BY DATE(fecha)
            """

    cursor.execute(sql_select_data)
    datos_sensor = cursor.fetchall()
    cursor.close()

    # Determinar el valor predeterminado para el campo de fecha en el formulario
    fecha_predeterminada = fecha_consulta

 
    return render_template('ver_datos_cultivo.html', datos_sensor=datos_sensor, fecha_predeterminada=fecha_predeterminada, id_cultivo=id_cultivo)


# ARCHIVO PLANO
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import os

@app.route('/analisis_cultivo/<int:id_cultivo>', methods=['POST'])
def analisis_cultivo(id_cultivo):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Obtener el ID del sensor asociado al cultivo
    cursor.execute("SELECT id_sensor FROM cultivos WHERE id_cultivo = %s", (id_cultivo,))
    id_sensor = cursor.fetchone()[0]

    # Construir la consulta SQL para seleccionar los datos del sensor asociado
    tabla_sensor = str(id_sensor)

    # Obtener el mes seleccionado por el usuario (si se proporciona)
    mes_seleccionado = request.form.get('mes')

    # Consulta SQL para seleccionar los datos correspondientes al mes seleccionado
    if mes_seleccionado:
        sql_select_data = f"""
            SELECT fecha, temperatura, ph, presion, humedad, sustrato, electroresistencia 
            FROM {tabla_sensor} 
            WHERE DATE_PART('month', fecha) = {mes_seleccionado}
        """
    else:
        # Si no se proporciona un mes, se asume el mes actual
        fecha_actual = datetime.date.today().strftime("%Y-%m-%d")
        sql_select_data = f"""
            SELECT fecha, temperatura, ph, presion, humedad, sustrato, electroresistencia 
            FROM {tabla_sensor} 
            WHERE DATE(fecha) = '{fecha_actual}'
        """

    cursor.execute(sql_select_data)
    datos_sensor = cursor.fetchall()
    cursor.close()

    # Verificar si se encontraron datos para el mes seleccionado
    if datos_sensor:
        # Nombre del archivo PDF
        nombre_archivo = f"analisis_cultivo_{id_cultivo}.pdf"

        # Ruta donde se guardará el archivo
        directorio_pdf = "archivos_pdf"
        ruta_archivo = os.path.join(directorio_pdf, nombre_archivo)

        # Crear el directorio si no existe
        if not os.path.exists(directorio_pdf):
            os.makedirs(directorio_pdf)

        # Crear el archivo PDF
        c = canvas.Canvas(ruta_archivo, pagesize=letter)
        y = 750
        for dato in datos_sensor:
            for i, valor in enumerate(dato):
                c.drawString(100, y, f"{valor}")
                y -= 20
            y -= 20  # Espacio entre cada conjunto de datos
        c.save()

        # Devolver una respuesta indicando que el archivo se ha guardado
        return f"El archivo PDF se ha guardado en {ruta_archivo}"
    else:
        # Si no se encontraron datos para el mes seleccionado, devolver un mensaje de error
        return "No hay datos disponibles para el mes seleccionado."




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
