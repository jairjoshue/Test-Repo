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

# Función para consultar a Gemini
def consultar_gemini(mensaje):
    if GEMINI_AVAILABLE:
        try:
            response = model.generate_content(mensaje)
            return response.text if response and response.text else "Lo siento, no puedo responder en este momento."
        except Exception as e:
            print("Error en Gemini:", e)
            return "Ocurrió un error al procesar la respuesta."
    else:
        return "El servicio de IA no está disponible."

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
if prompt := st.chat_input("Escribe tu pregunta..."):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Obtener respuesta de Gemini
    respuesta = consultar_gemini(prompt)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    
    # Mostrar respuesta en el chat
    with st.chat_message("assistant"):
        st.markdown(respuesta)
