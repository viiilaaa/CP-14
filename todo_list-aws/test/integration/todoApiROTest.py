import os
import unittest
import requests
import pytest

BASE_URL = os.environ.get("BASE_URL")
# BASE_URL = "https://m0qwfec693.execute-api.us-east-1.amazonaws.com/Prod"

@pytest.mark.api
class TestApiReadOnly(unittest.TestCase):
    
    def setUp(self):
        self.assertIsNotNone(BASE_URL, "URL no configurada")
        self.assertTrue(len(BASE_URL) > 8, "URL no configurada")

    def test_api_list_todos(self):
        """Prueba de lectura: Listar todos los elementos"""
        print('\n---------------------------------------')
        print('Starting - Read-Only test: List TODOS')
        
        url = f"{BASE_URL}/todos"
        response = requests.get(url)
        
        print(f'Response status: {response.status_code}')
        
        self.assertEqual(
            response.status_code, 200, f"Error en la petición GET a {url}"
        )
        
        self.assertIsInstance(response.json(), list, "La respuesta debería ser una lista")
        print(f'Items encontrados: {len(response.json())}')
        print('End - Read-Only test: List TODOS')

    def test_api_get_single_todo(self):
        """Prueba de lectura: Obtener el detalle de un elemento existente"""
        print('\n---------------------------------------')
        print('Starting - Read-Only test: Get Single TODO')
        
        list_url = f"{BASE_URL}/todos"
        list_response = requests.get(list_url)
        todos = list_response.json()

        if len(todos) > 0:
            
            first_todo = todos[0]
           
            todo_id = first_todo.get('id') or first_todo.get('ID') 
            
            if todo_id:
                url = f"{BASE_URL}/todos/{todo_id}"
                response = requests.get(url)
                
                print(f'Testing GET for ID: {todo_id}')
                self.assertEqual(
                    response.status_code, 200, f"Error al intentar leer el ID {todo_id}"
                )
                self.assertIn('text', response.json(), "El cuerpo de la respuesta debería contener el campo 'text'")
            else:
                pytest.skip("No se encontró un campo ID en los objetos de la lista para probar el GET individual")
        else:
            
            print("No hay datos en producción para validar un GET individual.")
            pytest.skip("Omitiendo porque no hay registros previos en el entorno.")

        print('End - Read-Only test: Get Single TODO')
