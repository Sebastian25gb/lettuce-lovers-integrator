import unittest
from app import app, conn

class TestApp(unittest.TestCase):

    def setUp(self):
        # Configurar un cliente de prueba para interactuar con la aplicación
        self.app = app.test_client()
        # Crear una tabla temporal para pruebas en la base de datos
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR)")
            conn.commit()

    def tearDown(self):
        # Eliminar la tabla temporal de la base de datos después de cada prueba
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS test_table")
            conn.commit()

    def test_home_route(self):
        # Prueba para la ruta principal '/'
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_login_route(self):
        # Prueba para la ruta de inicio de sesión '/login'
        response = self.app.post('/login', data=dict(username='test_user', password='test_password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully logged in', response.data)

    # Agregar más pruebas para otras rutas y funcionalidades de tu aplicación

if __name__ == '__main__':
    unittest.main()
