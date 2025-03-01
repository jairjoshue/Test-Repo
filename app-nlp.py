import streamlit as st

# Título de la aplicación
st.title("🚀 Mi Primera App en Streamlit")

# Texto de bienvenida
st.write("¡Hola, bienvenido a mi primera aplicación en Streamlit!")

# Input del usuario
nombre = st.text_input("Escribe tu nombre:")

# Botón para saludar
if st.button("Saludar"):
    st.write(f"👋 ¡Hola, {nombre}! Bienvenido a Streamlit Cloud.")

# Mostrar una gráfica simple
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set_title("Ejemplo de Gráfico con Matplotlib")

st.pyplot(fig)

# Finalizar con un mensaje
st.write("Gracias por probar esta app. 🚀")

