import streamlit as st
from chat_module import inicializar_chat, mostrar_chat, entrada_chat

# Inicializar el chat en la sesión
inicializar_chat()

# Mostrar la ventana de chat
mostrar_chat()

# Capturar la respuesta del usuario
respuesta = entrada_chat()

if respuesta:
    # Aquí puedes agregar la lógica para generar la siguiente pregunta en base a la respuesta del usuario.
    st.session_state["chat_history"].append(("👨‍💼", "Gracias por tu respuesta. Ahora dime..."))
