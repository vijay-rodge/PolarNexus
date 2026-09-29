import pandas as pd
from typing import Dict, Any, Optional

class PolarDataVisualizer:
    @classmethod
    def create_timeseries_figure(
        cls, 
        df: pd.DataFrame, 
        parameter_col: str, 
        time_col: str, 
        title: str, 
        unit: str = "°C"
    ) -> Optional[Any]:
        try:
            import plotly.graph_objects as go
            clean_df = df.dropna(subset=[time_col, parameter_col]).sort_values(by=time_col)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=clean_df[time_col],
                y=clean_df[parameter_col],
                mode='lines',
                name=f'Raw {parameter_col} ({unit})',
                line=dict(color='#00ADB5', width=1.5),
                opacity=0.7
            ))
            if len(clean_df) > 50:
                clean_df['rolling_avg'] = clean_df[parameter_col].rolling(window=14, min_periods=1).mean()
                fig.add_trace(go.Scatter(
                    x=clean_df[time_col],
                    y=clean_df['rolling_avg'],
                    mode='lines',
                    name='Trend (14-Point Rolling Mean)',
                    line=dict(color='#FF5722', width=2.5)
                ))
            fig.update_layout(
                title=dict(text=title, font=dict(size=18, color='#EEEEEE')),
                paper_bgcolor='rgba(15, 23, 42, 0.8)',
                plot_bgcolor='rgba(30, 41, 59, 0.7)',
                xaxis=dict(
                    title='Observation Timestamp (UTC)',
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.1)',
                    rangeslider=dict(visible=True)
                ),
                yaxis=dict(
                    title=f'{parameter_col} [{unit}]',
                    showgrid=True,
                    gridcolor='rgba(255, 255, 255, 0.1)'
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                font=dict(color='#E2E8F0'),
                margin=dict(l=40, r=40, t=60, b=40)
            )
            return fig
        except Exception:
            return None

    @classmethod
    def create_monthly_distribution(
        cls,
        df: pd.DataFrame,
        parameter_col: str,
        time_col: str,
        title: str,
        unit: str = "°C"
    ) -> Optional[Any]:
        try:
            import plotly.express as px
            clean_df = df.dropna(subset=[time_col, parameter_col]).copy()
            clean_df['Month'] = pd.to_datetime(clean_df[time_col]).dt.strftime('%b')
            month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            fig = px.box(
                clean_df, 
                x='Month', 
                y=parameter_col, 
                category_orders={'Month': month_order},
                title=title,
                color_discrete_sequence=['#38BDF8']
            )
            fig.update_layout(
                paper_bgcolor='rgba(15, 23, 42, 0.8)',
                plot_bgcolor='rgba(30, 41, 59, 0.7)',
                yaxis_title=f"{parameter_col} [{unit}]",
                font=dict(color='#E2E8F0')
            )
            return fig
        except Exception:
            return None
