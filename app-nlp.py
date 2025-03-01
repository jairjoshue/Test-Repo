import streamlit as st
import json
import random
import google.generativeai as genai

# Configurar API de Gemini (¡Reemplaza con tu clave!)
API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="gemini-pro")

# Datos simulados de postulantes y preguntas
postulantes = [
    {"nombre": "Jairsinho Patiño", "documento": "10010010", "codigo_puesto": "A1"},
    {"nombre": "Juan Perez", "documento": "20020020", "codigo_puesto": "A1"},
    {"nombre": "Pepe Guzman", "documento": "30030030", "codigo_puesto": "B2"},
    {"nombre": "Manuel Burga", "documento": "40040040", "codigo_puesto": "B2"},
    {"nombre": "Maria Cuadro", "documento": "50050050", "codigo_puesto": "C4"},
    {"nombre": "Jose Machicao", "documento": "60060060", "codigo_puesto": "C4"}
]

preguntas_generales_empresa = {
    "¿Qué conoce sobre Minera CHINALCO y su impacto en la minería peruana?": "Minera CHINALCO opera la mina Toromocho, destacándose por la innovación tecnológica y su enfoque en sostenibilidad.",
    "¿Cuáles considera que son los desafíos más importantes en la industria minera actualmente?": "Optimización de procesos, reducción del impacto ambiental y uso de tecnología avanzada."
}

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

# Función para validar postulantes
def validar_postulante(nombre, documento):
    for postulante in postulantes:
        if postulante["nombre"].lower() == nombre.lower() and postulante["documento"] == documento:
            return puestos.get(postulante["codigo_puesto"]), postulante["codigo_puesto"]
    return None, None

# Función para evaluar respuestas con Gemini
def evaluar_respuesta_gemini(pregunta, respuesta, respuesta_esperada):
    prompt = f"""
    Evalúa la respuesta del candidato en comparación con la respuesta esperada.
    Devuelve una puntuación (1: Correcto, 0.5: Parcialmente Correcto, 0: Incorrecto) y una explicación.
    Pregunta: {pregunta}
    Respuesta del candidato: {respuesta}
    Respuesta esperada: {respuesta_esperada}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

# Streamlit UI
st.title("🛠️ Chatbot de Entrevistas - Minera CHINALCO")
st.write("Simulador de entrevistas con evaluación de respuestas mediante IA.")

# Ingreso de datos del postulante
nombre = st.text_input("Ingrese su nombre completo:")
documento = st.text_input("Ingrese su documento de identidad:")

if st.button("Validar Postulante"):
    puesto, codigo_puesto = validar_postulante(nombre, documento)
    if puesto:
        st.success(f"✅ Validación exitosa. Usted está postulando para: **{puesto['nombre']}**")
        iniciar = st.checkbox("Acepto las reglas de la entrevista.")
        
        if iniciar:
            st.subheader("📋 Preguntas Generales sobre la Empresa")
            puntaje_total = 0
            total_preguntas = len(preguntas_generales_empresa) + len(puesto["preguntas"])
            
            for pregunta, respuesta_esperada in preguntas_generales_empresa.items():
                respuesta = st.text_area(f"📝 {pregunta}")
                if st.button(f"Evaluar {pregunta[:20]}..."):
                    evaluacion = evaluar_respuesta_gemini(pregunta, respuesta, respuesta_esperada)
                    st.write(f"Evaluación: {evaluacion}")
                    if "Correcto" in evaluacion:
                        puntaje_total += 1
                    elif "Parcialmente Correcto" in evaluacion:
                        puntaje_total += 0.5
            
            st.subheader("📊 Preguntas Técnicas del Puesto")
            for pregunta, respuesta_esperada in puesto["preguntas"].items():
                respuesta = st.text_area(f"📝 {pregunta}")
                if st.button(f"Evaluar {pregunta[:20]}..."):
                    evaluacion = evaluar_respuesta_gemini(pregunta, respuesta, respuesta_esperada)
                    st.write(f"Evaluación: {evaluacion}")
                    if "Correcto" in evaluacion:
                        puntaje_total += 1
                    elif "Parcialmente Correcto" in evaluacion:
                        puntaje_total += 0.5
            
            porcentaje_aciertos = (puntaje_total / total_preguntas) * 100
            st.success(f"🎯 Puntaje final: **{porcentaje_aciertos:.2f}%**")
            st.write("📩 Sus respuestas serán enviadas a Recursos Humanos para su evaluación.")
    else:
        st.error("❌ No encontramos su información en nuestra base de datos. Para dudas, escriba a inforrhh@chinalco.com.pe")



