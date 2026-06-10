import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
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

# CONEXIÓN NATIVA USANDO GOOGLE-AUTH DIRECTO
try:
    # 1. Recuperamos los datos del Service Account desde tus Secrets de Streamlit
    sec = st.secrets["connections"]["gsheets"]["service_account"]
    
    # 2. Armamos el diccionario limpio mapeando los datos del TOML
    creds_dict = {
        "type": sec["type"],
        "project_id": sec["project_id"],
        "private_key_id": sec["private_key_id"],
        "private_key": sec["private_key"],
        "client_email": sec["client_email"],
        "client_id": sec["client_id"],
        "auth_uri": sec["auth_uri"],
        "token_uri": sec["token_uri"],
        "auth_provider_x509_cert_url": sec["auth_provider_x509_cert_url"],
        "client_x509_cert_url": sec["client_x509_cert_url"],
        "universe_domain": sec.get("universe_domain", "googleapis.com")
    }
    
    # 3. Definimos los alcances (scopes) oficiales que exige Google para leer y escribir
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # 4. Generamos las credenciales nativas con la librería oficial de Google
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    
    # 5. Conectamos gspread de forma directa
    gc = gspread.authorize(credentials)
    
    # 6. Abrimos la planilla usando la URL de tus Secrets
    url_planilla = st.secrets["connections"]["gsheets"]["spreadsheet"]
    sh = gc.open_by_url(url_planilla)
    worksheet = sh.get_worksheet(0)
    
    # 7. Descargamos los datos a un DataFrame
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

except Exception as e:
    st.error(f"Error de conexión técnica directa: {e}")
    st.stop()

if df.empty:
    st.warning("La planilla está vacía o no tiene el formato correcto (columnas: Numeros, Estado, Llamado)")
    st.stop()

# PARCHE DE TIPOS Y LIMPIEZA
df['Numeros'] = df['Numeros'].astype(str)
df['Estado'] = df['Estado'].astype(str).fillna('Disponible').replace(['nan', ''], 'Disponible')
df['Llamado'] = df['Llamado'].astype(str).fillna('No').replace(['nan', ''], 'No')

# FILTRADO: Solo mostramos los números pendientes
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
    
    # Índice real de la fila en Google Sheets
    idx_original_gsheet = int(df_pendientes.index[0]) + 2
    
    if estado_actual == 'Revisita':
        st.warning("⭐ ESTE NÚMERO ES UNA REVISITA")

    st.markdown(f'<div class="numero-grande"><a href="tel:{numero_actual}" style="text-decoration:none; color:#1E3A8A;">{numero_actual}</a></div>', unsafe_allow_html=True)
    st.caption("👆 Toca el número desde el celular para llamar directamente")

    st.divider()

    # BOTONES DE ACCIÓN DIRECTA (Modifican las celdas en tiempo real)
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
