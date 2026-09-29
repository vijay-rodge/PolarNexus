import streamlit as st

def render_sidebar():
    """
    Renders the unified PolarNexus sidebar branding header, navigation context,
    and metadata badge across all pages in the Polar Science Platform.
    """
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 0.8rem 0.4rem 1.2rem 0.4rem; border-bottom: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 1.2rem;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 16px; background: linear-gradient(135deg, #0284C7, #38BDF8); box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4); margin-bottom: 0.6rem;">
                <span style="font-size: 2rem;">❄️</span>
            </div>
            <h1 style="font-size: 1.65rem; font-weight: 800; background: linear-gradient(135deg, #38BDF8, #818CF8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; letter-spacing: -0.03em;">PolarNexus</h1>
            <p style="font-size: 0.8rem; color: #94A3B8; margin: 0.2rem 0 0.8rem 0; font-weight: 500;">Polar Science Outreach & Knowledge Portal</p>
            <div style="display: flex; gap: 0.4rem; justify-content: center; flex-wrap: wrap;">
                <span style="background: rgba(2, 132, 199, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 0.68rem; padding: 0.2rem 0.5rem; border-radius: 9999px; font-weight: 600;">SIH PS 26063</span>
                <span style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(52, 211, 153, 0.3); font-size: 0.68rem; padding: 0.2rem 0.5rem; border-radius: 9999px; font-weight: 600;">NCPOR / MoES</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
