import streamlit as st
import google.generativeai as genai
import time

# Cargar CSS personalizado
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Llamar la función al inicio
load_css()

# Configurar la API de Gemini
API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
genai.configure(api_key=API_KEY)

# Definir el modelo a utilizar
#model = genai.GenerativeModel(model_name="gemini-1.5-pro")  # Última versión de Gemini
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Datos simulados de postulantes y preguntas
postulantes = [
    {"nombre": "Jairsinho Patiño", "documento": "10010010", "codigo_puesto": "A1"},
    {"nombre": "Juan Perez", "documento": "20020020", "codigo_puesto": "A1"},
    {"nombre": "Pepe Guzman", "documento": "30030030", "codigo_puesto": "B2"},
    {"nombre": "Manuel Burga", "documento": "40040040", "codigo_puesto": "B2"},
    {"nombre": "Maria Cuadro", "documento": "50050050", "codigo_puesto": "C4"},
    {"nombre": "Jose Machicao", "documento": "60060060", "codigo_puesto": "C4"}
]

# Preguntas generales sobre la empresa
preguntas_generales_empresa = {
    "¿Qué conoce sobre Minera CHINALCO y su impacto en la minería peruana?": "Minera CHINALCO opera la mina Toromocho, destacándose por la innovación tecnológica y su enfoque en sostenibilidad.",
    "¿Cuáles considera que son los desafíos más importantes en la industria minera actualmente?": "Optimización de procesos, reducción del impacto ambiental y uso de tecnología avanzada."
}

# Definir los puestos y preguntas técnicas
puestos = {
    "A1": {
        "nombre": "Analista de Datos",
        "descripcion": "Analizar datos de producción minera y desarrollar reportes en Power BI.",
        "preguntas": {
            "Explique cómo usaría Power BI para mejorar el análisis de producción minera.": "Power BI permite visualizar datos en tiempo real para una mejor toma de decisiones.",
            "¿Cómo manejaría un gran volumen de datos de sensores en la mina?": "Utilizaría Big Data y almacenamiento en la nube.",
            "Describa un caso de uso en minería donde el Machine Learning pueda optimizar procesos.": "Predicción de fallos en maquinaria para mantenimiento preventivo."
        }
    }
}

# Estado de la aplicación
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

# Evaluación con Gemini
def evaluar_respuestas_todas(respuestas_usuario):
    feedback_total = {}
    puntaje_total = 0
    total_preguntas = len(respuestas_usuario)

    for pregunta, datos in respuestas_usuario.items():
        respuesta = datos["respuesta"]
        respuesta_esperada = datos["esperada"]
        prompt = f"""
        Evalúa la respuesta del candidato en comparación con la respuesta esperada.
        Devuelve una puntuación (1: Correcto, 0.5: Parcialmente Correcto, 0: Incorrecto) y una breve justificación.
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

# UI Mejorada
st.image("https://www.chinalco.com.pe/wp-content/uploads/2020/08/logo-chinalco-2.png", width=200)
st.markdown("<h1>Chatbot de Entrevistas - Minera CHINALCO</h1>", unsafe_allow_html=True)
st.write("<p style='text-align: center;'>Simulador de entrevistas con IA</p>", unsafe_allow_html=True)

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
    iniciar = st.checkbox("Acepto las reglas de la entrevista.")
    
    if iniciar:
        puesto = st.session_state["puesto"]
        st.markdown("<h2>📝 Preguntas Generales</h2>", unsafe_allow_html=True)
        
        for pregunta in preguntas_generales_empresa.keys():
            st.markdown(f"<div class='question-box'><h3>{pregunta}</h3></div>", unsafe_allow_html=True)
            respuesta = st.text_area(f"Responda aquí:", key=pregunta)
            st.session_state["respuestas_usuario"][pregunta] = {"respuesta": respuesta, "esperada": preguntas_generales_empresa[pregunta]}

        st.markdown("<h2>📊 Preguntas Técnicas</h2>", unsafe_allow_html=True)

        for pregunta in puesto["preguntas"].keys():
            st.markdown(f"<div class='question-box'><h3>{pregunta}</h3></div>", unsafe_allow_html=True)
            respuesta = st.text_area(f"Responda aquí:", key=pregunta)
            st.session_state["respuestas_usuario"][pregunta] = {"respuesta": respuesta, "esperada": puesto["preguntas"][pregunta]}

        # Botón para enviar todas las respuestas
        if st.button("📩 Enviar Entrevista y Obtener Feedback"):
            feedback_total, porcentaje_aciertos = evaluar_respuestas_todas(st.session_state["respuestas_usuario"])
            st.success(f"🎯 Puntaje final: **{porcentaje_aciertos:.2f}%**")
            st.write("📩 Sus respuestas serán enviadas a Recursos Humanos para su evaluación.")

            # Mostrar feedback detallado
            for pregunta, datos in feedback_total.items():
                st.markdown(f"<div class='feedback-box'><h3>{pregunta}</h3>", unsafe_allow_html=True)
                st.write(f"✅ Respuesta: {datos['respuesta_usuario']}")
                st.write(f"📊 Evaluación: {datos['evaluacion']}")
                st.write(f"🎯 Puntaje: {datos['puntaje']}/1")
                st.markdown("</div>", unsafe_allow_html=True)
