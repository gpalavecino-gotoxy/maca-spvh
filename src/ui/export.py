"""
Pestaña de exportación de informes – SPVH Municipalidad de Rosario.
"""
from __future__ import annotations

import streamlit as st

from src.report.pdf_exporter import generar_pdf
from src.report.word_exporter import generar_word


def render() -> None:
    df = st.session_state.get("df")

    if df is None:
        st.info("Primero cargue un archivo en la pestaña Cargar.")
        return

    nombre_barrio = st.session_state.get("nombre_barrio", "")
    fecha = st.session_state.get("fecha", "")
    incluir_detalle = st.session_state.get("incluir_detalle", False)

    st.header("Exportar Informe")

    # ── Resumen de lo que se exportará ────────────────────────────────────────
    st.subheader("Resumen")
    st.markdown(
        f"- **Barrio:** {nombre_barrio}\n"
        f"- **Fecha:** {fecha}\n"
        f"- **Total lotes:** {len(df)}\n"
        f"- **Manzanas:** {df['MANZANA'].nunique()}\n"
        f"- **Detalle por manzana:** {'Sí' if incluir_detalle else 'No'}"
    )

    st.divider()

    # ── Exportar Word ─────────────────────────────────────────────────────────
    st.subheader("Documento Word (.docx)")

    if st.button("Generar y descargar Word", key="btn_word"):
        with st.spinner("Generando informe..."):
            docx_bytes = generar_word(df, nombre_barrio, fecha, incluir_detalle)
            st.session_state._docx_bytes = docx_bytes

    if st.session_state.get("_docx_bytes") is not None:
        st.download_button(
            label="⬇ Descargar Word",
            data=st.session_state._docx_bytes,
            file_name=f"informe_{nombre_barrio}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="dl_word",
        )

    # ── Exportar PDF ──────────────────────────────────────────────────────────
    st.subheader("Documento PDF")

    if st.button("Generar y descargar PDF", key="btn_pdf"):
        with st.spinner("Generando informe..."):
            try:
                docx_bytes = generar_word(df, nombre_barrio, fecha, incluir_detalle)
                pdf_bytes = generar_pdf(docx_bytes)
                st.session_state._pdf_bytes = pdf_bytes
            except RuntimeError as exc:
                st.error(f"No se pudo generar el PDF: {exc}")
                st.session_state._pdf_bytes = None

    if st.session_state.get("_pdf_bytes") is not None:
        st.download_button(
            label="⬇ Descargar PDF",
            data=st.session_state._pdf_bytes,
            file_name=f"informe_{nombre_barrio}.pdf",
            mime="application/pdf",
            key="dl_pdf",
        )
