"""
Pestaña de carga de datos – SPVH Municipalidad de Rosario.
"""
from __future__ import annotations

import datetime

import streamlit as st

from src.data.loader import cargar_excel

_MESES_ES = {
    "January": "enero",
    "February": "febrero",
    "March": "marzo",
    "April": "abril",
    "May": "mayo",
    "June": "junio",
    "July": "julio",
    "August": "agosto",
    "September": "septiembre",
    "October": "octubre",
    "November": "noviembre",
    "December": "diciembre",
}


def _fecha_hoy_es() -> str:
    """Devuelve la fecha de hoy en formato español, p.ej. '18 de mayo de 2026'."""
    hoy = datetime.date.today()
    mes_en = hoy.strftime("%B")
    mes_es = _MESES_ES.get(mes_en, mes_en.lower())
    return hoy.strftime(f"%d de {mes_es} de %Y")


def render() -> None:
    st.title("Generador de Informes de Lotes – SPVH Municipalidad de Rosario")

    st.markdown("Cargue el archivo Excel con los datos del padrón municipal para generar el informe.")

    # ── Controles de entrada ──────────────────────────────────────────────────
    uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx"])

    nombre_barrio = st.text_input(
        "Nombre del barrio",
        value=st.session_state.get("nombre_barrio", ""),
    )

    fecha = st.text_input(
        "Fecha del informe",
        value=st.session_state.get("fecha", _fecha_hoy_es()),
    )

    incluir_detalle = st.checkbox(
        "Incluir detalle completo por manzana en el informe Word",
        value=st.session_state.get("incluir_detalle", False),
    )

    # ── Botón de carga ────────────────────────────────────────────────────────
    if st.button("Cargar datos", type="primary"):
        if uploaded_file is None:
            st.error("Por favor, suba un archivo Excel antes de continuar.")
        elif not nombre_barrio.strip():
            st.error("Por favor, ingrese el nombre del barrio.")
        else:
            try:
                df = cargar_excel(uploaded_file)
            except ValueError as exc:
                st.error(f"Error al leer el archivo: {exc}")
            else:
                st.session_state.df = df
                st.session_state.nombre_barrio = nombre_barrio.strip()
                st.session_state.fecha = fecha
                st.session_state.incluir_detalle = incluir_detalle
                st.success(
                    f"✓ {len(df)} lotes cargados de {nombre_barrio.strip()}"
                )

    # ── Resumen del estado actual ─────────────────────────────────────────────
    if st.session_state.get("df") is not None:
        df_loaded = st.session_state.df
        st.info(
            f"**Datos cargados:** {len(df_loaded)} lotes · "
            f"Barrio: {st.session_state.get('nombre_barrio', '—')} · "
            f"Fecha: {st.session_state.get('fecha', '—')} · "
            f"Manzanas: {df_loaded['MANZANA'].nunique()}"
        )
