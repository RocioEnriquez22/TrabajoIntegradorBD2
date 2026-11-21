import psycopg2

DB_CONFIG = {
    "dbname": "northwind", #nuestra bd
    "user": "postgres",
    "password": "1234",  # ponemos nuestra contraseña si tenemos
    "host": "127.0.0.1",
    "port": "5432", 
}

def obtener_conexion():
    return psycopg2.connect(**DB_CONFIG)