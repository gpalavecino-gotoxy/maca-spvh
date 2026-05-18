"""
Pestaña del dashboard interactivo – SPVH Municipalidad de Rosario.
"""
from __future__ import annotations

import streamlit as st

from src.data.analyzer import (
    agrupar_estados_para_informe,
    detectar_patrones_observaciones,
    estado_por_manzana,
    totales_por_estado,
)
from src.report.charts import (
    grafico_barras_por_manzana_plotly,
    grafico_torta_estados_plotly,
)


def render() -> None:
    df = st.session_state.get("df")

    if df is None:
        st.info("Primero cargue un archivo en la pestaña Cargar.")
        return

    st.header(f"Dashboard – {st.session_state.get('nombre_barrio', '')}")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_lotes = len(df)
    estados_raw = totales_por_estado(df)
    escriturados_info = estados_raw.get("ESCRITURADO", {})
    pct_escriturados = escriturados_info.get("porcentaje", 0.0)

    deuda_count = int(df["ESTADO"].isin(["DEUDA"]).sum())
    manzanas_count = df["MANZANA"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Lotes", total_lotes)
    col2.metric("% Escriturados", f"{pct_escriturados:.1f}%")
    col3.metric("Lotes con Deuda", deuda_count)
    col4.metric("Manzanas", manzanas_count)

    # ── Gráficos ──────────────────────────────────────────────────────────────
    estado_general = agrupar_estados_para_informe(df)
    pivot = estado_por_manzana(df)

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(
            grafico_torta_estados_plotly(estado_general),
            use_container_width=True,
        )
    with chart_col2:
        st.plotly_chart(
            grafico_barras_por_manzana_plotly(pivot),
            use_container_width=True,
        )

    # ── Filtros y tabla ───────────────────────────────────────────────────────
    st.subheader("Explorar datos")

    manzanas = sorted(df["MANZANA"].unique().tolist())
    all_estados = sorted(df["ESTADO"].dropna().unique().tolist())

    filtro_manzana = st.selectbox(
        "Filtrar por Manzana",
        options=["Todas"] + manzanas,
    )
    filtro_estados = st.multiselect(
        "Filtrar por Estado",
        options=all_estados,
        default=all_estados,
    )
    busqueda = st.text_input("Buscar titular o dirección", "")

    # Aplicar filtros
    filtered_df = df.copy()

    if filtro_manzana != "Todas":
        filtered_df = filtered_df[filtered_df["MANZANA"] == filtro_manzana]

    filtered_df = filtered_df[filtered_df["ESTADO"].isin(filtro_estados)]

    if busqueda.strip():
        term = busqueda.strip().lower()
        mask = (
            filtered_df["TITULAR"].fillna("").str.lower().str.contains(term, regex=False)
            | filtered_df["DIRECCION"].fillna("").str.lower().str.contains(term, regex=False)
        )
        filtered_df = filtered_df[mask]

    st.dataframe(
        filtered_df[["MANZANA", "LOTE", "TITULAR", "COTITULAR", "DIRECCION", "ESTADO", "OBSERVACIONES"]],
        use_container_width=True,
        hide_index=True,
    )

    st.caption(f"{len(filtered_df)} lote(s) mostrado(s)")

    # ── Análisis de observaciones ─────────────────────────────────────────────
    st.subheader("Análisis de Observaciones")

    patrones = detectar_patrones_observaciones(df)

    if not patrones:
        st.write("No se detectaron patrones en las observaciones.")
    else:
        items = list(patrones.items())
        num_cols = 3
        for i in range(0, len(items), num_cols):
            cols = st.columns(num_cols)
            for j, (key, count) in enumerate(items[i : i + num_cols]):
                cols[j].metric(label=key, value=count)
