import psycopg2
from tkinter import messagebox
import tkinter as tk

def probar_conexion():
    # Creamos una ventana oculta solo para poder mostrar cuadros de alerta limpios
    ventana_oculta = tk.Tk()
    ventana_oculta.withdraw()

    conexion = None
    try:
        # 1. Intentamos abrir la conexión mediante el driver psycopg2
        conexion = psycopg2.connect(
            dbname="northwind_2",
            user="postgres",
            password="postgres",
            host="127.0.0.1",
            port="5432",
            client_encoding="utf8"
        )
        
        # 2. Creamos un cursor para hacer una consulta rápida de prueba
        cursor = conexion.cursor()
        cursor.execute("SELECT version();")
        version_pg = cursor.fetchone()[0]

        # 3. Si llegamos acá, todo salió perfecto
        messagebox.showinfo(
            "Conexión Exitosa", 
            f"¡Conectado a Northwind con éxito!\n\nMotor detectado:\n{version_pg}"
        )

    except UnicodeDecodeError as ude:
        # Si PostgreSQL envió un mensaje de error en español (con tildes) en formato Windows-1252,
        # lo decodificamos manualmente para poder leer qué nos está diciendo:
        mensaje_real = ude.object.decode("latin-1", errors="replace")
        messagebox.showerror(
            "Error de PostgreSQL (Decodificado)", 
            f"PostgreSQL rechazó la conexión por este motivo:\n\n{mensaje_real}"
        )

    except Exception as error:
        # Si falla la contraseña, el puerto o el servidor está apagado, cae acá
        messagebox.showerror(
            "Error de Conexión", 
            f"No se pudo conectar a PostgreSQL:\n\n{error}"
        )

    finally:
        # 4. Cerramos siempre los recursos por seguridad
        if conexion:
            cursor.close()
            conexion.close()

# Ejecutamos la prueba
if __name__ == "__main__":
    probar_conexion()
