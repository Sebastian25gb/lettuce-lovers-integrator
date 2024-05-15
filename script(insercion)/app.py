import random
from datetime import datetime
import psycopg2
import time

def obtener_conexion():
    try:
        conn = psycopg2.connect(
            dbname="dump-vovdberw-202405031600",
            user="postgres",
            password="1",
            host="localhost"
        )
        print("Conexion de PostgreSQL exitosa")
        return conn
    except psycopg2.Error as e:
        print("Error de PostgreSQL al conectar:", e)
        return None

def insertar_sensor_data():
    try:
        opciones_tablas = ['a1234', 'b1234', 'c1234','d1234']
        
        for nombre_sensor in opciones_tablas:
            conn = obtener_conexion()
            if conn is None:
                continue
            
            try:
                temperatura = random.randint(-20, 50)
                ph = random.randint(0, 14)
                presion = random.randint(0, 1000)
                humedad = random.randint(0, 100)
                sustrato = random.randint(0, 100)
                electroresistencia = random.randint(-50, 100)
                fecha_actual = datetime.now()

                cur = conn.cursor()
                sql_insert = "INSERT INTO {} (fecha, temperatura, ph, presion, humedad, sustrato, electroresistencia) VALUES (%s, %s, %s, %s, %s, %s, %s)".format(nombre_sensor)
                parametros = (fecha_actual, temperatura, ph, presion, humedad, sustrato, electroresistencia)
                cur.execute(sql_insert, parametros)
                conn.commit()
                cur.close()
                conn.close()

                print("Datos del sensor insertados correctamente en la tabla {}.".format(nombre_sensor))
            except psycopg2.Error as e:
                print("Error de PostgreSQL:", e)
                print("La tabla {} no existe.".format(nombre_sensor))
            except Exception as error:
                print("Error al insertar datos del sensor:", error)

    except psycopg2.Error as e:
        print("Error de PostgreSQL:", e)
    except Exception as error:
        print("Error al insertar datos del sensor:", error)
        
def insercion_periodica():
    while True:
        insertar_sensor_data()
        time.sleep(60)



# Ejemplo de uso
# insertar_sensor_data()
insercion_periodica()
