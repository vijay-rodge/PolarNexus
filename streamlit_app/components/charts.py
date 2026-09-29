import streamlit as st
import pandas as pd
from scientific_engine.visualizer import PolarDataVisualizer

def render_timeseries_chart(df: pd.DataFrame, parameter_col: str, time_col: str, title: str, unit: str = "°C"):
    fig = PolarDataVisualizer.create_timeseries_figure(
        df=df,
        parameter_col=parameter_col,
        time_col=time_col,
        title=title,
        unit=unit
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Interactive chart rendering is not available for this subset.")

def render_monthly_distribution_chart(df: pd.DataFrame, parameter_col: str, time_col: str, title: str, unit: str = "°C"):
    fig = PolarDataVisualizer.create_monthly_distribution(
        df=df,
        parameter_col=parameter_col,
        time_col=time_col,
        title=title,
        unit=unit
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)
