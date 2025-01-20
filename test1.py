import requests
from bs4 import BeautifulSoup
import json

# URL de la página y configuración de Telegram
URL = "https://www.cgeonline.com.ar/informacion/apertura-de-citas.html"
TELEGRAM_TOKEN = "7815426031:AAHyH7NA4THnEo3AKoT_llR9Bjf9ZlNd6ic"
CHAT_ID = "1773852782"

# Archivo para guardar las fechas anteriores
DATA_FILE = "datos_pagina.json"


def enviar_mensaje_telegram(mensaje):
    url_telegram = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        requests.post(url_telegram, data=params)
    except Exception as e:
        print(f"Error al enviar mensaje por Telegram: {e}")


def obtener_fechas_pasaportes():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Buscar el div con la clase 'table-responsive-sm' y luego encontrar la tabla
        tabla = soup.find("div", class_="table-responsive-sm").find("table")
        if not tabla:
            raise ValueError("No se encontró la tabla dentro de 'table-responsive-sm'.")

        # Buscar la fila correspondiente al servicio de pasaportes
        fila_pasaportes = None
        for fila in tabla.find_all("tr"):
            columnas = fila.find_all("td")
            if columnas and "Pasaportes" in columnas[0].get_text(strip=True):
                fila_pasaportes = fila
                break

        if not fila_pasaportes:
            raise ValueError("No se encontró la fila del servicio de pasaportes.")

        # Extraer las fechas de la última y próxima apertura
        columnas = fila_pasaportes.find_all("td")
        if len(columnas) < 3:
            raise ValueError("La fila de pasaportes no contiene las columnas esperadas.")

        ultima_apertura = columnas[1].get_text(strip=True)
        proxima_apertura = columnas[2].get_text(strip=True)

        return ultima_apertura, proxima_apertura
    except Exception as e:
        print(f"Error al obtener las fechas de pasaportes: {e}")
        return None, None


def leer_datos_anteriores():
    try:
        with open(DATA_FILE, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return {"ultima_apertura": "", "proxima_apertura": ""}


def guardar_datos(ultima_apertura, proxima_apertura):
    with open(DATA_FILE, "w") as archivo:
        json.dump({"ultima_apertura": ultima_apertura, "proxima_apertura": proxima_apertura}, archivo)


def verificar_cambios():
    ultima_actual, proxima_actual = obtener_fechas_pasaportes()
    if not ultima_actual or not proxima_actual:
        return  # Si hubo un error, salir

    datos_anteriores = leer_datos_anteriores()
    ultima_anterior = datos_anteriores["ultima_apertura"]
    proxima_anterior = datos_anteriores["proxima_apertura"]

    if proxima_actual != proxima_anterior:
        mensaje = (
            "¡Cambio detectado en las fechas de apertura de citas para pasaportes!\n"
            f"Última apertura: {ultima_actual}\n"
            f"Próxima apertura: {proxima_actual}"
        )
        enviar_mensaje_telegram(mensaje)
        print("Notificación enviada por cambio en las fechas de pasaportes.")
        guardar_datos(ultima_actual, proxima_actual)
    else:
        print("No hay cambios detectados en las fechas de pasaportes.")


# Ejecución del programa una sola vez
if __name__ == "__main__":
    verificar_cambios()
