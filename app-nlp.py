import streamlit as st
import json
import random
import time
from google.generativeai import configure, generate_content

# Configurar la API de Gemini
# Configurar la API de Gemini
GEMINI_API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
configure(api_key=API_KEY)

# Usar un modelo ligero para evitar bloqueos
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Cargar datos desde archivos JSON
def cargar_json(nombre_archivo):
    with open(nombre_archivo, "r", encoding="utf-8") as archivo:
        return json.load(archivo)

# Guardar datos en archivos JSON
def guardar_json(nombre_archivo, datos):
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4, ensure_ascii=False)

# Cargar datos
postulantes = cargar_json("postulantes.json")
preguntas_generales_empresa = cargar_json("preguntas_generales.json")
puestos = cargar_json("puestos.json")

# Estado de la aplicación
def inicializar_estado():
    if "entrevista_iniciada" not in st.session_state:
        st.session_state["entrevista_iniciada"] = False
    if "respuestas_usuario" not in st.session_state:
        st.session_state["respuestas_usuario"] = {}
    if "preguntas_ordenadas" not in st.session_state:
        st.session_state["preguntas_ordenadas"] = []
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "puesto" not in st.session_state:
        st.session_state["puesto"] = None
    if "postulante" not in st.session_state:
        st.session_state["postulante"] = None

inicializar_estado()

# Validar postulante
def validar_postulante(documento):
    for postulante in postulantes:
        if postulante["documento"] == documento:
            return postulante, puestos.get(postulante["codigo_puesto"])
    return None, None

# Iniciar entrevista
def iniciar_entrevista():
    puesto = st.session_state["puesto"]
    if not st.session_state["preguntas_ordenadas"]:
        preguntas = list(puesto["preguntas"].items())
        random.shuffle(preguntas)
        st.session_state["preguntas_ordenadas"] = preguntas
    st.session_state["chat_history"].append(("👨‍💼", f"Bienvenido a Minera CHINALCO. Postula al puesto de **{puesto['nombre']}**. Comencemos la entrevista."))

# Evaluación con IA
def evaluar_respuestas():
    respuestas_usuario = st.session_state["respuestas_usuario"]
    feedback_total = {}
    puntaje_total = 0
    total_preguntas = len(respuestas_usuario)
    for pregunta, datos in respuestas_usuario.items():
        respuesta = datos["respuesta"]
        respuesta_esperada = datos["esperada"]
        prompt = f"Evalúa la respuesta: {respuesta} frente a la esperada: {respuesta_esperada}. Da un puntaje entre 0-100%."
        response = model.generate_content(prompt)
        feedback_total[pregunta] = {"respuesta": respuesta, "evaluacion": response.text.strip()}
    return feedback_total

# Guardar historial de entrevistas
def guardar_historial():
    historial = {"postulante": st.session_state["postulante"], "respuestas": evaluar_respuestas()}
    with open("historial.json", "w", encoding="utf-8") as file:
        json.dump(historial, file, indent=4, ensure_ascii=False)

# Interfaz Streamlit
st.image("logo-mina.png", width=200)
st.markdown("<h1>💬 Chatbot de Entrevista - Minera CHINALCO</h1>", unsafe_allow_html=True)

documento = st.text_input("Ingrese su documento:")
if st.button("Verificar"):
    postulante, puesto = validar_postulante(documento)
    if postulante:
        st.session_state["postulante"] = postulante
        st.session_state["puesto"] = puesto
        st.session_state["entrevista_iniciada"] = True
        iniciar_entrevista()
    else:
        st.error("No se encontró en la base de datos. Contacte a RRHH.")

# Chatbot
chat_container = st.container()
with chat_container:
    for rol, mensaje in st.session_state["chat_history"]:
        st.markdown(f"**{rol}**: {mensaje}")

respuesta_usuario = st.text_input("Escriba su respuesta aquí:")
if st.button("📤 Enviar Respuesta"):
    if st.session_state["entrevista_iniciada"] and respuesta_usuario:
        pregunta, respuesta_esperada = st.session_state["preguntas_ordenadas"].pop(0)
        st.session_state["respuestas_usuario"][pregunta] = {"respuesta": respuesta_usuario, "esperada": respuesta_esperada}
        st.session_state["chat_history"].append(("👤", respuesta_usuario))
        if not st.session_state["preguntas_ordenadas"]:
            guardar_historial()
            st.success("Entrevista finalizada. Sus respuestas han sido enviadas a RRHH.")
