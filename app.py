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

# TU ARCHIVO JSON NUEVO INTEGRADO
creds_dict = {
  "type": "service_account",
  "project_id": "corded-aquifer-402514",
  "private_key_id": "b2a53e05a0d7afdfb7abf0a9a37ad4123f137c38",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDGXB1iz5RFMUgN\nnpuD3EYDTVuOJy/VH6dS9ityTuZ7ICjcKXchMHfHAsaAFV8y2KYOJYfaSKZSn4P9\nBQ0NYduibUZi9X4C7uEKcUf+luP3XBK7Eucyn5XcBrUv3sbpjgY7+b0bQgPLI0B2\nOpGPBas/J0WqF6KcRwTK5RJqkBtRnKX4aKtCmXVXioMNZZPdnKPrUH/pjZLHedXX\ngUETqfq53nTVYlyFy6R1WcEtMpZ1+e5x8DuZyAEmr2Si0/9JvGMcAdRlieiK8wdC\nj/OKaRUousXyt4j09se3Dp1kS8lbxEueEeGl1MnQNebZb3D0DGKdGfPqh8RNn3lX\ngHUbiGZHAgMBAAECggEABM2HLUokZ2vS4vgzq2+Ccc2w3qdxP4z60rCWNbgrrtCF\nB2uo8EX0UykXNakO0ImGtRyl25xbC/DD09+y71+EChHw8drK2HcAk5hRlhxWMbo/\nfoXDJlUkiPAlTp7rcbftdmH3eQ5R+YcFe7ddqI5fv/GLUhvXZUb3mpK4WESGp3pY\nw+ejm+ZwOuoeS2DlKm5K0DpDuajnCTI/gMlRVnrpRGBRHCo12na6dx9OtjaC3lYs\nI1xQv7CGwntamvorYyLKb20+dec+qnnp6J3B/ZDGMZ1DFXIImUnBJLQpw6yxGr0M\nxH99UnTm9X3WsMxro7+PsCCx4kGjDCXSEhEvRbj7aQKBgQDpBaooQ49HvfmysLe2\nDs6yyYhDnmwqD/Sx8Mhb++AymXfVzLBZBHz2dyvs+6p3oMZFns38MiD39njlTqd6\ntu0almpr8eTy1tWCAmPk8jOXNiUcO6iTku5b2fvUodHp4P1ZW+Vvi4tsNjYLECfZ\nZbNyzAhX+h7mtBpo+bLuxugNTwKBgQDZ63IzlwCxSzY4vdJRv/E01SOU2P9dPyaY\n1NEgtY2lt6ipAyiWJpMDab2SV3YlawPGsSDHMCpIuSKBbSmHPWlrmjZjPRUgBDOd\nM/cLLnFiIvaP3oLPveD84H4SfFUgPKsCP8QYhVFyFJZZCPWRISZl0v8pgw2V+mQy\n0/YEV6aJiQKBgApts3jL1Ty7ttIVcJNYRE3iERQdoe+b+TKBeSYMtrLtBVzvJTFG\nryUEnlWjybRC4Ly657MSt0EBqdVxWLN4PlJDSw37rGhlzvZbjwbvA/oPdUe3L8sy\n9zHrJocUmuVhqVT3dOQyFZJJNs/18CKdl5NaqEDvs7RVeR0bl7Nx+W6nAoGBAJDR\n4F4ajtJD+m+w7nF3jnOe5XuIzgQI8LyGSchj/xNPP126hKFsVyzge6QiTZjGSocj\ntXXKM3+K0TyT8BI5JLLmlBhVQpG5WReyrg2XOrCOLa8kn2gxdrB2/DGKwQOgbcEb\n4VSuXJbkyZm304I0NpFarEnJFyFBeo8wv4DZQwqJAoGAG7QGb72sin+EJhzpFYRf\nc7zgG2x55apj7k6RX93MkX7w542/iCqFDC+v8WmgKKxbNjSULTy9j4GJ55X8KstR\nVow6GssGhovluazTfqQndAQQ+ecZ7aYYp2i+dX6lfBbew3bfsswCTtO8wkxAemRp\nc874rWBv1HzFRmzx74DBeQ=\n-----END PRIVATE KEY-----\n",
  "client_email": "robot-agenda@corded-aquifer-402514.iam.gserviceaccount.com",
  "client_id": "100877979570026245847",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/robot-agenda%40corded-aquifer-402514.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# PARCHE AUTOMÁTICO DE SEGURIDAD
# Reemplaza los caracteres '\n' de texto por saltos de línea verdaderos que Google exige
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

# CONEXIÓN DIRECTA CON GOOGLE SHEETS
try:
    gc = gspread.service_account_from_dict(creds_dict)
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

    # BOTONES DE ACCIÓN (Escriben directo en las celdas)
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
