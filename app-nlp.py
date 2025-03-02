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
if "messages" not in st.session_state:
    st.session_state.messages = []
if "postulante" not in st.session_state:
    st.session_state.postulante = None
if "preguntas" not in st.session_state:
    st.session_state.preguntas = []
if "respuestas" not in st.session_state:
    st.session_state.respuestas = {}

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Validación del postulante
if st.session_state.postulante is None:
    mostrar_mensaje = "Bienvenido a la entrevista de Minera CHINALCO. Ingresa tu número de documento para validar tu registro."
    doc_input = st.chat_input(mostrar_mensaje)
    if doc_input:
        st.session_state.messages.append({"role": "user", "content": doc_input})
        postulante = next((p for p in postulantes if p["documento"] == doc_input), None)
        if postulante:
            st.session_state.postulante = postulante
            puesto = puestos[postulante["codigo_puesto"]]
            mostrar_mensaje = f"Bienvenido **{postulante['nombre']}**. Postulas al puesto **{puesto['nombre']}**. Acepta los términos para continuar."
            if st.button("Acepto los términos"):
                st.session_state.preguntas = list(puesto["preguntas"].keys())
                st.session_state.pregunta_actual = 0
                st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": "Tu documento no está registrado. Contacta con RRHH en infoprocesosrrhh@chinalco.com.pe."})
            st.stop()

# Proceso de preguntas
if st.session_state.postulante and st.session_state.preguntas:
    if st.session_state.pregunta_actual < len(st.session_state.preguntas):
        pregunta_actual = st.session_state.preguntas[st.session_state.pregunta_actual]
        mostrar_mensaje = f"{pregunta_actual}"
        respuesta_usuario = st.chat_input(mostrar_mensaje)
        if respuesta_usuario:
            st.session_state.messages.append({"role": "user", "content": respuesta_usuario})
            st.session_state.respuestas[pregunta_actual] = {
                "respuesta": respuesta_usuario
            }
            st.session_state.pregunta_actual += 1
            st.rerun()
    else:
        num_entrevista = random.randint(100000, 999999)
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Preparar consultas para evaluación en lote
        consultas_eval = []
        for pregunta, datos in st.session_state.respuestas.items():
            respuesta_usuario = datos["respuesta"]
            respuesta_esperada = puestos[st.session_state.postulante["codigo_puesto"]]["preguntas"][pregunta]
            consultas_eval.append(f"Compara la respuesta con la esperada y da un puntaje de 0 a 100:\n\nPregunta: {pregunta}\nRespuesta usuario: {respuesta_usuario}\nRespuesta esperada: {respuesta_esperada}")
        
        resultados_eval = consultar_gemini_lote(consultas_eval)
        
        # Asignar evaluaciones
        for i, pregunta in enumerate(st.session_state.respuestas.keys()):
            st.session_state.respuestas[pregunta]["evaluacion"] = resultados_eval[i]
        
        # Generar feedback y calificación en lote
        feedback_general = consultar_gemini_lote(["Genera un feedback general sobre la entrevista basándote en las respuestas del postulante."])[0]
        promedio_calificacion = consultar_gemini_lote(["Calcula un puntaje promedio basado en la evaluación de respuestas del postulante."])[0]
        
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
        
        st.session_state.messages.append({"role": "assistant", "content": f"Gracias por completar la entrevista. Tu número de entrevista es {num_entrevista}.\n\n**Feedback:** {feedback_general}\n\n**Calificación final:** {promedio_calificacion}"})
        st.session_state.clear()
