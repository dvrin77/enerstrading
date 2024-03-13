import telebot
import threading
import tkinter as tk
from tkinter import filedialog
import os
import time

# Variable para almacenar el contenido anterior del archivo
contenido_anterior = ""
contenido_lock = threading.Event()

# Función para enviar el contenido al bot de Telegram solo si hay cambios
def enviar_contenido():
    global contenido_anterior
    # Obtenemos el token, chat_id y la ruta del archivo desde la interfaz
    token = token_entry.get()
    chat_id = chat_id_entry.get()
    ruta_archivo = ruta_archivo_entry.get()
    # Creamos una instancia del bot de Telegram usando telebot
    bot = telebot.TeleBot(token)

    # Función que se ejecutará en el hilo para enviar contenido solo si hay cambios
    def enviar_contenido_con_cambios():
        global contenido_anterior
        while True:
            try:
                # Leemos el contenido actual del archivo si la ruta es válida
                if os.path.exists(ruta_archivo):
                    with open(ruta_archivo, "r") as file:
                        contenido_actual = file.read()
                    # Comparamos el contenido actual con el contenido anterior
                    if contenido_actual != contenido_anterior:
                        # Enviamos el contenido del archivo a Telegram
                        bot.send_message(chat_id, contenido_actual)
                        # Actualizamos el contenido anterior
                        contenido_anterior = contenido_actual
                # Esperamos a que se produzca algún cambio en el archivo
                contenido_lock.wait()
            except Exception as e:
                print(f"Error: {e}")
                # Reiniciamos el hilo en caso de error
                threading.Thread(target=enviar_contenido_con_cambios, daemon=True).start()
                break

    # Iniciamos el hilo para enviar contenido solo si hay cambios
    threading.Thread(target=enviar_contenido_con_cambios, daemon=True).start()

# Función para monitorear cambios en el archivo
def monitorear_cambios():
    global contenido_anterior
    while True:
        # Obtenemos la ruta del archivo desde la interfaz
        ruta_archivo = ruta_archivo_entry.get()
        # Verificamos si la ruta del archivo es válida
        if os.path.exists(ruta_archivo):
            with open(ruta_archivo, "r") as file:
                contenido_actual = file.read()
            # Comparamos el contenido actual con el contenido anterior
            if contenido_actual != contenido_anterior:
                # Actualizamos el contenido anterior
                contenido_anterior = contenido_actual
                contenido_lock.set()  # Despierta al hilo de enviar_contenido_con_cambios
        # Esperamos antes de volver a verificar cambios
        time.sleep(1)

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Bot de Telegram")

# Campos para especificar token, chat_id y ruta del archivo
tk.Label(root, text="Token del bot:").pack()
token_entry = tk.Entry(root)
token_entry.pack()
tk.Label(root, text="Chat ID:").pack()
chat_id_entry = tk.Entry(root)
chat_id_entry.pack()
tk.Label(root, text="Ruta del archivo:").pack()
ruta_archivo_entry = tk.Entry(root)
ruta_archivo_entry.pack()

# Botón para seleccionar el archivo de texto
def seleccionar_archivo():
    ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
    ruta_archivo_entry.delete(0, tk.END)
    ruta_archivo_entry.insert(0, ruta)
    contenido_lock.set()  # Despierta al hilo de enviar_contenido_con_cambios

tk.Button(root, text="Seleccionar archivo", command=seleccionar_archivo).pack()

# Botón para iniciar el envío solo si hay cambios
tk.Button(root, text="Enviar contenido", command=enviar_contenido).pack()

# Iniciar el hilo para monitorear cambios en el archivo
threading.Thread(target=monitorear_cambios, daemon=True).start()

# Iniciar la interfaz gráfica
root.mainloop()
