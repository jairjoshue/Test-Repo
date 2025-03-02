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

# 🔹 Funciones para manejar archivos JSON
def cargar_json(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        return json.load(archivo)

def guardar_json(nombre_archivo, datos):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

# 🔹 Cargar datos desde archivos JSON
postulantes = cargar_json("postulantes.json")
preguntas_generales = cargar_json("preguntas_generales.json")
puestos = cargar_json("puestos.json")

# 🔹 Configurar estado inicial
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "esperando_nombre" not in st.session_state:
    st.session_state["esperando_nombre"] = True
if "esperando_documento" not in st.session_state:
    st.session_state["esperando_documento"] = False
if "proceso_activo" not in st.session_state:
    st.session_state["proceso_activo"] = False
if "respuestas_usuario" not in st.session_state:
    st.session_state["respuestas_usuario"] = {}
if "entrevista_id" not in st.session_state:
    st.session_state["entrevista_id"] = f"CH-{random.randint(1000,9999)}"

# 🔹 Función para agregar mensaje al chat
def agregar_mensaje(remitente, mensaje):
    st.session_state["chat_history"].append({"role": remitente, "message": mensaje})

# 🔹 Función para parafrasear preguntas con Gemini
def parafrasear_pregunta(pregunta):
    prompt = f"Reescribe la siguiente pregunta de manera diferente, manteniendo el mismo significado: {pregunta}"
    response = model.generate_content(prompt)
    return response.text.strip()

# 🔹 Evaluar respuestas con IA (verifica coherencia con la esperada)
def evaluar_respuesta(pregunta, respuesta, respuesta_esperada):
    prompt = f"""
    Evalúa la respuesta del candidato comparándola con la respuesta esperada. Devuelve un puntaje (1: Correcto, 0.5: Parcialmente Correcto, 0: Incorrecto) y una breve justificación.
    Pregunta: {pregunta}
    Respuesta del candidato: {respuesta}
    Respuesta esperada: {respuesta_esperada}
    """
    response = model.generate_content(prompt)
    feedback = response.text.strip()

    # Extraer puntaje
    if "1" in feedback:
        puntaje = 1
    elif "0.5" in feedback:
        puntaje = 0.5
    else:
        puntaje = 0

    return {"respuesta_usuario": respuesta, "evaluacion": feedback, "puntaje": puntaje}

# 🔹 Guardar historial de entrevistas
def guardar_historial():
    historial = {
        "id_entrevista": st.session_state["entrevista_id"],
        "nombre": st.session_state["nombre"],
        "documento": st.session_state["documento"],
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "respuestas": st.session_state["respuestas_usuario"]
    }
    historial_json = "historial.json"
    
    if os.path.exists(historial_json):
        with open(historial_json, "r", encoding="utf-8") as file:
            historial_existente = json.load(file)
    else:
        historial_existente = []

    historial_existente.append(historial)

    with open(historial_json, "w", encoding="utf-8") as file:
        json.dump(historial_existente, file, indent=4, ensure_ascii=False)

# 🔹 UI - Chat
st.markdown("<h1>💬 Chat de Entrevista</h1>", unsafe_allow_html=True)

# 🔹 Mostrar historial del chat
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["message"])

# 🔹 Capturar entrada del usuario
user_input = st.text_input("Escribe tu respuesta aquí:", key="user_input")

# 🔹 Procesar la entrada del usuario
if st.button("Enviar Respuesta") or user_input:
    if user_input:
        agregar_mensaje("user", user_input)

        # 🔹 Paso 1: Ingresar Nombre
        if st.session_state["esperando_nombre"]:
            st.session_state["nombre"] = user_input
            st.session_state["esperando_nombre"] = False
            st.session_state["esperando_documento"] = True
            agregar_mensaje("bot", "Ahora ingresa tu documento de identidad.")
        
        # 🔹 Paso 2: Validar Documento
        elif st.session_state["esperando_documento"]:
            documento = user_input
            postulante = next((p for p in postulantes if p["documento"] == documento), None)

            if postulante:
                st.session_state["documento"] = documento
                st.session_state["puesto"] = puestos[postulante["codigo_puesto"]]
                st.session_state["esperando_documento"] = False
                st.session_state["proceso_activo"] = True

                agregar_mensaje("bot", f"✅ Bienvenido {postulante['nombre']}.\n\n📌 Estás postulando al puesto **{st.session_state['puesto']['nombre']}**.")
                agregar_mensaje("bot", "Para continuar, debes aceptar los términos de la entrevista. Escribe **'ACEPTO'** para continuar.")

            else:
                agregar_mensaje("bot", "❌ No encontramos tu documento. Contacta a RRHH en infoprocesosrrhh@chinalco.com.pe.")

        # 🔹 Paso 3: Confirmar aceptación
        elif st.session_state["proceso_activo"]:
            if user_input.lower() in ["acepto", "si acepto"]:
                agregar_mensaje("bot", "✅ Gracias. Iniciemos con las preguntas generales.")
                
                # Generar preguntas parafraseadas
                preguntas_parafraseadas = {parafrasear_pregunta(k): v for k, v in preguntas_generales.items()}
                st.session_state["preguntas_parafraseadas"] = preguntas_parafraseadas

                # Lanzar primera pregunta
                pregunta_actual, respuesta_esperada = random.choice(list(preguntas_parafraseadas.items()))
                st.session_state["pregunta_actual"] = pregunta_actual
                agregar_mensaje("bot", pregunta_actual)
            else:
                agregar_mensaje("bot", "❌ No aceptaste los términos. La entrevista ha sido cancelada.")

        # 🔹 Procesar respuestas a preguntas
        elif "pregunta_actual" in st.session_state:
            pregunta_actual = st.session_state["pregunta_actual"]
            respuesta_esperada = st.session_state["preguntas_parafraseadas"][pregunta_actual]

            evaluacion = evaluar_respuesta(pregunta_actual, user_input, respuesta_esperada)
            st.session_state["respuestas_usuario"][pregunta_actual] = evaluacion
            guardar_historial()

            agregar_mensaje("bot", "✅ Respuesta registrada. Continuemos...")
            del st.session_state["pregunta_actual"]

    st.experimental_rerun()
