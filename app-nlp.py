import google.generativeai as genai

API_KEY = "AIzaSyDoEksHdh7cJ-yY4cblNU15D84zfDkVxbM"
genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel(model_name="gemini-pro")
    response = model.generate_content("Hola, ¿cómo estás?")
    print(response.text)
except Exception as e:
    print(f"Error: {e}")

st.write(f"✅ Evaluación: {evaluacion}")  # Forzamos a Streamlit a mostrar el texto
st.text(evaluacion)  # Asegura que la salida se muestre correctamente
