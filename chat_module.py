import streamlit as st

# Inicializar historial del chat en la sesión
def inicializar_chat():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            ("👨‍💼", "Hola, bienvenido a la entrevista virtual de Minera CHINALCO."),
            ("👨‍💼", "Voy a realizarte algunas preguntas sobre tu experiencia y conocimientos."),
        ]

# Mostrar los mensajes del chat en Streamlit
def mostrar_chat():
    st.markdown("<h2>💬 Ventana de Chat</h2>", unsafe_allow_html=True)
    
    chat_container = st.container()
    
    with chat_container:
        for rol, mensaje in st.session_state["chat_history"]:
            if rol == "👨‍💼":  # Entrevistador (mensaje alineado a la izquierda)
                st.markdown(f"<div style='text-align: left; padding: 5px; background-color: #f1f1f1; border-radius: 10px;'>{rol} {mensaje}</div>", unsafe_allow_html=True)
            else:  # Candidato (mensaje alineado a la derecha)
                st.markdown(f"<div style='text-align: right; padding: 5px; background-color: #d1e7fd; border-radius: 10px;'>{rol} {mensaje}</div>", unsafe_allow_html=True)

# Entrada de texto y envío de respuesta
def entrada_chat():
    respuesta_usuario = st.text_input("Escriba su respuesta aquí:")

    if st.button("📤 Enviar Respuesta"):
        if respuesta_usuario:
            st.session_state["chat_history"].append(("👤", respuesta_usuario))
            return respuesta_usuario
    return None
