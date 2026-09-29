import streamlit as st
from typing import Dict, Any, List

def render_metric_card(title: str, value: str, delta: str = None, icon: str = "📊"):
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9)); 
                padding: 1.2rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1); 
                box-shadow: 0 4px 12px rgba(0,0,0,0.2); margin-bottom: 1rem;">
        <div style="font-size: 0.85rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">{icon} {title}</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8; margin: 0.4rem 0;">{value}</div>
        {f'<div style="font-size: 0.8rem; color: #34D399;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def render_station_card(station: Dict[str, Any]):
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); 
                border-radius: 14px; padding: 1.4rem; margin-bottom: 1.2rem; transition: transform 0.2s;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="color: #38BDF8; margin: 0; font-size: 1.4rem;">❄️ {station.get('name')} Station</h3>
            <span style="background: rgba(14, 165, 233, 0.2); color: #38BDF8; padding: 4px 12px; 
                         border-radius: 20px; font-size: 0.8rem; font-weight: 600;">{station.get('status')}</span>
        </div>
        <p style="color: #CBD5E1; margin: 0.6rem 0 0.8rem 0; font-size: 0.95rem;">{station.get('overview')}</p>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; font-size: 0.85rem; color: #94A3B8; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 0.8rem;">
            <div>📍 <strong>Region</strong>: {station.get('region')}</div>
            <div>🗓️ <strong>Founded</strong>: {station.get('commissioned_year')}</div>
            <div>🌐 <strong>Coords</strong>: {station.get('latitude')}°, {station.get('longitude')}°</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
