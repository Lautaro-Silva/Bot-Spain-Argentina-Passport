import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os

# Archivo de configuración con las credenciales
CONFIG_FILE = "config.json"
DATA_FILE = "datos_pagina.json"

def cargar_configuracion(config_file):
    try:
        with open(config_file, "r") as archivo_config:
            return json.load(archivo_config)
    except FileNotFoundError:
        print(f"Error: El archivo {config_file} no se encuentra.")
    except json.JSONDecodeError:
        print("Error: El archivo de configuración no tiene un formato válido.")
    return None

def enviar_mensaje_telegram(token, chat_id, mensaje):
    """Envía un mensaje a través de Telegram."""
    url_telegram = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": mensaje}
    try:
        requests.post(url_telegram, data=params)
    except requests.RequestException as e:
        print(f"Error al enviar mensaje por Telegram: {e}")

def obtener_fila_pasaportes(tabla):
    for fila in tabla.find_all("tr"):
        columnas = fila.find_all("td")
        if columnas and "Pasaportes" in columnas[0].get_text(strip=True) and "renovación y primera vez" in columnas[0].get_text(strip=True):
            return fila
    return None

def obtener_fechas_pasaportes(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        tabla = soup.find("div", class_="table-responsive-sm").find("table")
        if not tabla:
            raise ValueError("No se encontró la tabla dentro de 'table-responsive-sm'.")
        fila_pasaportes = obtener_fila_pasaportes(tabla)
        if not fila_pasaportes:
            raise ValueError("No se encontró la fila del servicio de pasaportes.")
        columnas = fila_pasaportes.find_all("td")
        if len(columnas) < 3:
            raise ValueError("La fila de pasaportes no contiene las columnas esperadas.")
        return columnas[1].get_text(strip=True), columnas[2].get_text(strip=True)
    except requests.RequestException as e:
        print(f"Error al obtener las fechas de pasaportes: {e}")
    return None, None

def leer_datos_anteriores(data_file):
    """Lee los datos guardados anteriormente de las fechas y la última notificación."""
    try:
        with open(data_file, "r") as archivo:
            datos = json.load(archivo)
            if "ultima_apertura" not in datos:
                datos["ultima_apertura"] = ""
            if "proxima_apertura" not in datos:
                datos["proxima_apertura"] = ""
            if "ultima_notificacion" not in datos:
                datos["ultima_notificacion"] = ""  # Valor por defecto
            return datos
    except FileNotFoundError:
        return {"ultima_apertura": "", "proxima_apertura": "", "ultima_notificacion": ""}

def guardar_datos(data_file, ultima_apertura, proxima_apertura, ultima_notificacion):
    """Guarda las fechas actuales y la última notificación en un archivo, como un registro."""
    if os.path.exists(data_file):
        with open(data_file, "r") as archivo:
            try:
                data = json.load(archivo)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    nueva_entrada = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ultima_apertura": ultima_apertura,
        "proxima_apertura": proxima_apertura,
        "ultima_notificacion": ultima_notificacion
    }

    data.append(nueva_entrada)

    with open(data_file, "w") as archivo:
        json.dump(data, archivo, indent=4)

def verificar_cambios(url, token, chat_id, data_file):
    """Verifica si las fechas de apertura han cambiado y si deben enviarse notificaciones."""
    ultima_actual, proxima_actual = obtener_fechas_pasaportes(url)
    if not ultima_actual or not proxima_actual:
        return

    datos_anteriores = leer_datos_anteriores(data_file)
    ultima_anterior = datos_anteriores["ultima_apertura"]
    proxima_anterior = datos_anteriores["proxima_apertura"]
    ultima_notificacion = datos_anteriores["ultima_notificacion"]

    if proxima_actual != proxima_anterior:
        mensaje = (
            "¡Cambio detectado en las fechas de apertura de citas para pasaportes!\n"
            f"Última apertura: {ultima_actual}\n"
            f"Próxima apertura: {proxima_actual}"
        )
        enviar_mensaje_telegram(token, chat_id, mensaje)
        print("Notificación enviada por cambio en las fechas de pasaportes.")
        guardar_datos(data_file, ultima_actual, proxima_actual, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    current_time = datetime.now()
    if current_time.hour == 9:
        if proxima_actual != proxima_anterior:
            mensaje_diario = (
                "¡Cambio detectado en las fechas de apertura de citas para pasaportes!\n"
                f"Última apertura: {ultima_actual}\n"
                f"Próxima apertura: {proxima_actual}"
            )
            enviar_mensaje_telegram(token, chat_id, mensaje_diario)
            print("Notificación diaria enviada por cambio en las fechas de pasaportes.")
        else:
            mensaje_diario = (
                "No ha habido cambios en las fechas de apertura de citas para pasaportes.\n"
                f"Última apertura: {ultima_actual}\n"
                f"Próxima apertura: {proxima_actual}"
            )
            enviar_mensaje_telegram(token, chat_id, mensaje_diario)
            print("No hay cambios detectados en las fechas de pasaportes (notificación diaria).")

        guardar_datos(data_file, ultima_actual, proxima_actual, current_time.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    config = cargar_configuracion(CONFIG_FILE)
    if config is None:
        raise Exception("No se pudo cargar la configuración. Abortando ejecución.")

    URL = config["URL"]
    TELEGRAM_TOKEN = config["TELEGRAM_TOKEN"]
    CHAT_ID = config["CHAT_ID"]

    while True:
        verificar_cambios(URL, TELEGRAM_TOKEN, CHAT_ID, DATA_FILE)
        print("Esperando 30 minutos para la siguiente verificación...")
        time.sleep(1800)  # Pausa de 30 minutos (1800 segundos)
