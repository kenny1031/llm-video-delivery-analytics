from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

REPORTS_DIR = Path("reports")
LLM_OUTPUTS_DIR = REPORTS_DIR / "llm_outputs"
DIAGNOSTICS_DIR = REPORTS_DIR / "diagnostics"

BAR_COLORS = ["#6366F1", "#A78BFA", "#F59E0B", "#10B981", "#EF4444"]
VARIANT_COLORS = {
    "control": "#64748B",
    "treatment": "#8B5CF6",
}

st.set_page_config(
    page_title="Video Delivery Analytics",
    page_icon="📊",
    layout="wide",
)


def polish_bar_chart(fig, height: int = 380):
    fig.update_traces(
        width=0.35,
        textposition="outside",
        cliponaxis=False,
        marker_line_width=0,
    )
    fig.update_layout(
        height=height,
        bargap=0.45,
        bargroupgap=0.15,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=30, t=55, b=45),
        font=dict(size=12),
        title=dict(font=dict(size=16)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        title=None,
    )
    fig.update_yaxes(
        gridcolor="#E5E7EB",
        zeroline=False,
    )
    return fig


@st.cache_resource
def get_engine():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing. Please set it in .env.")
    return create_engine(DATABASE_URL)


@st.cache_data(ttl=300)
def read_sql(query: str) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(query, engine)


def metric_card(label: str, value: str, delta: str | None = None):
    st.metric(label=label, value=value, delta=delta)


def fmt_ms(x: float) -> str:
    return f"{x:.2f} ms"


def fmt_pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def fmt_usd(x: float) -> str:
    return f"${x:.4f}"


def load_text(path: Path) -> str:
    if not path.exists():
        return f"File not found: `{path}`"
    return path.read_text(encoding="utf-8")


def page_overview():
    st.title("Video Delivery Quality & Cost Analytics")
    st.caption(
        "A local analytics dashboard for delivery quality, cost governance, "
        "capacity monitoring, experiment analysis, and LLM-assisted readouts."
    )

    quality = read_sql(
        """
        SELECT
            variant,
            COUNT(*) AS event_count,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(startup_time_ms) AS avg_startup_time_ms,
            AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
            AVG(cache_hit) AS cache_hit_rate,
            SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events
        FROM delivery_events
        GROUP BY variant
        ORDER BY variant
        """
    )

    capacity = read_sql(
        """
        SELECT
            COUNT(*) AS snapshot_count,
            AVG(utilization_ratio) AS avg_utilization,
            MAX(utilization_ratio) AS peak_utilization,
            SUM(CASE WHEN utilization_ratio >= 0.85 THEN 1 ELSE 0 END) AS high_utilization_hours
        FROM edge_capacity_snapshots
        """
    )

    control = quality[quality["variant"] == "control"].iloc[0]
    treatment = quality[quality["variant"] == "treatment"].iloc[0]

    latency_lift = (
        treatment["avg_latency_ms"] - control["avg_latency_ms"]
    ) / control["avg_latency_ms"]

    cost_lift = (
        treatment["cost_per_1k_events"] - control["cost_per_1k_events"]
    ) / control["cost_per_1k_events"]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Treatment Latency",
            fmt_ms(treatment["avg_latency_ms"]),
            f"{latency_lift * 100:.2f}% vs control",
        )

    with c2:
        metric_card(
            "Treatment Startup Time",
            fmt_ms(treatment["avg_startup_time_ms"]),
        )

    with c3:
        metric_card(
            "Cost per 1K Events",
            fmt_usd(treatment["cost_per_1k_events"]),
            f"{cost_lift * 100:.2f}% vs control",
        )

    with c4:
        metric_card(
            "Peak Edge Utilization",
            fmt_pct(capacity.iloc[0]["peak_utilization"]),
        )

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Experiment Quality Metrics")
        st.dataframe(quality, use_container_width=True)

        fig = px.bar(
            quality,
            x="variant",
            y=["avg_latency_ms", "avg_startup_time_ms"],
            barmode="group",
            title="Latency and Startup Time by Variant",
            color_discrete_sequence=["#8B5CF6", "#F59E0B"],
        )
        fig = polish_bar_chart(fig, height=340)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Capacity Summary")
        st.dataframe(capacity, use_container_width=True)

        st.info(
            "Capacity report is available in the Capacity Risk page. "
            "The peak utilization metric above highlights the highest observed edge capacity pressure."
        )


def page_quality_experiment():
    st.title("Quality Experiment")

    quality = read_sql(
        """
        SELECT
            variant,
            COUNT(*) AS event_count,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(startup_time_ms) AS avg_startup_time_ms,
            AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
            AVG(cache_hit) AS cache_hit_rate
        FROM delivery_events
        GROUP BY variant
        ORDER BY variant
        """
    )

    st.subheader("Variant-level Quality Metrics")
    st.dataframe(quality, use_container_width=True)

    fig1 = px.bar(
        quality,
        x="variant",
        y="avg_latency_ms",
        title="Average Latency by Variant",
        text_auto=".2f",
        color="variant",
        color_discrete_map=VARIANT_COLORS,
    )
    fig1 = polish_bar_chart(fig1, height=340)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        quality,
        x="variant",
        y="avg_rebuffer_ratio",
        title="Average Rebuffer Ratio by Variant",
        text_auto=".4f",
        color="variant",
        color_discrete_map=VARIANT_COLORS,
    )
    fig1 = polish_bar_chart(fig2, height=340)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Segment Diagnostics")

    segment = st.selectbox(
        "Choose segment",
        ["region_code", "edge_pop", "protocol", "ip_version"],
    )

    segment_df = read_sql(
        f"""
        SELECT
            {segment},
            variant,
            COUNT(*) AS event_count,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(startup_time_ms) AS avg_startup_time_ms,
            AVG(rebuffer_ratio) AS avg_rebuffer_ratio,
            AVG(cache_hit) AS cache_hit_rate,
            SUM(cdn_cost_usd) AS total_cdn_cost_usd
        FROM delivery_events
        GROUP BY {segment}, variant
        ORDER BY avg_latency_ms DESC
        """
    )

    st.dataframe(segment_df, use_container_width=True)

    fig3 = px.bar(
        segment_df,
        x=segment,
        y="avg_latency_ms",
        color="variant",
        barmode="group",
        title=f"Average Latency by {segment}",
        color_discrete_map=VARIANT_COLORS,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("A/B Test Readout")
    st.markdown(load_text(REPORTS_DIR / "experiment_readout.md"))


def page_cost_governance():
    st.title("Cost Governance")

    overall = read_sql(
        """
        SELECT
            variant,
            COUNT(*) AS event_count,
            SUM(cdn_cost_usd) AS total_cdn_cost_usd,
            AVG(cdn_cost_usd) AS avg_cost_per_event,
            SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
            AVG(cache_hit) AS cache_hit_rate,
            AVG(latency_ms) AS avg_latency_ms,
            AVG(rebuffer_ratio) AS avg_rebuffer_ratio
        FROM delivery_events
        GROUP BY variant
        ORDER BY variant
        """
    )

    st.subheader("Overall Cost Metrics")
    st.dataframe(overall, use_container_width=True)

    fig1 = px.bar(
        overall,
        x="variant",
        y="cost_per_1k_events",
        title="Cost per 1K Events by Variant",
        text_auto=".4f",
        color="variant",
        color_discrete_map=VARIANT_COLORS,
    )
    fig1 = polish_bar_chart(fig1, height=340)
    st.plotly_chart(fig1, use_container_width=True)

    segment = st.selectbox(
        "Cost breakdown dimension",
        ["region_code", "edge_pop", "protocol", "ip_version"],
    )

    breakdown = read_sql(
        f"""
        SELECT
            {segment},
            variant,
            COUNT(*) AS event_count,
            SUM(cdn_cost_usd) AS total_cdn_cost_usd,
            SUM(cdn_cost_usd) / NULLIF(COUNT(*), 0) * 1000 AS cost_per_1k_events,
            AVG(cache_hit) AS cache_hit_rate,
            AVG(latency_ms) AS avg_latency_ms
        FROM delivery_events
        GROUP BY {segment}, variant
        ORDER BY total_cdn_cost_usd DESC
        """
    )

    st.subheader(f"Cost Breakdown by {segment}")
    st.dataframe(breakdown, use_container_width=True)

    fig2 = px.bar(
        breakdown,
        x=segment,
        y="cost_per_1k_events",
        color="variant",
        barmode="group",
        title=f"Cost per 1K Events by {segment}",
        color_discrete_map=VARIANT_COLORS,
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Cost-quality Report")
    st.markdown(load_text(REPORTS_DIR / "cost_quality_report.md"))


def page_capacity_risk():
    st.title("Capacity Risk")

    risk = read_sql(
        """
        SELECT
            edge_pop,
            region_code,
            AVG(utilization_ratio) AS avg_utilization,
            MAX(utilization_ratio) AS peak_utilization,
            SUM(CASE WHEN utilization_ratio >= 0.85 THEN 1 ELSE 0 END) AS high_utilization_hours,
            SUM(CASE WHEN utilization_ratio >= 0.90 THEN 1 ELSE 0 END) AS critical_utilization_hours,
            COUNT(*) AS total_hours,
            SUM(CASE WHEN utilization_ratio >= 0.85 THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS high_utilization_share,
            AVG(cpu_utilization) AS avg_cpu_utilization,
            AVG(memory_utilization) AS avg_memory_utilization
        FROM edge_capacity_snapshots
        GROUP BY edge_pop, region_code
        ORDER BY high_utilization_share DESC, peak_utilization DESC
        """
    )

    st.subheader("Capacity Risk Table")
    st.dataframe(risk, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        fig1 = px.bar(
            risk,
            x="edge_pop",
            y="peak_utilization",
            color="region_code",
            title="Peak Utilization by Edge PoP",
            text_auto=".2%",
            color_discrete_sequence=BAR_COLORS,
        )
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        fig2 = px.bar(
            risk,
            x="edge_pop",
            y="high_utilization_share",
            color="region_code",
            title="High-utilization Share by Edge PoP",
            text_auto=".2%",
            color_discrete_sequence=BAR_COLORS,
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Capacity Snapshots")

    selected_edge = st.selectbox("Choose edge PoP", sorted(risk["edge_pop"].unique()))

    snapshots = read_sql(
        f"""
        SELECT
            snapshot_time,
            edge_pop,
            region_code,
            utilization_ratio,
            cpu_utilization,
            memory_utilization,
            active_connections
        FROM edge_capacity_snapshots
        WHERE edge_pop = '{selected_edge}'
        ORDER BY snapshot_time
        """
    )

    fig3 = px.line(
        snapshots,
        x="snapshot_time",
        y=["utilization_ratio", "cpu_utilization", "memory_utilization"],
        title=f"Resource Utilization Over Time: {selected_edge}",
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Capacity Report")
    st.markdown(load_text(REPORTS_DIR / "capacity_report.md"))


def page_llm_readouts():
    st.title("LLM-assisted Readouts")
    st.caption(
        "The LLM rewrites structured SQL/Python diagnostics into business-facing summaries. "
        "It is not used as the source of truth."
    )

    tab1, tab2, tab3 = st.tabs(
        ["Experiment Readout", "Root-cause Hypotheses", "Metric Dictionary"]
    )

    with tab1:
        st.subheader("Experiment Readout")
        st.markdown(load_text(LLM_OUTPUTS_DIR / "protocol_test_readout.md"))

    with tab2:
        st.subheader("Grounded Root-cause Hypotheses")
        st.markdown(load_text(LLM_OUTPUTS_DIR / "root_cause_hypotheses.md"))

        st.divider()
        st.subheader("Rule-based Source-of-truth Summary")
        st.markdown(load_text(DIAGNOSTICS_DIR / "rule_based_root_cause.md"))

    with tab3:
        st.subheader("Metric Dictionary")
        st.markdown(load_text(REPORTS_DIR / "metric_dictionary.md"))


def main():
    st.sidebar.title("Navigation")

    page = st.sidebar.radio(
        "Go to",
        [
            "Overview",
            "Quality Experiment",
            "Cost Governance",
            "Capacity Risk",
            "LLM Readouts",
        ],
    )

    st.sidebar.divider()
    st.sidebar.caption(
        "PostgreSQL metrics · Python analytics · local LLM summaries"
    )

    st.sidebar.markdown(
        """
        **Source of truth**
        - SQL metrics
        - Statistical tests
        - Rule-based diagnostics

        **LLM usage**
        - Readout rewriting
        - Hypothesis summarisation
        """
    )

    if page == "Overview":
        page_overview()
    elif page == "Quality Experiment":
        page_quality_experiment()
    elif page == "Cost Governance":
        page_cost_governance()
    elif page == "Capacity Risk":
        page_capacity_risk()
    elif page == "LLM Readouts":
        page_llm_readouts()


if __name__ == "__main__":
    main()