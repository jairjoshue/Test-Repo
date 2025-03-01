import streamlit as st
import time

# Cargar estilos CSS para simular WhatsApp
st.markdown("""
    <style>
        /* Contenedor principal del chat */
        .chat-container {
            width: 100%;
            max-width: 500px;
            margin: auto;
            background: #f0f0f0;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            height: 500px;
            overflow-y: auto;
        }

        /* Mensajes del bot */
        .bot-message {
            background: #dcf8c6;
            color: black;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            max-width: 80%;
            display: inline-block;
        }

        /* Mensajes del usuario */
        .user-message {
            background: #ffffff;
            color: black;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            max-width: 80%;
            display: inline-block;
            align-self: flex-end;
        }

        /* Contenedor de cada mensaje */
        .message-container {
            display: flex;
            width: 100%;
            margin-bottom: 10px;
        }

        .bot-container {
            justify-content: flex-start;
        }

        .user-container {
            justify-content: flex-end;
        }

        /* Estilo del input de usuario */
        .input-container {
            display: flex;
            margin-top: 15px;
        }

        .input-text {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 14px;
            outline: none;
        }

        .send-button {
            background: #25D366;
            border: none;
            color: white;
            padding: 10px 15px;
            margin-left: 5px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }

        .send-button:hover {
            background: #1ebe57;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializar historial de chat en sesión si no existe
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "text": "Hola, bienvenido a la entrevista virtual de Minera CHINALCO."},
        {"role": "bot", "text": "Voy a realizarte algunas preguntas sobre tu experiencia y conocimientos."}
    ]

# Función para agregar mensajes al historial
def add_message(role, text):
    st.session_state.chat_history.append({"role": role, "text": text})

# Título del Chatbot
st.markdown("<h2>💬 Chat de Entrevista</h2>", unsafe_allow_html=True)

# Mostrar el contenedor de chat
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    if msg["role"] == "bot":
        st.markdown(f'<div class="message-container bot-container"><span class="bot-message">🤖 {msg["text"]}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="message-container user-container"><span class="user-message">👤 {msg["text"]}</span></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input de usuario
user_input = st.text_input("Escribe tu respuesta aquí:", key="user_input")

# Enviar mensaje con Enter
if user_input:
    add_message("user", user_input)  # Agregar mensaje del usuario
    time.sleep(1)  # Simula una pausa antes de la respuesta del bot
    add_message("bot", "Gracias por tu respuesta. Ahora dime...")  # Respuesta simulada del bot
    st.session_state.user_input = ""  # Limpiar input después de enviar
    st.rerun()  # Recargar la interfaz para mostrar los nuevos mensajes
