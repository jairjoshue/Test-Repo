import streamlit as st
import json
import random
import datetime
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

# Inicializar historial de chat
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "postulante" not in st.session_state:
        st.session_state.postulante = None
    if "preguntas" not in st.session_state:
        st.session_state.preguntas = []
    if "preguntas_generales" not in st.session_state:
        st.session_state.preguntas_generales = list(preguntas_generales.keys())
    if "respuestas" not in st.session_state:
        st.session_state.respuestas = {}
    if "acepto_terminos" not in st.session_state:
        st.session_state.acepto_terminos = False
    if "pregunta_actual" not in st.session_state:
        st.session_state.pregunta_actual = None

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
if st.session_state.postulante is None:
    mostrar_mensaje("assistant", "Bienvenido a la entrevista de Minera CHINALCO. Ingresa tu número de documento para validar tu registro.")
    doc_input = st.chat_input("Ingresa tu número de documento")
    if doc_input:
        mostrar_mensaje("user", doc_input)
        postulante = next((p for p in postulantes if p["documento"] == doc_input), None)
        if postulante:
            st.session_state.postulante = postulante
            puesto = puestos[postulante["codigo_puesto"]]
            mostrar_mensaje("assistant", f"Bienvenido **{postulante['nombre']}**. Postulas al puesto **{puesto['nombre']}**. Acepta los términos para continuar.")
        else:
            mostrar_mensaje("assistant", "Tu documento no está registrado. Contacta con RRHH en infoprocesosrrhh@chinalco.com.pe.")
            st.stop()

# Aceptación de términos
if st.session_state.postulante and not st.session_state.acepto_terminos:
    if st.button("Acepto los términos"):
        mostrar_mensaje("user", "Acepto los términos")
        st.session_state.acepto_terminos = True

# Preguntas generales antes de las específicas
if st.session_state.acepto_terminos and st.session_state.pregunta_actual is None:
    if st.session_state.preguntas_generales:
        st.session_state.pregunta_actual = st.session_state.preguntas_generales.pop(0)
        mostrar_mensaje("assistant", st.session_state.pregunta_actual)
    elif st.session_state.preguntas:
        st.session_state.pregunta_actual = st.session_state.preguntas.pop(0)
        mostrar_mensaje("assistant", st.session_state.pregunta_actual)

if st.session_state.acepto_terminos and st.session_state.pregunta_actual:
    respuesta_usuario = st.chat_input("Tu respuesta")
    if respuesta_usuario:
        mostrar_mensaje("user", respuesta_usuario)
        st.session_state.respuestas[st.session_state.pregunta_actual] = {"respuesta": respuesta_usuario}
        st.session_state.pregunta_actual = None
        st.rerun()

# Finalización y análisis (solo cuando no quedan preguntas pendientes)
if st.session_state.acepto_terminos and not st.session_state.preguntas and not st.session_state.preguntas_generales and st.session_state.pregunta_actual is None:
    num_entrevista = random.randint(100000, 999999)
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    consultas_eval = [
        f"Pregunta: {p}\nRespuesta usuario: {r['respuesta']}\nRespuesta esperada: {preguntas_generales.get(p, '')}" 
        for p, r in st.session_state.respuestas.items()
    ]
    resultados_eval = consultar_gemini_lote(consultas_eval)
    for i, pregunta in enumerate(st.session_state.respuestas.keys()):
        st.session_state.respuestas[pregunta]["evaluacion"] = resultados_eval[i]
    feedback_general = consultar_gemini_lote(["Genera un feedback general sobre la entrevista."])[0]
    promedio_calificacion = consultar_gemini_lote(["Calcula un puntaje promedio."])[0]
    reporte = {
        "postulante": st.session_state.postulante,
        "puesto": puestos[st.session_state.postulante["codigo_puesto"]],
        "fecha": fecha,
        "respuestas": st.session_state.respuestas,
        "feedback": feedback_general,
        "calificacion": promedio_calificacion,
        "id_entrevista": num_entrevista
    }
    with open(f"entrevista_{num_entrevista}.json", "w") as f:
        json.dump(reporte, f)
    mostrar_mensaje("assistant", f"Gracias por completar la entrevista. **Feedback:** {feedback_general}\n**Calificación final:** {promedio_calificacion}")
    st.session_state.clear()
