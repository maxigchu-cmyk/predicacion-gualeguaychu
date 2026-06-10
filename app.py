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

# DICCIONARIO DE CREDENCIALES DIRECTO EN CÓDIGO
creds_dict = {
    "type": "service_account",
    "project_id": "corded-aquifer-402514",
    "private_key_id": "493795e6aac15b1df87461888df225497c281379",
    "private_key": "-----BEGIN PRIVATE KEY-----\n"
                  "MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDhw+mCXHLG+H04\n"
                  "7Rw1+Ae5qgPKxdOE/k/vxaQv7ZV7Gx+ZBLm1mxk3VNJyQrjeu/QIjBfuGsK8MwG+\n"
                  "ukyOURheJaX6Fv8Vc6mgI0RbM8Tngmpoa91g8t0n2yoLJG3G3lKXvXUbUaJosoxX\n"
                  "ZaKSh3AXUYY7bgOZFRvcxTMgxN8bGQ8Ty7NY1Im6aJW9zK48xK6NX7s5vgfGfX1x\n"
                  "R8/prVjaLdqv2wJpA72tXs46/9iyPjMfCF0hP2woyO4QOzZax7SiKD/b9dstpGXi\n"
                  "lFZbAT9cXpgqzdLZA07H5+fCRRnOAumTYvgRmxZu6ORI+xo5+R88uWjgUMMcQhsO\n"
                  "gL7F7gCNAgMBAAECggEAClx7KkYzZ1HOr27kYU6zjhARMfxvx3YDdangreltt5No\n"
                  "WRW4Ly9B0kIEkYVh5ikCm2TQkVctkkUWAqqaqlpq76EzM53cEaA4C/cqYzQmSIi5\n"
                  "+PZgV9t1jmd2z8GZfyvDZx7lEb6moT72hWlO84IfQRa2/iG/rQYku/ZZ8RpP8faX\n"
                  "mPsYGkr6tGRBZoIsZFcUYQtLEYwHJG/f1td7bOwU1phQ3SX/EyKM4Wg+F8Zc8Xth\n"
                  "tEX0nszBrI+CbJmXlNo2qpocqV12sRsWXwceCrIXtjrYbQwDb4ydR/DaePcSDibu\n"
                  "mq1Fn4jSVMOJqbALALqqp/ewirh8pxGLCqnlztymuQKBgQD/TO+cyqMFR2nmaAUb\n"
                  "qSZ0oP0P+BfHPh3vYu08xo/ZNqQ5wTJO9VQ8Qx0jdVdlDMGVmDdk7RxlgJzeEe2W\n"
                  "0mRwbbU/H5T1mBNKkscWRKn9GzuAougJ0FrzX/zXOsv7tCnP4S0W/QZMgyGscSVG\n"
                  "2rNcaElwiSykLdrlu3szGVjh5QKBgQDiYkK04EdDmo4DK69H+TmEtNAdg3n6GrQB\n"
                  "qhAT5pPj+Pp4p8V4u9RxhhQA8q/RF8mrc2WWMe8xsoThMWQkOrfIURDzdcmaURcv\n"
                  "AXSvEeHaSD060c1xvqA+P/egTR/KDcNVAs1bCw2eZkSC6k8C0i658gGTvnHyU7w/\n"
                  "oHAA8DrZiQKBgQCHmF1LcXTUQPHGJklQP67lEvxVlvdKI3vSwUAvn2aXf6YJ5srJ\n"
                  "lROATkUTqCcazIOk6IvDVwxV/NFUQUFncadW723scOG072iPmxWShjWi8OvRjrSf\n"
                  "QcKMsNahmeDtduseNgK0yv6ldKBV7mJWF6Jb2ifnVXQYXyJ8Ee+FXFkQ4QKBgQDO\n"
                  "3tv2TbzRmjqLyy+xpZ1aF6DWV37vfddgbfejN+GNQcgg2a8qVPodg1hkRWFEwWgY\n"
                  "tKrwRVE/KNMkte287atj8jB7SfegfNmiqsHl+YFZ5wmM5ovGlVv5hprScafLDCij\n"
                  "Vpwxxjf7t5iTyXnKKido5C1sxWt69engesvfD6e3gQKBgQCNFBL5gQWKz5fCFe2/\n"
                  "fh+KGkTdaC183RzmSw9jlHJZyZM9sn9tgL11W9BErzXe441WHW0pu7vfksMi4S27\n"
                  "NlwIpETCoTP7fwv7HB4d0cAdaZ0fJuKclVm9Wxg/1ipwM6DI2qIuJOYuF1/Rd9wW\n"
                  "2Hs93Oil8aHJzXq3TLVhnig15A==\n"
                  "-----END PRIVATE KEY-----\n",
    "client_email": "robot-agenda@corded-aquifer-402514.iam.gserviceaccount.com",
    "client_id": "100877979570026245847",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/robot-agenda%40corded-aquifer-402514.iam.gserviceaccount.com"
}

# CONEXIÓN
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

# FILTRADO
df_pendientes = df[(df['Llamado'] != 'Sí') & (df['Estado'] != 'Inexistente')]

# MÉTRICAS
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

    # BOTONES DE ACCIÓN
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
