"""
Punto de entrada principal – Generador de Informes SPVH Municipalidad de Rosario.
"""
import streamlit as st

st.set_page_config(page_title="Generador de Informes – SPVH", layout="wide")

# Inicializar session_state con valores por defecto
if "df" not in st.session_state:
    st.session_state.df = None
if "nombre_barrio" not in st.session_state:
    st.session_state.nombre_barrio = ""
if "fecha" not in st.session_state:
    st.session_state.fecha = ""
if "incluir_detalle" not in st.session_state:
    st.session_state.incluir_detalle = False

from src.ui import dashboard, export, home  # noqa: E402

tab_cargar, tab_dashboard, tab_exportar = st.tabs(["📤 Cargar", "📊 Dashboard", "📄 Exportar"])

with tab_cargar:
    home.render()

with tab_dashboard:
    dashboard.render()

with tab_exportar:
    export.render()
