import streamlit as st
import json
import random
import datetime

# Cargar datos desde archivos JSON
with open("/mnt/data/postulantes.json", "r") as f:
    postulantes = json.load(f)
with open("/mnt/data/puestos.json", "r") as f:
    puestos = json.load(f)
with open("/mnt/data/preguntas_generales.json", "r") as f:
    preguntas_generales = json.load(f)

# Inicializar historial de chat
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "postulante" not in st.session_state:
        st.session_state.postulante = None
    if "preguntas" not in st.session_state:
        st.session_state.preguntas = []
    if "respuestas" not in st.session_state:
        st.session_state.respuestas = {}

init_session()

# Función para buscar postulante
def buscar_postulante(documento):
    for p in postulantes:
        if p["documento"] == documento:
            return p
    return None

# Función para mostrar mensaje en el chat
def mostrar_mensaje(rol, mensaje):
    with st.chat_message(rol):
        st.markdown(mensaje)
    st.session_state.messages.append({"role": rol, "content": mensaje})

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Pantalla inicial
if st.session_state.postulante is None:
    mostrar_mensaje("assistant", "Bienvenido al proceso de entrevista de Minera CHINALCO. Por favor, ingresa tu número de documento para verificar tu registro.")
    doc_input = st.chat_input("Ingresa tu número de documento")
    if doc_input:
        postulante = buscar_postulante(doc_input)
        if postulante:
            st.session_state.postulante = postulante
            puesto = puestos[postulante["codigo_puesto"]]
            mostrar_mensaje("assistant", f"Bienvenido {postulante['nombre']}. Postulas al puesto **{puesto['nombre']}**. Este proceso evaluará tu idoneidad para el puesto mediante una serie de preguntas. Acepta los términos para continuar.")
            if st.button("Aceptar términos"):
                st.session_state.preguntas = list(puesto["preguntas"].keys())
                st.rerun()
        else:
            mostrar_mensaje("assistant", "Tu documento no está registrado. Contacta con RRHH en infoprocesosrrhh@chinalco.com.pe.")
            st.stop()

# Proceso de preguntas
if st.session_state.postulante and st.session_state.preguntas:
    if "pregunta_actual" not in st.session_state:
        st.session_state.pregunta_actual = 0
    
    if st.session_state.pregunta_actual < len(st.session_state.preguntas):
        pregunta = st.session_state.preguntas[st.session_state.pregunta_actual]
        mostrar_mensaje("assistant", f"{pregunta}")
        respuesta_usuario = st.chat_input("Tu respuesta")
        if respuesta_usuario:
            st.session_state.respuestas[pregunta] = respuesta_usuario
            st.session_state.pregunta_actual += 1
            st.rerun()
    else:
        num_entrevista = random.randint(100000, 999999)
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reporte = {
            "postulante": st.session_state.postulante,
            "puesto": puestos[st.session_state.postulante["codigo_puesto"]],
            "fecha": fecha,
            "respuestas": st.session_state.respuestas,
            "id_entrevista": num_entrevista
        }
        with open(f"/mnt/data/entrevista_{num_entrevista}.json", "w") as f:
            json.dump(reporte, f)
        mostrar_mensaje("assistant", f"Gracias por completar la entrevista. Tu número de entrevista es {num_entrevista}. RRHH se comunicará contigo.")
        st.session_state.clear()
