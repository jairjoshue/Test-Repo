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

def guardar_json(nombre_archivo, datos):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

# Cargar base de datos
postulantes = cargar_json("postulantes.json")
preguntas_generales = cargar_json("preguntas_generales.json")
puestos = cargar_json("puestos.json")

# Inicializar estado
def iniciar_estado():
    st.session_state["chat_history"] = []
    st.session_state["entrevista_iniciada"] = False
    st.session_state["respuestas_usuario"] = {}
    st.session_state["preguntas_generales"] = []
    st.session_state["preguntas_tecnicas"] = []
    st.session_state["puesto_actual"] = None
    st.session_state["acepto_condiciones"] = False

if "chat_history" not in st.session_state:
    iniciar_estado()

# Función para agregar mensajes al chat
def add_message(role, text):
    st.session_state["chat_history"].append({"role": role, "text": text})

# Mensaje de bienvenida
if not st.session_state["chat_history"]:
    add_message("bot", "👋 ¡Hola! Bienvenido a la entrevista virtual de Minera CHINALCO.")
    add_message("bot", "Para esta prueba, puedes usar los siguientes credenciales:")
    for p in postulantes:
        add_message("bot", f"- Nombre: {p['nombre']}, Documento: {p['documento']}")
    add_message("bot", "Por favor, ingresa tu nombre tal como está registrado.")

# Renderizar historial de chat
st.markdown("<h2>💬 Chat de Entrevista</h2>", unsafe_allow_html=True)
chat_container = st.container()
with chat_container:
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "bot":
            st.markdown(f'<div class="bot-message">🤖 {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-message">👤 {msg["text"]}</div>', unsafe_allow_html=True)

# Entrada de texto
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Escribe tu respuesta aquí:")
    submit_button = st.form_submit_button("Enviar Respuesta")

# Procesar la entrada del usuario
if submit_button and user_input:
    add_message("user", user_input)
    
    # Solicitar documento después del nombre
    if "nombre_postulante" not in st.session_state:
        st.session_state["nombre_postulante"] = user_input
        add_message("bot", "Gracias. Ahora ingresa tu número de documento.")
    
    elif "documento_postulante" not in st.session_state:
        postulante = next((p for p in postulantes if p["documento"] == user_input), None)
        if postulante:
            st.session_state["documento_postulante"] = user_input
            st.session_state["puesto_actual"] = postulante["codigo_puesto"]
            add_message("bot", f"¡Bienvenido {postulante['nombre']}! Estás postulando para {puestos[postulante['codigo_puesto']]['nombre']}")
            add_message("bot", "Antes de continuar, acepta los términos de la entrevista.")
            if st.button("✅ Acepto los términos"):
                st.session_state["acepto_condiciones"] = True
                add_message("bot", "¡Gracias! Iniciemos la entrevista.")
        else:
            add_message("bot", "Tu documento no está registrado. Contacta a inforrhh@chinalco.com.pe.")
    
    # Iniciar preguntas
    if st.session_state.get("acepto_condiciones"):
        if not st.session_state["preguntas_generales"]:
            st.session_state["preguntas_generales"] = list(preguntas_generales.items())
        if st.session_state["preguntas_generales"]:
            pregunta, respuesta_esperada = st.session_state["preguntas_generales"].pop(0)
            add_message("bot", pregunta)
            st.session_state["respuestas_usuario"][pregunta] = {"respuesta": user_input, "esperada": respuesta_esperada}
        elif not st.session_state["preguntas_tecnicas"]:
            puesto = puestos[st.session_state["puesto_actual"]]
            st.session_state["preguntas_tecnicas"] = list(puesto["preguntas"].items())
        elif st.session_state["preguntas_tecnicas"]:
            pregunta, respuesta_esperada = st.session_state["preguntas_tecnicas"].pop(0)
            add_message("bot", pregunta)
            st.session_state["respuestas_usuario"][pregunta] = {"respuesta": user_input, "esperada": respuesta_esperada}
    
    # Finalización
    if not st.session_state["preguntas_generales"] and not st.session_state["preguntas_tecnicas"]:
        add_message("bot", "¡Gracias por completar la entrevista! Tus respuestas serán enviadas a Recursos Humanos.")
        entrevista_id = random.randint(1000, 9999)
        add_message("bot", f"Tu número de entrevista es: {entrevista_id}")
        guardar_json("historial.json", st.session_state["respuestas_usuario"])
        iniciar_estado()
    
    st.rerun()
