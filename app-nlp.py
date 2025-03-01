import streamlit as st
import google.generativeai as genai
import json
import os
import random
import time
from datetime import datetime

# Configurar la API de Gemini
API_KEY = "TU_API_KEY_AQUI"
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

# Inicializar historial de chat
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

# Función para agregar mensajes al chat
def add_message(role, text):
    st.session_state["chat_history"].append({"role": role, "text": text})

# Parafrasear pregunta con Gemini
def parafrasear_pregunta(pregunta):
    prompt = f"Parafrasea la siguiente pregunta sin cambiar su significado: {pregunta}"
    response = model.generate_content(prompt)
    return response.text.strip() if response else pregunta

# Evaluar respuestas con IA
def evaluar_respuesta(pregunta, respuesta, respuesta_esperada):
    prompt = f"""
    Evalúa la respuesta del candidato en comparación con la respuesta esperada.
    Devuelve una puntuación (1: Correcto, 0.5: Parcialmente Correcto, 0: Incorrecto) y una justificación.
    Pregunta: {pregunta}
    Respuesta del candidato: {respuesta}
    Respuesta esperada: {respuesta_esperada}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# Guardar historial de entrevistas
def guardar_historial():
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    historial = {
        "nombre": st.session_state["nombre_postulante"],
        "documento": st.session_state["documento_postulante"],
        "fecha": fecha_actual,
        "puesto": st.session_state["puesto_actual"],
        "respuestas": st.session_state["respuestas_usuario"]
    }
    guardar_json("historial.json", historial)

# UI de Chatbot
st.markdown("<h2>💬 Chat de Entrevista</h2>", unsafe_allow_html=True)
chat_container = st.container()

# Mostrar historial de chat
with chat_container:
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "bot":
            st.markdown(f'<div class="bot-message">🤖 {msg["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="user-message">👤 {msg["text"]}</div>', unsafe_allow_html=True)

# Proceso de entrevista
if not st.session_state["entrevista_iniciada"]:
    if not st.session_state.get("nombre_postulante"):
        add_message("bot", "Hola, bienvenido a la entrevista virtual de Minera CHINALCO. ¿Cuál es tu nombre completo?")
    else:
        add_message("bot", "Por favor, ingresa tu número de documento de identidad para validar tu postulación.")

elif st.session_state["entrevista_iniciada"]:
    if not st.session_state["preguntas_generales"]:
        for pregunta in preguntas_generales_empresa.keys():
            st.session_state["preguntas_generales"].append(parafrasear_pregunta(pregunta))
    
    if not st.session_state["preguntas_tecnicas"]:
        preguntas_puesto = puestos[st.session_state["puesto_actual"]]["preguntas"]
        preguntas_aleatorias = list(preguntas_puesto.keys())
        random.shuffle(preguntas_aleatorias)
        for pregunta in preguntas_aleatorias:
            st.session_state["preguntas_tecnicas"].append(parafrasear_pregunta(pregunta))

    if st.session_state["preguntas_generales"]:
        pregunta_actual = st.session_state["preguntas_generales"].pop(0)
        add_message("bot", pregunta_actual)

    elif st.session_state["preguntas_tecnicas"]:
        pregunta_actual = st.session_state["preguntas_tecnicas"].pop(0)
        add_message("bot", pregunta_actual)

    else:
        add_message("bot", "La entrevista ha finalizado. Tus respuestas han sido enviadas a Recursos Humanos. ¡Gracias por participar!")
        guardar_historial()
        st.session_state["entrevista_iniciada"] = False

# Captura de texto
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Escribe tu respuesta aquí:")
    submit_button = st.form_submit_button("Enviar Respuesta")

# Procesar respuesta del usuario
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
