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

# LEER DATOS (Usamos el cliente nativo para tener control total de lectura/escritura)
client = conn.client
# Abrimos la planilla usando la URL limpia que configuraste en tus Secrets
spreadsheet = client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
# Seleccionamos la primera hoja (Hoja 1)
worksheet = spreadsheet.get_worksheet(0)

# Pasamos los datos a un DataFrame de Pandas para trabajarlo en la App
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Si la planilla está totalmente vacía en las columnas de control, aseguramos que existan
if 'Numeros' not in df.columns:
    st.error("No se encontró la columna 'Numeros' en la planilla de Google Sheets.")
    st.stop()

# PARCHE DE TIPOS: Forzamos a que todo sea tratado como texto (string)
df['Numeros'] = df['Numeros'].astype(str)

if 'Estado' not in df.columns:
    df['Estado'] = 'Disponible'
else:
    df['Estado'] = df['Estado'].astype(str).fillna('Disponible').replace('', 'Disponible')

if 'Llamado' not in df.columns:
    df['Llamado'] = 'No'
else:
    df['Llamado'] = df['Llamado'].astype(str).fillna('No').replace('', 'No')

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
    
    # Obtenemos el índice real/original (sumamos 2 porque en Google Sheets las filas empiezan en 1 y la fila 1 son los encabezados)
    idx_original_gsheet = int(df_pendientes.index[0]) + 2
    
    # Cartel visual si es una Revisita
    if estado_actual == 'Revisita':
        st.warning("⭐ ESTE NÚMERO ES UNA REVISITA")

    # Número Gigante con función de llamada
    st.markdown(f'<div class="numero-grande"><a href="tel:{numero_actual}" style="text-decoration:none; color:#1E3A8A;">{numero_actual}</a></div>', unsafe_allow_html=True)
    st.caption("👆 Toca el número desde el celular para llamar directamente")

    st.divider()

    # BOTONES DE ACCIÓN (Escriben directamente en la celda exacta de Google Sheets)
    if st.button("✅ Siguiente Número (Llamado Hecho)"):
        # Columna C es 'Llamado' (columna 3)
        worksheet.update_cell(idx_original_gsheet, 3, "Sí")
        st.toast("Progreso guardado en la nube.")
        st.rerun()

    if st.button("🚫 No existe / Fuera de servicio"):
        # Columna B es 'Estado' (columna 2) y Columna C es 'Llamado' (columna 3)
        worksheet.update_cell(idx_original_gsheet, 2, "Inexistente")
        worksheet.update_cell(idx_original_gsheet, 3, "Sí")
        st.error(f"Número {numero_actual} marcado como Inexistente.")
        st.rerun()

    if st.button("⭐ Marcar como Revisita para volver a llamar"):
        # Columna B es 'Estado' (columna 2)
        worksheet.update_cell(idx_original_gsheet, 2, "Revisita")
        st.success(f"Número {numero_actual} guardado como Revisita.")
        st.rerun()

else:
    st.balloons()
    st.success("¡Excelente trabajo! Se completaron todos los números de la lista.")
    if st.button("🔄 Reiniciar lista para una nueva vuelta"):
        # Borramos las columnas de control para arrancar de cero de forma masiva
        for i in range(2, total_numeros + 2):
            worksheet.update_cell(i, 2, "Disponible")
            worksheet.update_cell(i, 3, "No")
        st.rerun()
