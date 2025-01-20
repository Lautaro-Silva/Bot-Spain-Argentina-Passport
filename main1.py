import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

# URL de la página y configuración de Telegram
URL = "https://www.cgeonline.com.ar/informacion/apertura-de-citas.html"
TELEGRAM_TOKEN = "7815426031:AAHyH7NA4THnEo3AKoT_llR9Bjf9ZlNd6ic"
CHAT_ID = "1773852782"

# Archivo para guardar las fechas anteriores y la última notificación
DATA_FILE = "datos_pagina.json"


def enviar_mensaje_telegram(mensaje):
    """Envia un mensaje a través de Telegram."""
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        requests.post(url_telegram, data=params)
    except Exception as e:
        print(f"Error al enviar mensaje por Telegram: {e}")


def obtener_fechas_pasaportes():
    try:
        # Make the HTTP request
        response = requests.get(URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table inside the 'table-responsive-sm' div
        tabla = soup.find("div", class_="table-responsive-sm").find("table")
        if not tabla:
            raise ValueError("No se encontró la tabla dentro de 'table-responsive-sm'.")

        # Loop through all rows to find the 'Pasaportes' row with the correct text
        fila_pasaportes = None
        for fila in tabla.find_all("tr"):
            columnas = fila.find_all("td")
            # Ensure we are looking at the correct row because there are multiple with the name Pasaportes
            if columnas and "Pasaportes" in columnas[0].get_text(strip=True) and "renovación y primera vez" in columnas[0].get_text(strip=True):
                fila_pasaportes = fila
                break

        if not fila_pasaportes:
            raise ValueError("No se encontró la fila del servicio de pasaportes.")

        # Extract the last and next opening dates
        columnas = fila_pasaportes.find_all("td")
        if len(columnas) < 3:
            raise ValueError("La fila de pasaportes no contiene las columnas esperadas.")

        ultima_apertura = columnas[1].get_text(strip=True)
        proxima_apertura = columnas[2].get_text(strip=True)

        # Print the extracted dates (for debugging)
        print(f"Última apertura: {ultima_apertura}")
        print(f"Próxima apertura: {proxima_apertura}")

        return ultima_apertura, proxima_apertura

    except Exception as e:
        print(f"Error al obtener las fechas de pasaportes: {e}")
        return None, None



def leer_datos_anteriores():
    """Lee los datos guardados anteriormente de las fechas y la última notificación."""
    try:
        with open(DATA_FILE, "r") as archivo:
            datos = json.load(archivo)
            # Verificar que todas las claves necesarias existan
            if "ultima_apertura" not in datos:
                datos["ultima_apertura"] = ""
            if "proxima_apertura" not in datos:
                datos["proxima_apertura"] = ""
            if "ultima_notificacion" not in datos:
                datos["ultima_notificacion"] = ""  # Valor por defecto
            return datos
    except FileNotFoundError:
        # Si el archivo no existe, devolver datos iniciales vacíos
        return {"ultima_apertura": "", "proxima_apertura": "", "ultima_notificacion": ""}



def guardar_datos(ultima_apertura, proxima_apertura, ultima_notificacion):
    """Guarda las fechas actuales y la última notificación en un archivo, como un registro."""
    # Check if the file exists
    if os.path.exists(DATA_FILE):
        # Load the existing data if the file exists
        with open(DATA_FILE, "r") as archivo:
            try:
                data = json.load(archivo)
            except json.JSONDecodeError:
                data = []  # If the file is empty or corrupted, start with an empty list
    else:
        # If the file does not exist, start with an empty list
        data = []

    # Create a new entry with the current data
    nueva_entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp for when the data is saved
        "ultima_apertura": ultima_apertura,
        "proxima_apertura": proxima_apertura,
        "ultima_notificacion": ultima_notificacion
    }

    # Append the new entry to the data list
    data.append(nueva_entrada)

    # Save the updated data back to the file
    with open(DATA_FILE, "w") as archivo:
        json.dump(data, archivo, indent=4)


def verificar_cambios():
    """Verifica si las fechas de apertura han cambiado y si deben enviarse notificaciones."""
    ultima_actual, proxima_actual = obtener_fechas_pasaportes()
    if not ultima_actual or not proxima_actual:
        return  # Si hubo un error, salir

    datos_anteriores = leer_datos_anteriores()
    ultima_anterior = datos_anteriores["ultima_apertura"]
    proxima_anterior = datos_anteriores["proxima_apertura"]
    ultima_notificacion = datos_anteriores["ultima_notificacion"]

    # Verificar si las fechas han cambiado
    if proxima_actual != proxima_anterior:
        mensaje = (
            "¡Cambio detectado en las fechas de apertura de citas para pasaportes!\n"
            f"Última apertura: {ultima_actual}\n"
            f"Próxima apertura: {proxima_actual}"
        )
        # Enviar un mensaje inmediatamente cuando se detecte un cambio
        enviar_mensaje_telegram(mensaje)
        print("Notificación enviada por cambio en las fechas de pasaportes.")
        # Actualizar los datos
        guardar_datos(ultima_actual, proxima_actual, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Enviar mensaje diario a las 9:00 AM, independientemente de si hay cambios
    current_time = datetime.now()
    if current_time.hour == 9:
        if proxima_actual != proxima_anterior:
            mensaje_diario = (
                "¡Cambio detectado en las fechas de apertura de citas para pasaportes!\n"
                f"Última apertura: {ultima_actual}\n"
                f"Próxima apertura: {proxima_actual}"
            )
            enviar_mensaje_telegram(mensaje_diario)
            print("Notificación diaria enviada por cambio en las fechas de pasaportes.")
        else:
            mensaje_diario = (
                "No ha habido cambios en las fechas de apertura de citas para pasaportes.\n"
                f"Última apertura: {ultima_actual}\n"
                f"Próxima apertura: {proxima_actual}"
            )
            enviar_mensaje_telegram(mensaje_diario)
            print("No hay cambios detectados en las fechas de pasaportes (notificación diaria).")

        # Actualizar la última notificación
        guardar_datos(ultima_actual, proxima_actual, current_time.strftime("%Y-%m-%d %H:%M:%S"))


# Ejecución continua del programa
if __name__ == "__main__":
    while True:
        verificar_cambios()  # Verificar cambios en las fechas
        print("Esperando 30 minutos para la siguiente verificación...")
        time.sleep(1800)  # Pausa de 30 minutos (1800 segundos)
