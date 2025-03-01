import streamlit as st
import google.generativeai as genai
import json
import os
import random
import time
from datetime import datetime

# Configurar la API de Gemini
API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
genai.configure(api_key=API_KEY)

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

# Configuración del estado de la aplicación en Streamlit
if "entrevista_iniciada" not in st.session_state:
    st.session_state["entrevista_iniciada"] = False
if "respuestas_usuario" not in st.session_state:
    st.session_state["respuestas_usuario"] = {}
if "preguntas_ordenadas" not in st.session_state:
    st.session_state["preguntas_ordenadas"] = []
if "entrevista_completada" not in st.session_state:
    st.session_state["entrevista_completada"] = False
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Validar postulante
def validar_postulante(nombre, documento):
    for postulante in postulantes:
        if postulante["nombre"].lower() == nombre.lower() and postulante["documento"] == documento:
            return puestos.get(postulante["codigo_puesto"]), postulante["codigo_puesto"]
    return None, None

# Iniciar la entrevista (se mezclan preguntas solo la primera vez)
def iniciar_entrevista():
    puesto = st.session_state["puesto"]
    if not st.session_state["preguntas_ordenadas"]:
        preguntas = list(puesto["preguntas"].items())
        random.shuffle(preguntas)  # Mezclar solo una vez
        st.session_state["preguntas_ordenadas"] = preguntas

# Evaluación con IA (Gemini)
def evaluar_respuestas(respuestas_usuario):
    feedback_total = {}
    puntaje_total = 0
    total_preguntas = len(respuestas_usuario)

    for pregunta, datos in respuestas_usuario.items():
        respuesta = datos["respuesta"]
        respuesta_esperada = datos["esperada"]
        prompt = f"""
        Evalúa la respuesta del candidato en comparación con la respuesta esperada.
        Devuelve una puntuación (1: Correcto, 0.5: Parcialmente Correcto, 0: Incorrecto) y una justificación clara.
        Además, realiza un análisis de sentimientos para evaluar la confianza del candidato.
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

# Guardar historial de entrevistas
def guardar_historial(nombre, documento, feedback_total, porcentaje_aciertos):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    historial = {"nombre": nombre, "documento": documento, "fecha": fecha_actual, 
                 "puntaje": porcentaje_aciertos, "respuestas": feedback_total}

    ruta = "historial.json"
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as file:
            historial_existente = json.load(file)
    else:
        historial_existente = []

    historial_existente.append(historial)

    with open(ruta, "w", encoding="utf-8") as file:
        json.dump(historial_existente, file, indent=4, ensure_ascii=False)

# UI - Estilo Chatbot
st.image("logo-mina.png", width=200)
st.markdown("<h1>💬 Entrevista Virtual - Minera CHINALCO</h1>", unsafe_allow_html=True)

# Validación del postulante
st.markdown("<h2>🔍 Validación de Identidad</h2>", unsafe_allow_html=True)

nombre = st.text_input("Ingrese su nombre completo:")
documento = st.text_input("Ingrese su documento de identidad:")

if st.button("🔎 Validar Postulante"):
    puesto, codigo_puesto = validar_postulante(nombre, documento)
    
    if puesto:
        st.session_state["puesto"] = puesto
        st.session_state["entrevista_iniciada"] = True
        st.session_state["chat_history"].append(("📢", f"✅ Validación exitosa para {nombre}"))

        # Mensaje de bienvenida
        st.session_state["chat_history"].append(("👨‍💼", f"Bienvenido a Minera CHINALCO, {nombre}. Postulas al puesto de **{puesto['nombre']}**."))
        
        iniciar_entrevista()
    else:
        st.error("❌ No encontramos su información. Contacte a inforrhh@chinalco.com.pe")

# Entrevista - Estilo Chatbot
if st.session_state["entrevista_iniciada"]:
    if st.checkbox("✅ Acepto las reglas de la entrevista"):

        st.markdown("<h2>💬 Chat de Entrevista</h2>", unsafe_allow_html=True)

        for rol, mensaje in st.session_state["chat_history"]:
            if rol == "👨‍💼":
                st.markdown(f"<div style='text-align: left; padding: 5px; background-color: #f1f1f1; border-radius: 10px;'>{rol} {mensaje}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: right; padding: 5px; background-color: #d1e7fd; border-radius: 10px;'>{rol} {mensaje}</div>", unsafe_allow_html=True)

        # Preguntas de la entrevista
        for pregunta, respuesta_esperada in st.session_state["preguntas_ordenadas"]:
            respuesta = st.text_input(f"{pregunta}", key=pregunta)
            if respuesta:
                st.session_state["chat_history"].append(("👤", respuesta))
                st.session_state["respuestas_usuario"][pregunta] = {"respuesta": respuesta, "esperada": respuesta_esperada}
                time.sleep(1)

        if st.button("📩 Enviar Entrevista"):
            feedback_total, porcentaje_aciertos = evaluar_respuestas(st.session_state["respuestas_usuario"])
            guardar_historial(nombre, documento, feedback_total, porcentaje_aciertos)

            # Mensaje final al postulante
            st.session_state["chat_history"].append(("📢", f"🎯 Puntaje final: **{porcentaje_aciertos:.2f}%**"))
            st.session_state["chat_history"].append(("📢", "📩 Sus respuestas han sido enviadas a Recursos Humanos de Minera CHINALCO."))

            # Informe a RRHH
            st.markdown("### 📑 Informe Enviado a Recursos Humanos")
            st.json({
                "nombre": nombre,
                "documento": documento,
                "puesto": st.session_state["puesto"]["nombre"],
                "puntaje_final": porcentaje_aciertos,
                "detalles": feedback_total
            })
