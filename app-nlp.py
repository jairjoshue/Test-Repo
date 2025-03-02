import streamlit as st
import json
import random
import time
from google.generativeai import configure, generate_content

# Configurar la API de Gemini
# Configurar la API de Gemini
GEMINI_API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
configure(api_key=API_KEY)
#model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Cargar bases de datos
with open("preguntas_generales.json", "r", encoding="utf-8") as f:
    preguntas_generales = json.load(f)

with open("postulantes.json", "r", encoding="utf-8") as f:
    postulantes = json.load(f)

with open("puestos.json", "r", encoding="utf-8") as f:
    puestos = json.load(f)

# Función para verificar postulante
def verificar_postulante(documento):
    for p in postulantes:
        if p["documento"] == documento:
            return p
    return None

# Función para parafrasear pregunta con Gemini
def parafrasear_pregunta(pregunta):
    prompt = f"Parafrasea la siguiente pregunta sin cambiar su significado: {pregunta}"
    respuesta = generate_content(prompt)
    return respuesta.text.strip()

# Función para evaluar respuesta con Gemini
def evaluar_respuesta(pregunta, respuesta):
    prompt = (f"Evalúa la respuesta del candidato en base a la siguiente pregunta esperada: \n"
              f"Pregunta: {pregunta}\n"
              f"Respuesta esperada: {preguntas_generales.get(pregunta, 'No disponible')}\n"
              f"Respuesta del candidato: {respuesta}\n"
              f"Devuelve un porcentaje de certeza (0-100%) basado en la relevancia de la respuesta.")
    resultado = generate_content(prompt)
    return resultado.text.strip()

# Estado de la aplicación
if "estado" not in st.session_state:
    st.session_state.estado = "inicio"
    st.session_state.intentos = 0
    st.session_state.respuestas = []

st.title("🎤 Entrevista Virtual - Minera CHINALCO")

# Chatbot - Lógica de Flujo
if st.session_state.estado == "inicio":
    st.write("👋 ¡Bienvenido al proceso de entrevistas virtuales de CHINALCO!")
    st.write("Para continuar, ingresa tu número de documento registrado en el sistema.")
    documento = st.text_input("Número de documento", key="doc")
    if st.button("Verificar"):
        postulante = verificar_postulante(documento)
        if postulante:
            st.session_state.postulante = postulante
            st.session_state.estado = "bienvenida"
            st.experimental_rerun()
        else:
            st.error("❌ No encontramos tu documento en la base de datos. Contacta a RRHH: infoprocesosrrhh@chinalco.com.pe")

elif st.session_state.estado == "bienvenida":
    postulante = st.session_state.postulante
    puesto = puestos.get(postulante["codigo_puesto"], {})
    st.write(f"✅ Hola **{postulante['nombre']}**, bienvenido al proceso de selección para el puesto de **{puesto.get('nombre', 'No identificado')}**.")
    st.write("Este proceso consta de preguntas específicas sobre el puesto y validaremos tus respuestas.")
    
    if st.button("Aceptar y continuar"):
        st.session_state.estado = "preguntas"
        st.experimental_rerun()

elif st.session_state.estado == "preguntas":
    puesto = puestos.get(st.session_state.postulante["codigo_puesto"], {})
    preguntas = list(puesto.get("preguntas", {}).keys())
    
    if "pregunta_actual" not in st.session_state:
        st.session_state.pregunta_actual = 0
    
    if st.session_state.pregunta_actual < len(preguntas):
        pregunta = preguntas[st.session_state.pregunta_actual]
        pregunta_parafraseada = parafrasear_pregunta(pregunta)
        st.write(f"🧐 Pregunta {st.session_state.pregunta_actual + 1}: {pregunta_parafraseada}")
        respuesta = st.text_area("Tu respuesta", key="respuesta")
        
        if st.button("Enviar respuesta"):
            puntuacion = evaluar_respuesta(pregunta, respuesta)
            st.session_state.respuestas.append({
                "pregunta_original": pregunta,
                "pregunta_parafraseada": pregunta_parafraseada,
                "respuesta": respuesta,
                "puntuacion": puntuacion
            })
            st.session_state.pregunta_actual += 1
            st.experimental_rerun()
    else:
        st.session_state.estado = "finalizar"
        st.experimental_rerun()

elif st.session_state.estado == "finalizar":
    id_entrevista = random.randint(10000, 99999)
    st.write("🎉 ¡Has completado la entrevista!")
    st.write(f"Tu entrevista ha sido registrada con el ID: **{id_entrevista}**")
    st.write("Tu desempeño será evaluado y RRHH se pondrá en contacto contigo.")
    
    with open(f"reporte_{id_entrevista}.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.respuestas, f, ensure_ascii=False, indent=4)
    
    if st.button("Finalizar"):
        st.session_state.estado = "inicio"
        st.session_state.respuestas = []
        st.session_state.pregunta_actual = 0
        st.experimental_rerun()
