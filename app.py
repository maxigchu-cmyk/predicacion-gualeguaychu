import streamlit as st
import gspread
import pandas as pd
import json

# CONFIGURACIÓN VISUAL
st.set_page_config(page_title="Predicación Sincronizada", layout="centered")

st.markdown("""
    <style>
    .numero-grande { font-size: 70px !important; font-weight: bold; color: #1E3A8A; text-align: center; margin: 10px 0; }
    .stButton>button { width: 100%; height: 75px; font-size: 24px !important; border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📞 Agenda Compartida")

# CONEXIÓN DIRECTA CORRIGIENDO LAS BARRAS EN MEMORIA
try:
    # 1. Cargamos el archivo JSON tal cual está en el repositorio
    with open("claves.json", "r") as f:
        creds_dict = json.load(f)
    
    # 2. PARCHE CLAVE: Reemplazamos la combinación de texto '\\n' por un salto de línea real '\n'
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    # 3. Nos autenticamos con el diccionario ya corregido y limpio
    gc = gspread.service_account_from_dict(creds_dict)
    
    # Buscamos la URL desde tus Secrets de Streamlit
    url_planilla = st.secrets["connections"]["gsheets"]["spreadsheet"]
    spreadsheet = gc.open_by_url(url_planilla)
    worksheet = spreadsheet.get_worksheet(0)
except Exception as e:
    st.error(f"Error de conexión técnica: {e}")
    st.stop()

# LEER DATOS REALES
data = worksheet.get_all_records()

if not data:
    st.warning("La planilla está vacía o no tiene columnas (Numeros, Estado, Llamado)")
    st.stop()

df = pd.DataFrame(data)

# PARCHE DE TIPOS
df['Numeros'] = df['Numeros'].astype(str)

if 'Estado' not in df.columns:
    df['Estado'] = 'Disponible'
else:
    df['Estado'] = df['Estado'].astype(str).fillna('Disponible').replace('', 'Disponible')

if 'Llamado' not in df.columns:
    df['Llamado'] = 'No'
else:
    df['Llamado'] = df['Llamado'].astype(str).fillna('No').replace('', 'No')

# FILTRADO: Solo pendientes
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
    fila_actual = df_pendientes.iloc[0]
    numero_actual = fila_actual['Numeros']
    estado_actual = fila_actual['Estado']
    
    idx_original_gsheet = int(df_pendientes.index[0]) + 2
    
    if estado_actual == 'Revisita':
        st.warning("⭐ ESTE NÚMERO ES UNA REVISITA")

    st.markdown(f'<div class="numero-grande"><a href="tel:{numero_actual}" style="text-decoration:none; color:#1E3A8A;">{numero_actual}</a></div>', unsafe_allow_html=True)
    st.caption("👆 Toca el número desde el celular para llamar directamente")

    st.divider()

    # BOTONES DE ACCIÓN (Escriben directo en las celdas de Google Sheets)
    if st.button("✅ Siguiente Número (Llamado Hecho)"):
        worksheet.update_cell(idx_original_gsheet, 3, "Sí")
        st.toast("Progreso guardado en la nube.")
        st.rerun()

    if st.button("🚫 No existe / Fuera de servicio"):
        worksheet.update_cell(idx_original_gsheet, 2, "Inexistente")
        worksheet.update_cell(idx_original_gsheet, 3, "Sí")
        st.error(f"Número {numero_actual} marcado como Inexistente.")
        st.rerun()

    if st.button("⭐ Marcar como Revisita para volver a llamar"):
        worksheet.update_cell(idx_original_gsheet, 2, "Revisita")
        st.success(f"Número {numero_actual} guardado como Revisita.")
        st.rerun()

else:
    st.balloons()
    st.success("¡Excelente trabajo! Se completaron todos los números de la lista.")
    if st.button("🔄 Reiniciar lista para una nueva vuelta"):
        for i in range(2, total_numeros + 2):
            worksheet.update_cell(i, 2, "Disponible")
            worksheet.update_cell(i, 3, "No")
        st.rerun()
