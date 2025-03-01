import streamlit as st
import google.generativeai as genai

# Configurar API de Gemini
API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
genai.configure(api_key=API_KEY)

# Prueba rápida para ver si Gemini responde
st.subheader("🔍 Test de Conexión con Gemini")

try:
    model = genai.GenerativeModel(model_name="gemini-pro")
    test_response = model.generate_content("Dime una frase motivadora.")
    st.write(f"✅ Respuesta de prueba: {test_response.text}")  # Se muestra en Streamlit
except Exception as e:
    st.error(f"❌ Error al conectar con Gemini: {e}")  # Se muestra en pantalla
