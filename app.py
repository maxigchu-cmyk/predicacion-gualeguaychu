import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURACIÓN
st.set_page_config(page_title="Predicación Sincronizada", layout="centered")

# Conexión con Google Sheets
# Nota: La URL de la planilla se configura en los "Secrets" de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# LEER DATOS
df = conn.read(ttl="0") # ttl="0" para que siempre lea la versión más nueva

# LÓGICA DE PERSISTENCIA
# Buscamos el primer número que NO tenga estado 'Llamado' o 'Inexistente'
# Agregamos una columna 'Llamado' en tu Excel si no existe
if 'Llamado' not in df.columns:
    df['Llamado'] = False

# Filtramos los que faltan llamar y que existen
df_pendientes = df[(df['Llamado'] == False) & (df['Estado'] != 'Inexistente')]

st.title("📞 Agenda Compartida")

if not df_pendientes.empty:
    # SIEMPRE mostramos el primero de la lista de pendientes
    fila_actual = df_pendientes.iloc[0]
    numero = str(fila_actual['Numeros'])
    indice_original = df_pendientes.index[0]

    st.markdown(f"<h1 style='text-align:center; font-size:70px;'>{numero}</h1>", unsafe_allow_html=True)
    st.write(f"Progreso global: {len(df) - len(df_pendientes)} de {len(df)} números.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Ya llamé (Pasar al siguiente)"):
            # Actualizamos la planilla directamente
            df.at[indice_original, 'Llamado'] = True
            conn.update(data=df)
            st.success("Progreso guardado para todos.")
            st.rerun()

    with col2:
        if st.button("🚫 No existe"):
            df.at[indice_original, 'Estado'] = 'Inexistente'
            df.at[indice_original, 'Llamado'] = True
            conn.update(data=df)
            st.warning("Número marcado como inexistente globalmente.")
            st.rerun()
else:
    st.balloons()
    st.success("¡Increíble! Entre todos terminaron la lista.")
    if st.button("🔄 Reiniciar lista para todos"):
        df['Llamado'] = False
        conn.update(data=df)
        st.rerun()
