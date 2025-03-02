import streamlit as st
import json
import random
import datetime
from google.generativeai import configure, generate_text

# Configurar API de Gemini
configure(api_key="AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM")

def procesar_lote_gemini(consultas):
    respuestas = generate_text("\n".join(consultas))
    return respuestas.text.split("\n") if respuestas else ["Error"] * len(consultas)

# Cargar datos desde archivos JSON
with open("postulantes.json", "r") as f:
    postulantes = json.load(f)
with open("puestos.json", "r") as f:
    puestos = json.load(f)
with open("preguntas_generales.json", "r") as f:
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
    mostrar_mensaje("assistant", "Bienvenido al proceso de entrevista de Minera CHINALCO. \n\n Para esta simulación, puedes usar estos datos de prueba: \n - Juan Perez - Documento: 20020020 \n - Maria Cuadro - Documento: 50050050")
    nombre_input = st.chat_input("Ingresa tu nombre (como está registrado en el sistema)")
    if nombre_input:
        mostrar_mensaje("user", nombre_input)
        mostrar_mensaje("assistant", "Gracias. Ahora, ingresa tu número de documento de identidad.")
        doc_input = st.chat_input("Ingresa tu número de documento")
        if doc_input:
            mostrar_mensaje("user", doc_input)
            postulante = buscar_postulante(doc_input)
            if postulante:
                st.session_state.postulante = postulante
                puesto = puestos[postulante["codigo_puesto"]]
                mostrar_mensaje("assistant", f"Bienvenido **{postulante['nombre']}**. Postulas al puesto **{puesto['nombre']}**. \n\n **Explicación del proceso:** \n - Se evaluarán tus conocimientos generales y técnicos. \n - Usaremos IA para parafrasear preguntas y validar respuestas. \n - Analizaremos la coherencia y confianza en tus respuestas. \n\n **Por favor, acepta los términos para continuar.**")
                if st.button("Acepto los términos"):
                    st.session_state.preguntas = list(puesto["preguntas"].keys())
                    st.session_state.pregunta_actual = 0
                    st.rerun()
            else:
                mostrar_mensaje("assistant", "Tu documento no está registrado. Contacta con RRHH en infoprocesosrrhh@chinalco.com.pe.")
                st.stop()

# Proceso de preguntas
if st.session_state.postulante and st.session_state.preguntas:
    if st.session_state.pregunta_actual < len(st.session_state.preguntas):
        preguntas_originales = st.session_state.preguntas
        consultas_gemini = [f"Parafrasea la pregunta manteniendo su significado: {p}" for p in preguntas_originales]
        preguntas_parafraseadas = procesar_lote_gemini(consultas_gemini)
        
        pregunta_actual = preguntas_parafraseadas[st.session_state.pregunta_actual]
        mostrar_mensaje("assistant", f"{pregunta_actual}")
        
        respuesta_usuario = st.chat_input("Tu respuesta")
        if respuesta_usuario:
            mostrar_mensaje("user", respuesta_usuario)
            consultas_eval = [
                f"Compara la respuesta con la esperada y da un porcentaje de certeza entre 0 y 100%: \n\n Respuesta: {respuesta_usuario} \n Respuesta esperada: {puestos[st.session_state.postulante['codigo_puesto']]['preguntas'][preguntas_originales[st.session_state.pregunta_actual]]}"
            ]
            consultas_sent = [f"Analiza el sentimiento de esta respuesta: {respuesta_usuario}"]
            
            resultados_eval = procesar_lote_gemini(consultas_eval)
            resultados_sent = procesar_lote_gemini(consultas_sent)
            
            st.session_state.respuestas[preguntas_originales[st.session_state.pregunta_actual]] = {
                "respuesta": respuesta_usuario,
                "certeza": resultados_eval[0],
                "sentimiento": resultados_sent[0]
            }
            
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
        with open(f"entrevista_{num_entrevista}.json", "w") as f:
            json.dump(reporte, f)
        mostrar_mensaje("assistant", f"Gracias por completar la entrevista. Tu número de entrevista es {num_entrevista}. RRHH se comunicará contigo.")
        st.session_state.clear()
