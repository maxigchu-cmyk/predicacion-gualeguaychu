import streamlit as st
import pandas as pd

# CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Agenda Predicación", page_icon="📞", layout="centered")

st.markdown("""
    <style>
    .numero-grande { font-size: 70px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin: 10px 0; }
    .stButton>button { width: 100%; height: 75px; font-size: 24px !important; border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📞 Agenda de Predicación")

# CARGA DE DATOS
with st.sidebar:
    st.header("📁 Base de Datos")
    archivo = st.file_uploader("Sube el archivo de números (CSV)", type=["csv"])
    
    if archivo:
        if 'db' not in st.session_state:
            df = pd.read_csv(archivo)
            if 'Estado' not in df.columns:
                df['Estado'] = 'Disponible'
            st.session_state.db = df
            st.session_state.indice = 0
            st.success("¡Base cargada!")

if 'db' not in st.session_state:
    st.info("Por favor, sube el archivo CSV en la barra lateral para comenzar.")
    st.stop()

# LÓGICA DE FILTRADO
df_activos = st.session_state.db[st.session_state.db['Estado'] != 'Inexistente'].reset_index(drop=True)
total = len(df_activos)

# PROGRESO
actual = st.session_state.indice + 1 if total > 0 else 0
st.write(f"**Progreso:** {actual} de {total} números")
st.progress(st.session_state.indice / total if total > 0 else 1.0)

# INTERFAZ PRINCIPAL
if st.session_state.indice < total:
    fila = df_activos.iloc[st.session_state.indice]
    num = str(fila['Numeros'])
    
    # Número Gigante
    st.markdown(f'<div class="numero-grande"><a href="tel:{num}" style="text-decoration:none; color:#1E3A8A;">{num}</a></div>', unsafe_allow_html=True)
    st.caption("👆 Toca el número para llamar")

    # Botones de Navegación
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ Anterior"):
            if st.session_state.indice > 0:
                st.session_state.indice -= 1
                st.rerun()
    with c2:
        if st.button("Siguiente ➡️"):
            if st.session_state.indice < total - 1:
                st.session_state.indice += 1
                st.rerun()

    st.divider()

    # Botones de Acción
    if st.button("🚫 No existe / Fuera de servicio"):
        idx_original = st.session_state.db[st.session_state.db['Numeros'] == int(num)].index
        st.session_state.db.at[idx_original[0], 'Estado'] = 'Inexistente'
        st.toast(f"Número {num} eliminado de la lista.")
        st.rerun()

    if st.button("⭐ Marcar como Revisita"):
        idx_original = st.session_state.db[st.session_state.db['Numeros'] == int(num)].index
        st.session_state.db.at[idx_original[0], 'Estado'] = 'Revisita'
        st.toast("Guardado como revisita.")
        st.rerun()
else:
    st.success("¡Vuelta completa!")
    if st.button("🔄 Reiniciar"):
        st.session_state.indice = 0
        st.rerun()

# GUARDAR CAMBIOS
with st.sidebar:
    st.divider()
    csv_final = st.session_state.db.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Avances", csv_final, "progreso.csv", "text/csv")