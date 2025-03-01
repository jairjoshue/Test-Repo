import streamlit as st
import google.generativeai as genai
import json
import time
import random
from datetime import datetime

# Cargar CSS personalizado
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Llamar la función al inicio
load_css()

# Configurar la API de Gemini
API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
genai.configure(api_key=API_KEY)

# Usar un modelo ligero para evitar bloqueos
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Función para cargar archivos JSON
def cargar_json(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)

# Cargar datos desde archivos JSON
postulantes = cargar_json("postulantes.json")
preguntas_generales = cargar_json("preguntas_generales.json")
puestos = cargar_json("puestos.json")

# Inicializar sesión de usuario
if "entrevista_iniciada" not in st.session_state:
    st.session_state["entrevista_iniciada"] = False
if "respuestas_usuario" not in st.session_state:
    st.session_state["respuestas_usuario"] = {}
if "entrevista_completada" not in st.session_state:
    st.session_state["entrevista_completada"] = False

# Función para validar postulantes
def validar_postulante(nombre, documento):
    for postulante in postulantes:
        if postulante["nombre"].lower() == nombre.lower() and postulante["documento"] == documento:
            return puestos.get(postulante["codigo_puesto"]), postulante["codigo_puesto"]
    return None, None

# Función para evaluar respuestas con IA
def evaluar_respuestas(respuestas_usuario):
    feedback_total = {}
    puntaje_total = 0
    total_preguntas = len(respuestas_usuario)

    for pregunta, datos in respuestas_usuario.items():
        respuesta = datos["respuesta"]
        respuesta_esperada = datos["esperada"]
        prompt = f"""
        Evalúa la respuesta del candidato comparándola con la respuesta esperada.
        Devuelve una puntuación (1: Correcto, 0.5: Parcialmente Correcto, 0: Incorrecto) y una breve justificación.
        Además, analiza la confianza y coherencia del candidato.
        
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

        feedback_total[pregunta] = {
            "respuesta_usuario": respuesta,
            "evaluacion": feedback,
            "puntaje": puntaje
        }
        puntaje_total += puntaje

    porcentaje_aciertos = (puntaje_total / total_preguntas) * 100
    return feedback_total, porcentaje_aciertos

# Guardar respuestas y feedback en JSON
def guardar_datos(nombre, documento, feedback_total, puntaje_final):
    respuesta_json = {
        "nombre": nombre,
        "documento": documento,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "puntaje_final": puntaje_final,
        "feedback": feedback_total
    }

    with open("data/feedback.json", "r+", encoding="utf-8") as file:
        datos = json.load(file)
        datos.append(respuesta_json)
        file.seek(0)
        json.dump(datos, file, indent=4, ensure_ascii=False)

# Interfaz Web Mejorada
st.image("logo-mina.png", width=200)
st.markdown("<h1 style='text-align: center;'>Chatbot de Entrevistas - Minera CHINALCO</h1>", unsafe_allow_html=True)

# Validación del postulante
st.markdown("<h2>🔍 Validación de Identidad</h2>", unsafe_allow_html=True)

nombre = st.text_input("Ingrese su nombre completo:")
documento = st.text_input("Ingrese su documento de identidad:")

if st.button("🔎 Validar Postulante"):
    puesto, codigo_puesto = validar_postulante(nombre, documento)
    
    if puesto:
        st.session_state["puesto"] = puesto
        st.session_state["entrevista_iniciada"] = True
        st.success(f"✅ Validación exitosa para: {nombre}")
    else:
        st.error("❌ No encontramos su información en nuestra base de datos. Para dudas, escriba a inforrhh@chinalco.com.pe")

# Iniciar la entrevista
if st.session_state["entrevista_iniciada"]:
    if st.checkbox("✅ Acepto las reglas de la entrevista"):
        puesto = st.session_state["puesto"]
        st.markdown("<h2>📝 Preguntas Generales</h2>", unsafe_allow_html=True)
        
        for pregunta in preguntas_generales.keys():
            st.markdown(f"<h3>{pregunta}</h3>", unsafe_allow_html=True)
            respuesta = st.text_area(f"Responda aquí:", key=pregunta)
            st.session_state["respuestas_usuario"][pregunta] = {"respuesta": respuesta, "esperada": preguntas_generales[pregunta]}

        st.markdown("<h2>📊 Preguntas Técnicas</h2>", unsafe_allow_html=True)

        preguntas_puesto = list(puesto["preguntas"].items())
        random.shuffle(preguntas_puesto)  # Orden aleatorio

        for pregunta, respuesta_esperada in preguntas_puesto:
            st.markdown(f"<h3>{pregunta}</h3>", unsafe_allow_html=True)
            respuesta = st.text_area(f"Responda aquí:", key=pregunta)
            st.session_state["respuestas_usuario"][pregunta] = {"respuesta": respuesta, "esperada": respuesta_esperada}

        # Botón para enviar respuestas
        if st.button("📩 Enviar Entrevista y Obtener Feedback"):
            feedback_total, porcentaje_aciertos = evaluar_respuestas(st.session_state["respuestas_usuario"])
            guardar_datos(nombre, documento, feedback_total, porcentaje_aciertos)
            st.success(f"🎯 Puntaje final: **{porcentaje_aciertos:.2f}%**")
            st.write("📩 Sus respuestas serán enviadas a Recursos Humanos.")

            # Mostrar feedback
            for pregunta, datos in feedback_total.items():
                st.markdown(f"<h3>{pregunta}</h3>", unsafe_allow_html=True)
                st.write(f"✅ Respuesta: {datos['respuesta_usuario']}")
                st.write(f"📊 Evaluación: {datos['evaluacion']}")
                st.write(f"🎯 Puntaje: {datos['puntaje']}/1")
