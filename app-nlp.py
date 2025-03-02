import streamlit as st
import json
import random
import datetime
import pandas as pd
import google.generativeai as genai

# Configurar API de Gemini
try:
    genai.configure(api_key="AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM")
    model = genai.GenerativeModel("gemini-1.5-flash")
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    print("Error al configurar Gemini:", e)

# Función para consultar a Gemini en lote
def consultar_gemini_lote(consultas):
    if GEMINI_AVAILABLE:
        try:
            response = model.generate_content("\n".join(consultas))
            return response.text.split("\n") if response and response.text else ["Error"] * len(consultas)
        except Exception as e:
            print("Error en Gemini:", e)
            return ["Error en procesamiento"] * len(consultas)
    else:
        return ["Gemini no disponible"] * len(consultas)

# Cargar datos desde archivos JSON
with open("postulantes.json", "r") as f:
    postulantes = json.load(f)
with open("puestos.json", "r") as f:
    puestos = json.load(f)
with open("preguntas_generales.json", "r") as f:
    preguntas_generales = json.load(f)

# Inicializar variables en la sesión
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "postulante" not in st.session_state:
        st.session_state.postulante = None
    if "df_preguntas" not in st.session_state:
        st.session_state.df_preguntas = pd.DataFrame(columns=["pregunta", "respuesta_esperada"])
    if "indice_pregunta" not in st.session_state:
        st.session_state.indice_pregunta = 0
    if "respuestas" not in st.session_state:
        st.session_state.respuestas = []
    if "acepto_terminos" not in st.session_state:
        st.session_state.acepto_terminos = False
    if "fase" not in st.session_state:
        st.session_state.fase = "inicio"

init_session()

# Función para mostrar mensajes en el chat
def mostrar_mensaje(rol, mensaje):
    with st.chat_message(rol):
        st.markdown(mensaje)
    st.session_state.messages.append({"role": rol, "content": mensaje})

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Validación del postulante
if st.session_state.fase == "inicio":
    mostrar_mensaje("assistant", "Bienvenido a la entrevista de Minera CHINALCO. Ingresa tu número de documento para validar tu registro.")
    doc_input = st.chat_input("Ingresa tu número de documento")
    if doc_input:
        mostrar_mensaje("user", doc_input)
        postulante = next((p for p in postulantes if p["documento"] == doc_input), None)
        if postulante:
            st.session_state.postulante = postulante
            puesto_codigo = postulante["codigo_puesto"]
            if puesto_codigo in puestos:
                st.session_state.df_preguntas = pd.DataFrame(
                    list({**preguntas_generales, **puestos[puesto_codigo]["preguntas"]}.items()), 
                    columns=["pregunta", "respuesta_esperada"]
                )
            mostrar_mensaje("assistant", f"Bienvenido **{postulante['nombre']}**. Postulas al puesto **{puestos[puesto_codigo]['nombre']}**. Acepta los términos para continuar.")
            st.session_state.fase = "esperando_terminos"
        else:
            mostrar_mensaje("assistant", "Tu documento no está registrado. Contacta con RRHH en infoprocesosrrhh@chinalco.com.pe.")
            st.stop()

# Aceptación de términos
if st.session_state.fase == "esperando_terminos":
    if st.button("Acepto los términos"):
        mostrar_mensaje("user", "Acepto los términos")
        st.session_state.acepto_terminos = True
        st.session_state.fase = "preguntas"
        st.rerun()

# Navegación por preguntas
if st.session_state.fase == "preguntas" and st.session_state.indice_pregunta < len(st.session_state.df_preguntas):
    pregunta_actual = st.session_state.df_preguntas.iloc[st.session_state.indice_pregunta]["pregunta"]
    if "pregunta_mostrada" not in st.session_state or st.session_state.pregunta_mostrada != pregunta_actual:
        mostrar_mensaje("assistant", pregunta_actual)
        st.session_state.pregunta_mostrada = pregunta_actual
    respuesta_usuario = st.chat_input("Tu respuesta")
    if respuesta_usuario:
        mostrar_mensaje("user", respuesta_usuario)
        st.session_state.respuestas.append({
            "pregunta": pregunta_actual,
            "respuesta_usuario": respuesta_usuario,
            "respuesta_esperada": st.session_state.df_preguntas.iloc[st.session_state.indice_pregunta]["respuesta_esperada"]
        })
        st.session_state.indice_pregunta += 1
        if st.session_state.indice_pregunta >= len(st.session_state.df_preguntas):
            st.session_state.fase = "evaluacion"
        st.rerun()

# Finalización y análisis tras responder todas las preguntas
if st.session_state.fase == "evaluacion":
    consultas_eval = [
        f"Pregunta: {r['pregunta']}\nRespuesta usuario: {r['respuesta_usuario']}\nRespuesta esperada: {r['respuesta_esperada']}"
        for r in st.session_state.respuestas
    ]
    resultados_eval = consultar_gemini_lote(consultas_eval)
    feedback_general = consultar_gemini_lote([f"Genera un feedback general sobre la entrevista considerando estas respuestas: {json.dumps(st.session_state.respuestas)}"])[0]
    promedio_calificacion = consultar_gemini_lote([f"Calcula un puntaje promedio basado en la coherencia y relevancia de las respuestas con respecto a las respuestas esperadas: {json.dumps(st.session_state.respuestas)}"])[0]
    mostrar_mensaje("assistant", f"Gracias por completar la entrevista. **Feedback:** {feedback_general}\n**Calificación final:** {promedio_calificacion}")
    st.session_state.clear()

