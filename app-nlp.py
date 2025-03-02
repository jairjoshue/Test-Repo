import streamlit as st
import json
import random
import datetime
import pandas as pd
import google.generativeai as genai
import re
# Configurar API de Gemini
try:
    genai.configure(api_key="AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM")
    model = genai.GenerativeModel("gemini-1.5-flash")
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    print("Error al configurar Gemini:", e)

# Función para consultar a Gemini por pregunta
def consultar_gemini(pregunta, respuesta_usuario, respuesta_esperada):
    if GEMINI_AVAILABLE:
        consulta = (
            f"Pregunta: {pregunta}\n"
            f"Respuesta usuario: {respuesta_usuario}\n"
            f"Respuesta esperada: {respuesta_esperada}\n"
            f"En la primera linea evalúa la respuesta con 0 si no cumple, 0.5 si cumple parcialmente, 1 si cumple bien."
            f"En una segunda linea explica brevemente y con solo una sola linea usandos menos de 20 palabras el porqué del puntaje y en otra linea analiza el sentimiento de la respuesta en menos de 20 palabras."
        )
        try:
            response = model.generate_content(consulta)
            return response.text if response and response.text else "Error en evaluación"
        except Exception as e:
            print("Error en Gemini:", e)
            return "Error en procesamiento"
    else:
        return "Gemini no disponible"
        
# Función para generar una repregunta con Gemini
def generar_repregunta(pregunta, respuesta_usuario):
    """
    Genera una repregunta basada en la respuesta del usuario para clarificar o expandir su respuesta.
    """
    if GEMINI_AVAILABLE:
        consulta = (
            f"Pregunta inicial: {pregunta}\n"
            f"Respuesta dada por el usuario: {respuesta_usuario}\n"
            f"Genera una repregunta breve para clarificar o ampliar la respuesta del usuario."
        )
        try:
            response = model.generate_content(consulta)
            return response.text.strip() if response and response.text else "Por favor, amplía tu respuesta con más detalles."
        except Exception as e:
            print("Error en Gemini:", e)
            return "Error al generar repregunta."
    else:
        return "No se pudo generar una repregunta en este momento."

def generar_informe(postulante, respuestas):
    """
    Genera un informe estructurado con el puntaje obtenido, feedback resumido y análisis de sentimientos.
    Retorna:
    - informe (str): El informe estructurado con la evaluación.
    - puntajes (list): Lista de puntajes individuales obtenidos por el postulante.
    """
    puntajes = []
    feedbacks = []

    for r in respuestas:
        resultado = consultar_gemini(r['pregunta'], r['respuesta_usuario'], r['respuesta_esperada']).strip()
        puntaje = extraer_puntaje(resultado)
        puntajes.append(puntaje)

        # Separar explicación y análisis de sentimientos
        lineas = resultado.split("\n")
        explicacion_resumida = lineas[2]  # Tomar solo la primera línea como explicación breve
        analisis_sentimiento = lineas[4] #next((linea for linea in lineas if "Sentimiento" in linea), "Sin análisis de sentimiento.")

        feedbacks.append(f"✅ **{r['pregunta']}**\n"
                         f"- **Puntaje:** {puntaje} ⭐\n"
                         f"- **Explicación:** {explicacion_resumida}\n"
                         f"- **Análisis de Sentimiento:** {analisis_sentimiento}")

    # Cálculo de puntaje final
    puntaje_total = sum(puntajes)
    puntaje_maximo = len(respuestas) if respuestas else 1  # Evitar división entre 0
    promedio = round((puntaje_total / puntaje_maximo) * 100, 2)  # Convertir a porcentaje

    # Generación del informe final
    informe = f"""
    **📌 Informe de Evaluación**\n\n
    **Nombre:** {postulante['nombre']}\n\n
    **Documento:** {postulante['documento']}\n\n
    **Puesto:** {postulante['codigo_puesto']}\n\n
    **Fecha:** {datetime.datetime.now().strftime('%d/%m/%Y')}\n\n
    **Resultados**
    {'\n\n'.join(feedbacks)}

    **🎯 Puntaje Final:** {puntaje_total}/{puntaje_maximo} ({promedio}%)
    """
    
    return informe, puntajes  # Retornar informe y lista de puntajes



def extraer_puntaje(resultado):
    """
    Extrae el puntaje devuelto por Gemini (0, 0.5 o 1).
    Si el resultado no tiene un número válido, se asigna 0.0.
    """
    match = re.search(r'(\d+(\.\d+)?)', resultado)  # Busca un número decimal o entero
    if match:
        return float(match.group(1))  # Convierte el primer número encontrado en float
    return 0.0  # Si no hay número, se asigna 0.0


# Función para mostrar mensajes en el chat
def mostrar_mensaje(rol, mensaje):
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if st.session_state.messages and st.session_state.messages[-1]["content"] == mensaje:
        return  # Evitar duplicados consecutivos
    with st.chat_message(rol):
        st.markdown(mensaje)
    st.session_state.messages.append({"role": rol, "content": mensaje})
    
# Cargar datos desde archivos JSON
with open("postulantes.json", "r") as f:
    postulantes = json.load(f)
with open("puestos.json", "r") as f:
    puestos = json.load(f)
with open("preguntas_generales.json", "r") as f:
    preguntas_generales = json.load(f)

# Inicializar variables en la sesión
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "postulante" not in st.session_state:
        st.session_state.postulante = None
    if "df_preguntas" not in st.session_state:
        st.session_state.df_preguntas = pd.DataFrame(columns=["pregunta", "respuesta_esperada"])
    if "indice_pregunta" not in st.session_state:
        st.session_state.indice_pregunta = 0
    if "respuestas" not in st.session_state:
        st.session_state.respuestas = []
    if "acepto_terminos" not in st.session_state:
        st.session_state.acepto_terminos = False
    if "fase" not in st.session_state:
        st.session_state.fase = "inicio"

init_session()

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Mostrar mensaje de bienvenida con lista de documentos de prueba solo una vez
if "mostro_documentos_prueba" not in st.session_state:
    st.session_state.mostro_documentos_prueba = False

if not st.session_state.mostro_documentos_prueba:
    documentos_prueba = "\n".join([f"- {p['documento']} ({p['nombre']})" for p in postulantes])
    mostrar_mensaje("assistant", "Bienvenido al proceso de entrevista. Esta es una prueba de validación. Puedes utilizar los siguientes documentos para probar el sistema:\n\n *" + documentos_prueba + "*")
    st.session_state.mostro_documentos_prueba = True

# Validación del postulante
if st.session_state.fase == "inicio":
    mostrar_mensaje("assistant", "Bienvenido a la entrevista de Minera CHINALCO. Esta entrevista es confidencial y sus datos serán tratados con estricta privacidad. Ingresa tu número de documento para validar tu registro.")
    doc_input = st.chat_input("Ingresa tu número de documento")
    if doc_input:
        mostrar_mensaje("user", doc_input)
        postulante = next((p for p in postulantes if p["documento"] == doc_input), None)
        if postulante:
            st.session_state.postulante = postulante
            puesto_codigo = postulante["codigo_puesto"]
            mostrar_mensaje("assistant", f"Bienvenido **{postulante['nombre']}**. Postulas al puesto **{puestos[puesto_codigo]['nombre']}**. Acepta los términos para continuar.")
            st.session_state.fase = "esperando_terminos"
            st.rerun()
        else:
            mostrar_mensaje("assistant", "Tu documento no está registrado. Contacta con RRHH en infoprocesosrrhh@chinalco.com.pe.")
            st.stop()

# Aceptación de términos
if st.session_state.fase == "esperando_terminos":
    if st.button("Acepto los términos"):
        mostrar_mensaje("user", "Acepto los términos")
        st.session_state.acepto_terminos = True
        st.session_state.fase = "preguntas"
        st.rerun()

# Cargar preguntas fijas
if st.session_state.fase == "preguntas" and st.session_state.df_preguntas.empty:
    todas_preguntas = {**preguntas_generales}
    puesto_codigo = st.session_state.postulante["codigo_puesto"]
    if puesto_codigo in puestos:
        todas_preguntas.update(puestos[puesto_codigo]["preguntas"])
    st.session_state.df_preguntas = pd.DataFrame(list(todas_preguntas.items()), columns=["pregunta", "respuesta_esperada"])
    st.session_state.indice_pregunta = 0
    st.rerun()

# Navegación por preguntas sin repeticiones
#if st.session_state.fase == "preguntas" and st.session_state.indice_pregunta < len(st.session_state.df_preguntas):
#    pregunta_actual = st.session_state.df_preguntas.iloc[st.session_state.indice_pregunta]["pregunta"]
#    if "pregunta_mostrada" not in st.session_state or st.session_state.pregunta_mostrada != pregunta_actual:
#        mostrar_mensaje("assistant", f"Pregunta {st.session_state.indice_pregunta + 1}: {pregunta_actual}")
#        st.session_state.pregunta_mostrada = pregunta_actual
#    respuesta_usuario = st.chat_input("Tu respuesta")
#    if respuesta_usuario:
#        mostrar_mensaje("user", respuesta_usuario)
#        st.session_state.respuestas.append({
#            "pregunta": pregunta_actual,
#            "respuesta_usuario": respuesta_usuario,
#            "respuesta_esperada": st.session_state.df_preguntas.iloc[st.session_state.indice_pregunta]["respuesta_esperada"]
#        })
#        st.session_state.indice_pregunta += 1
#        if st.session_state.indice_pregunta >= len(st.session_state.df_preguntas):
#            st.session_state.fase = "evaluacion"
#        st.rerun()

# Navegación por preguntas con repregunta de Gemini
if st.session_state.fase == "preguntas" and st.session_state.indice_pregunta < len(st.session_state.df_preguntas):
    pregunta_actual = st.session_state.df_preguntas.iloc[st.session_state.indice_pregunta]["pregunta"]

    # Si es la primera vez que se muestra la pregunta, la guardamos
    if "pregunta_mostrada" not in st.session_state or st.session_state.pregunta_mostrada != pregunta_actual:
        mostrar_mensaje("assistant", f"Pregunta {st.session_state.indice_pregunta + 1}: {pregunta_actual}")
        st.session_state.pregunta_mostrada = pregunta_actual
        st.session_state.respuesta_parcial = None  # Inicializamos la respuesta parcial

    # Si aún no se ha respondido la primera vez
    if st.session_state.respuesta_parcial is None:
        respuesta_usuario = st.chat_input("Tu respuesta (máx. 50 palabras)")
        if respuesta_usuario:
            mostrar_mensaje("user", respuesta_usuario)
            st.session_state.respuesta_parcial = respuesta_usuario  # Guardamos la primera respuesta
            repregunta = generar_repregunta(pregunta_actual, respuesta_usuario)
            mostrar_mensaje("assistant", f"🤔 {repregunta}")  # Mostramos la repregunta
            st.rerun()
    else:
        # Obtener respuesta a la repregunta
        respuesta_repregunta = st.chat_input("Respuesta a la repregunta (máx. 50 palabras)")
        if respuesta_repregunta:
            mostrar_mensaje("user", respuesta_repregunta)
            
            # Concatenamos ambas respuestas para tener una única respuesta final
            respuesta_final = f"{st.session_state.respuesta_parcial} {respuesta_repregunta}"
            st.session_state.respuestas.append({
                "pregunta": pregunta_actual,
                "respuesta_usuario": respuesta_final,
                "respuesta_esperada": st.session_state.df_preguntas.iloc[st.session_state.indice_pregunta]["respuesta_esperada"]
            })
            
            # Pasar a la siguiente pregunta
            st.session_state.indice_pregunta += 1
            st.session_state.respuesta_parcial = None  # Reiniciar la variable para la siguiente pregunta
            
            if st.session_state.indice_pregunta >= len(st.session_state.df_preguntas):
                st.session_state.fase = "evaluacion"
            st.rerun()

# Evaluación de preguntas de forma individual
#if st.session_state.fase == "evaluacion":
#    puntajes = []
#    feedback = []
#    for r in st.session_state.respuestas:
#        resultado = consultar_gemini(r['pregunta'], r['respuesta_usuario'], r['respuesta_esperada']).strip()
#        puntaje = 0
#        try:
#            puntaje = float(resultado.split()[0]) if resultado[0].isdigit() else 0
#        except ValueError:
#            puntaje = 0
#        puntajes.append(puntaje)
#        motivo = resultado[2:].strip() if len(resultado) > 2 else "Sin evaluación"
#        feedback.append(f"✅ {r['pregunta']}\n**Puntaje:** {puntaje} ⭐\n**Motivo:** {motivo}")
#    
#    total_puntaje = sum(puntajes)
#    mostrar_mensaje("assistant", "\n\n".join(feedback) + f"\n\n🎯 **Puntaje final: {total_puntaje}/{len(puntajes)}**")
#    st.session_state.clear()
#    st.session_state.clear()
if st.session_state.fase == "evaluacion":
    informe, puntajes = generar_informe(st.session_state.postulante, st.session_state.respuestas)
    mostrar_mensaje("assistant", informe)
    
    # Verificar que puntajes no esté vacío antes de calcular promedio
    if len(puntajes) > 0:
        promedio_puntaje = sum(puntajes) / len(puntajes)
    else:
        promedio_puntaje = 0

    # Mostrar conclusión basada en puntaje final
    if promedio_puntaje >= 0.7:
        mostrar_mensaje("assistant", "✅ **El postulante ha demostrado un buen nivel de conocimientos.**")
    else:
        mostrar_mensaje("assistant", "⚠️ **El postulante necesita reforzar sus conocimientos antes de continuar con el proceso.**")

    # No limpiar la sesión inmediatamente
    st.stop()

