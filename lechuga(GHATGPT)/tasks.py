# tasks.py
import time
import random
import json
from celery import Celery
from flask import Flask
import psycopg2
from redis import Redis


app = Flask(__name__)

# Configura la conexión con la base de datos
conn = psycopg2.connect(
            host="rosie.db.elephantsql.com",
            database="vovdberw",
            user="vovdberw",
            password="6lu7q2yx-SeiyA6Nap0ikjQQXm-LEaA1")

# Crea una instancia de Celery
celery = Celery(
    app.name,
    backend='redis://localhost/0',
    broker='redis://localhost/0'
)

@celery.task
def generar_datos_parametros(id_cultivo):
    # Generar y insertar datos de parámetros en la tabla
    mes = 1
    semana = 1
    semanas_completadas = 0

    cursor = conn.cursor()

    while True:
        # Generar datos aleatorios para la semana actual
        temperatura = [random.randint(20, 40) for _ in range(7)]
        presion = [random.randint(900, 1100) for _ in range(7)]
        humedad = [random.randint(30, 80) for _ in range(7)]
        oxigenacion = [random.randint(10, 25) for _ in range(7)]

        # Datos a ser almacenados como JSON en la tabla parametros_cultivo_<id_cultivo>
        temperatura_json = json.dumps(temperatura)
        presion_json = json.dumps(presion)
        humedad_json = json.dumps(humedad)
        oxigenacion_json = json.dumps(oxigenacion)

        # Insertar los datos en la tabla
        insert_query = """
            INSERT INTO parametros_cultivo_{} (semana, mes, temperatura, presion, humedad, oxigenacion)
            VALUES (%s, %s, %s, %s, %s, %s);
        """.format(id_cultivo)
        cursor.execute(insert_query, (semana, mes, temperatura_json, presion_json, humedad_json, oxigenacion_json))
        conn.commit()

        # Incrementar la semana y actualizar el contador de semanas completadas
        semana = (semana + 1) % 5
        semanas_completadas += 1

        # Verificar si se han completado 4 semanas para el mes actual
        if semanas_completadas == 4:
            # Si se completan 4 semanas, pasar al siguiente mes y restablecer la semana a 1
            mes += 1
            semanas_completadas = 0
            semana = 1  # Iniciar la semana en 1 para el nuevo mes

        if mes >= 13:
            break

        # Esperar 5 segundos
        time.sleep(5)

    cursor.close()
