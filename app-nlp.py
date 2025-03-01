import streamlit as st
import google.generativeai as genai
import json
import os
import random
import time
from datetime import datetime

# Configurar la API de Gemini
# Configurar la API de Gemini
API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Cargar datos desde archivos JSON
def cargar_json(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        return json.load(archivo)

# Guardar datos en archivos JSON
def guardar_json(nombre_archivo, datos):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

# Cargar base de datos
postulantes = cargar_json("postulantes.json")
preguntas_generales_empresa = cargar_json("preguntas_generales.json")
puestos = cargar_json("puestos.json")

# Inicializar historial de chat y variables de estado
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "entrevista_iniciada" not in st.session_state:
    st.session_state["entrevista_iniciada"] = False

if "respuestas_usuario" not in st.session_state:
    st.session_state["respuestas_usuario"] = {}

if "preguntas_generales" not in st.session_state:
    st.session_state["preguntas_generales"] = []

if "preguntas_tecnicas" not in st.session_state:
    st.session_state["preguntas_tecnicas"] = []

if "puesto_actual" not in st.session_state:
    st.session_state["puesto_actual"] = None

# ✅ **Añadir mensaje al historial del chat**
def add_message(role, text):
    st.session_state["chat_history"].append({"role": role, "text": text})

# ✅ **Forzar que el primer mensaje SIEMPRE se muestre**
if not st.session_state["chat_history"]:
    add_message("bot", "👋 ¡Hola! Bienvenido a la entrevista virtual de Minera CHINALCO. Te guiaré en el proceso.")

# ✅ **Renderizar historial de chat ANTES de la caja de texto**
st.markdown("<h2>💬 Chat de Entrevista</h2>", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "bot":
            st.markdown(f'<div class="bot-message">🤖 {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-message">👤 {msg["text"]}</div>', unsafe_allow_html=True)

# ✅ **Caja de texto debe estar debajo del chat**
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Escribe tu respuesta aquí:")
    submit_button = st.form_submit_button("Enviar Respuesta")

# ✅ **Procesar la respuesta y continuar la entrevista**
if submit_button and user_input:
    add_message("user", user_input)

    if not st.session_state.get("nombre_postulante"):
        st.session_state["nombre_postulante"] = user_input
        add_message("bot", f"Gracias {user_input}. Ahora ingresa tu número de documento.")

    elif not st.session_state.get("documento_postulante"):
        postulante = next((p for p in postulantes if p["documento"] == user_input), None)
        if postulante:
            st.session_state["documento_postulante"] = user_input
            st.session_state["puesto_actual"] = postulante["codigo_puesto"]
            add_message("bot", f"¡Bienvenido {postulante['nombre']}! Estás postulando para {puestos[postulante['codigo_puesto']]['nombre']}. Acepta los términos para iniciar la entrevista.")
            st.session_state["entrevista_iniciada"] = True
        else:
            add_message("bot", "Tu documento no está registrado. Contacta a inforrhh@chinalco.com.pe.")

    st.rerun()
