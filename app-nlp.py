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

# Obtener las preguntas del puesto del postulante
puesto_codigo = None
preguntas_especificas = {}
if "postulante" in st.session_state and st.session_state.postulante:
    puesto_codigo = st.session_state.postulante["codigo_puesto"]
    if puesto_codigo in puestos and "preguntas" in puestos[puesto_codigo]:
        preguntas_especificas = puestos[puesto_codigo]["preguntas"]

# Fusionar preguntas generales y específicas en un dataframe
todas_preguntas = {**preguntas_generales, **preguntas_especificas}
df_preguntas = pd.DataFrame(list(todas_preguntas.items()), columns=["pregunta", "respuesta_esperada"])

# Inicializar historial de chat
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "df_preguntas" not in st.session_state:
        st.session_state.df_preguntas = df_preguntas
    if "indice_pregunta" not in st.session_state:
        st.session_state.indice_pregunta = 0
    if "respuestas" not in st.session_state:
        st.session_state.respuestas = []
    if "acepto_terminos" not in st.session_state:
        st.session_state.acepto_terminos = False
    if "fase" not in st.session_state:
        st.session_state.fase = "preguntas"

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
if "postulante" not in st.session_state or st.session_state.postulante is None:
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
        else:
            mostrar_mensaje("assistant", "Tu documento no está registrado. Contacta con RRHH en infoprocesosrrhh@chinalco.com.pe.")
            st.stop()

# Aceptación de términos
if st.session_state.postulante and not st.session_state.acepto_terminos:
    if st.button("Acepto los términos"):
        mostrar_mensaje("user", "Acepto los términos")
        st.session_state.acepto_terminos = True

# Navegación por preguntas
if st.session_state.acepto_terminos and st.session_state.indice_pregunta < len(st.session_state.df_preguntas):
    pregunta_actual = st.session_state.df_preguntas.iloc[st.session_state.indice_pregunta]
    mostrar_mensaje("assistant", pregunta_actual["pregunta"])
    respuesta_usuario = st.chat_input("Tu respuesta")
    if respuesta_usuario:
        mostrar_mensaje("user", respuesta_usuario)
        st.session_state.respuestas.append({
            "pregunta": pregunta_actual["pregunta"],
            "respuesta_usuario": respuesta_usuario,
            "respuesta_esperada": pregunta_actual["respuesta_esperada"]
        })
        st.session_state.indice_pregunta += 1
        st.rerun()

# Finalización y análisis tras responder todas las preguntas
if st.session_state.acepto_terminos and st.session_state.indice_pregunta >= len(st.session_state.df_preguntas):
    consultas_eval = [
        f"Pregunta: {r['pregunta']}\nRespuesta usuario: {r['respuesta_usuario']}\nRespuesta esperada: {r['respuesta_esperada']}"
        for r in st.session_state.respuestas
    ]
    resultados_eval = consultar_gemini_lote(consultas_eval)
    for i, r in enumerate(st.session_state.respuestas):
        r["evaluacion"] = resultados_eval[i]
    feedback_general = consultar_gemini_lote(["Genera un feedback general sobre la entrevista."])[0]
    promedio_calificacion = consultar_gemini_lote(["Calcula un puntaje promedio."])[0]
    mostrar_mensaje("assistant", f"Gracias por completar la entrevista. **Feedback:** {feedback_general}\n**Calificación final:** {promedio_calificacion}")
    st.session_state.clear()
