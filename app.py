import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Predicación Sincronizada", layout="centered")

st.markdown("""
    <style>
    .numero-grande { font-size: 70px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin: 10px 0; }
    .stButton>button { width: 100%; height: 75px; font-size: 24px !important; border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📞 Agenda Compartida")

# CONEXIÓN CON GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# LEER DATOS (ttl="0" para actualizar en tiempo real)
df = conn.read(ttl="0")

# PARCHE DE TIPOS: Forzamos a que todo sea tratado como texto (string)
df['Numeros'] = df['Numeros'].astype(str)
df['Estado'] = df['Estado'].astype(str).fillna('Disponible').replace('nan', 'Disponible')
df['Llamado'] = df['Llamado'].astype(str).fillna('No').replace('nan', 'No')

# FILTRADO: Solo mostramos los números que NO han sido llamados y que NO están inexistentes
df_pendientes = df[(df['Llamado'] != 'Sí') & (df['Estado'] != 'Inexistente')]

# MÉTRICAS DE PROGRESO
total_numeros = len(df)
quedan_pendientes = len(df_pendientes)
llamados_ok = total_numeros - quedan_pendientes

st.write(f"**Progreso global:** {llamados_ok} de {total_numeros} números procesados")
st.progress(llamados_ok / total_numeros if total_numeros > 0 else 1.0)

st.divider()

# INTERFAZ PRINCIPAL
if not df_pendientes.empty:
    # Tomamos SIEMPRE el primer número disponible de la lista de pendientes
    fila_actual = df_pendientes.iloc[0]
    numero_actual = fila_actual['Numeros']
    estado_actual = fila_actual['Estado']
    
    # Obtenemos el índice real/original en la planilla completa de Google Sheets
    idx_original = df_pendientes.index[0]
    
    # Cartel visual si es una Revisita
    if estado_actual == 'Revisita':
        st.warning("⭐ ESTE NÚMERO ES UNA REVISITA")

    # Número Gigante con función de llamada
    st.markdown(f'<div class="numero-grande"><a href="tel:{numero_actual}" style="text-decoration:none; color:#1E3A8A;">{numero_actual}</a></div>', unsafe_allow_html=True)
    st.caption("👆 Toca el número desde el celular para llamar directamente")

    st.divider()

    # BOTONES DE ACCIÓN
    if st.button("✅ Siguiente Número (Llamado Hecho)"):
        df.at[idx_original, 'Llamado'] = 'Sí'
        conn.update(data=df)
        st.toast("Progreso guardado en la nube.")
        st.rerun()

    if st.button("🚫 No existe / Fuera de servicio"):
        df.at[idx_original, 'Estado'] = 'Inexistente'
        df.at[idx_original, 'Llamado'] = 'Sí'
        conn.update(data=df)
        st.error(f"Número {numero_actual} marcado como Inexistente.")
        st.rerun()

    if st.button("⭐ Marcar como Revisita para volver a llamar"):
        df.at[idx_original, 'Estado'] = 'Revisita'
        conn.update(data=df)
        st.success(f"Número {numero_actual} guardado como Revisita.")
        st.rerun()

else:
    st.balloons()
    st.success("¡Excelente trabajo! Se completaron todos los números de la lista.")
    if st.button("🔄 Reiniciar lista para una nueva vuelta"):
        df['Llamado'] = 'No'
        df['Estado'] = 'Disponible'
        conn.update(data=df)
        st.rerun()
