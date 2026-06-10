import streamlit as st
import gspread
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

# CONEXIÓN NATIVA CON GSPREAD USANDO TUS SECRETS
try:
    # Autenticación con las credenciales del robot que tenés en Secrets
    credentials = st.secrets["connections"]["gsheets"]["service_account"]
    gc = gspread.service_account_from_dict(credentials)
    
    # Abrimos la planilla por su URL limpia
    url_planilla = st.secrets["connections"]["gsheets"]["spreadsheet"]
    spreadsheet = gc.open_by_url(url_planilla)
    worksheet = spreadsheet.get_worksheet(0) # Abre la primera hoja ("Hoja 1")
except Exception as e:
    st.error("Error al conectar con Google Sheets. Revisá tus Secrets.")
    st.stop()

# LEER DATOS REALES
data = worksheet.get_all_records()

if not data:
    st.warning("La planilla está vacía o no tiene el formato correcto (columnas: Numeros, Estado, Llamado)")
    st.stop()

df = pd.DataFrame(data)

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
    # Tomamos SIEMPRE el primer número disponible
    fila_actual = df_pendientes.iloc[0]
    numero_actual = fila_actual['Numeros']
    estado_actual = fila_actual['Estado']
    
    # Índice real en Google Sheets (las filas en Sheets empiezan en 1 y la fila 1 contiene los encabezados, por eso sumamos 2)
    idx_original_gsheet = int(df_pendientes.index[0]) + 2
    
    # Cartel visual si es una Revisita
    if estado_actual == 'Revisita':
        st.warning("⭐ ESTE NÚMERO ES UNA REVISITA")

    # Número Gigante con función de llamada
    st.markdown(f'<div class="numero-grande"><a href="tel:{numero_actual}" style="text-decoration:none; color:#1E3A8A;">{numero_actual}</a></div>', unsafe_allow_html=True)
    st.caption("👆 Toca el número desde el celular para llamar directamente")

    st.divider()

    # BOTONES DE ACCIÓN (Escriben directo en la celda exacta de Google Sheets)
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
        # Resetea las columnas completas de forma segura
        for i in range(2, total_numeros + 2):
            worksheet.update_cell(i, 2, "Disponible")
            worksheet.update_cell(i, 3, "No")
        st.rerun()
