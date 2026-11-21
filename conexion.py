import psycopg2
DB_CONFIG = {
    "dbname": "northwind_2", #nuestra bd
    "user": "postgres",
    "password": "postgres",  # ponemos nuestra contraseña si tenemos
    "host": "127.0.0.1",
    "port": "5432",
    "client_encoding":"utf8" 
}

def obtener_conexion():
    return psycopg2.connect(**DB_CONFIG)