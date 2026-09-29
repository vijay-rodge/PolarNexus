import streamlit as st
from typing import List, Dict, Any

def render_citations_drawer(citations: List[Dict[str, Any]]):
    if not citations:
        return
    with st.expander(f"📚 Verified Scientific Citations & Sources ({len(citations)})", expanded=False):
        for c in citations:
            cid = c.get("citation_id", "")
            src_name = c.get("source_name", "Official NCPOR Source")
            url = c.get("url") or c.get("source_url") or "#"
            doc_id = c.get("document_id") or c.get("dataset_id") or ""
            sec = c.get("section")
            pg = c.get("page")
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); padding: 0.8rem 1rem; border-radius: 8px; 
                        border-left: 3px solid #38BDF8; margin-bottom: 0.6rem; font-size: 0.9rem;">
                <div style="font-weight: 600; color: #F1F5F9;">[{cid}] {src_name}</div>
                <div style="color: #94A3B8; font-size: 0.8rem; margin: 0.2rem 0;">
                    {f'<strong>Identifier</strong>: <code>{doc_id}</code> | ' if doc_id else ''}
                    {f'<strong>Section</strong>: {sec} | ' if sec else ''}
                    {f'<strong>Page</strong>: {pg} | ' if pg else ''}
                    <a href="{url}" target="_blank" style="color: #38BDF8; text-decoration: none;">View Official Record ↗</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
