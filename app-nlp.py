import streamlit as st
import google.generativeai as genai

# Configurar la API de Gemini
API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
genai.configure(api_key=API_KEY)

# Definir el modelo a utilizar
#model = genai.GenerativeModel(model_name="gemini-1.5-pro")  # Última versión de Gemini
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Datos simulados de postulantes y preguntas
postulantes = [
    {"nombre": "Jairsinho Patiño Franco", "documento": "10010010", "codigo_puesto": "A1"},
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
# Inicializar estado de la aplicación
if "solicitudes_gemini" not in st.session_state:
    st.session_state["solicitudes_gemini"] = 0

if "entrevista_iniciada" not in st.session_state:
    st.session_state["entrevista_iniciada"] = False

# Función para validar postulantes
def validar_postulante(nombre, documento):
    for postulante in postulantes:
        if postulante["nombre"].lower() == nombre.lower() and postulante["documento"] == documento:
            return puestos.get(postulante["codigo_puesto"]), postulante["codigo_puesto"]
    return None, None

# Evaluación con Gemini (Usa Cache para evitar llamadas repetitivas)
@st.cache_data
def evaluar_respuesta_gemini(pregunta, respuesta, respuesta_esperada):
    if st.session_state["solicitudes_gemini"] >= 10:
        return "⚠️ Has alcanzado el límite de evaluaciones por sesión. Intenta más tarde."

    try:
        prompt = f"""
        Evalúa la respuesta del candidato en comparación con la respuesta esperada.
        Devuelve una puntuación (1: Correcto, 0.5: Parcialmente Correcto, 0: Incorrecto) y una explicación.
        Pregunta: {pregunta}
        Respuesta del candidato: {respuesta}
        Respuesta esperada: {respuesta_esperada}
        """
        
        response = model.generate_content(prompt)
        st.session_state["solicitudes_gemini"] += 1
        time.sleep(2)  # Previene sobrecarga en la API
        
        return response.text.strip()

    except google.api_core.exceptions.ResourceExhausted:
        return "❌ Límite de la API alcanzado. Intenta más tarde."

# Interfaz en Streamlit
st.title("🛠️ Chatbot de Entrevistas - Minera CHINALCO")
st.write("Simulador de entrevistas con evaluación de respuestas mediante IA.")

# Ingreso de datos del postulante
nombre = st.text_input("Ingrese su nombre completo:")
documento = st.text_input("Ingrese su documento de identidad:")

# Validar postulante
if st.button("Validar Postulante"):
    puesto, codigo_puesto = validar_postulante(nombre, documento)
    
    if puesto:
        st.session_state["puesto"] = puesto
        st.session_state["entrevista_iniciada"] = True
        st.success(f"✅ Validación exitosa. Usted está postulando para: **{puesto['nombre']}**")
    else:
        st.error("❌ No encontramos su información en nuestra base de datos. Para dudas, escriba a inforrhh@chinalco.com.pe")

# Iniciar la entrevista
if st.session_state["entrevista_iniciada"]:
    iniciar = st.checkbox("Acepto las reglas de la entrevista.")
    
    if iniciar:
        puesto = st.session_state["puesto"]
        st.subheader("📋 Preguntas Generales sobre la Empresa")
        puntaje_total = 0
        total_preguntas = len(preguntas_generales_empresa) + len(puesto["preguntas"])

        # Preguntas en orden con timer de 1 minuto entre cada una
        for i, (pregunta, respuesta_esperada) in enumerate(preguntas_generales_empresa.items()):
            st.write(f"📝 Pregunta {i + 1}: {pregunta}")
            respuesta = st.text_area(f"Responda aquí:", key=f"gen_{pregunta}")
            if st.button(f"Evaluar {pregunta[:20]}...", key=f"btn_{pregunta}"):
                evaluacion = evaluar_respuesta_gemini(pregunta, respuesta, respuesta_esperada)
                st.write(f"Evaluación: {evaluacion}")
                if "Correcto" in evaluacion:
                    puntaje_total += 1
                elif "Parcialmente Correcto" in evaluacion:
                    puntaje_total += 0.5
                time.sleep(60)  # Pausa de 1 minuto entre preguntas

        st.subheader("📊 Preguntas Técnicas del Puesto")
        for i, (pregunta, respuesta_esperada) in enumerate(puesto["preguntas"].items()):
            st.write(f"📝 Pregunta {i + 1}: {pregunta}")
            respuesta = st.text_area(f"Responda aquí:", key=f"tec_{pregunta}")
            if st.button(f"Evaluar {pregunta[:20]}...", key=f"btn_tec_{pregunta}"):
                evaluacion = evaluar_respuesta_gemini(pregunta, respuesta, respuesta_esperada)
                st.write(f"Evaluación: {evaluacion}")
                if "Correcto" in evaluacion:
                    puntaje_total += 1
                elif "Parcialmente Correcto" in evaluacion:
                    puntaje_total += 0.5
                time.sleep(60)  # Pausa de 1 minuto entre preguntas
        
        porcentaje_aciertos = (puntaje_total / total_preguntas) * 100
        st.success(f"🎯 Puntaje final: **{porcentaje_aciertos:.2f}%**")
        st.write("📩 Sus respuestas serán enviadas a Recursos Humanos para su evaluación.")
