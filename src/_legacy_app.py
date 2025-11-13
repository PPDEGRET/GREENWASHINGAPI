"""Streamlit application entrypoint for GreenCheck."""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add the src directory to the Python path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

import streamlit as st
from dotenv import load_dotenv

from analyzer import analyze_image
from config import AppConfig
from db import (
    SupabaseClient,
    get_anon_client,
    get_service_client,
    get_user_client,
)
from report import build_report

# --- App Config ---
load_dotenv()
config = AppConfig()


def _get_db_client() -> SupabaseClient:
    """Initialize Supabase client, respecting user auth."""
    if st.session_state.get("supabase_access_token"):
        return get_user_client(st.session_state["supabase_access_token"])
    return get_anon_client()


def _inject_global_styles() -> None:
    """Inject global CSS styles for a cleaner UI."""
    st.markdown(
        """
        <style>
            /* Your custom styles here */
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Render the sidebar with user auth and navigation."""
    st.sidebar.title("Navigation")
    # Add navigation links here


def render_main_content() -> None:
    """Render the main application content."""
    st.title("GreenCheck Greenwashing Detector")
    uploaded_file = st.file_uploader(
        "Upload an ad creative (JPG, PNG)", type=["jpg", "png"]
    )

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Creative", use_column_width=True)
        if st.button("Analyze Creative"):
            with st.spinner("Analyzing..."):
                image_bytes = uploaded_file.getvalue()
                results = analyze_image(image_bytes)
                st.session_state["analysis_results"] = results
                st.session_state["image_bytes"] = image_bytes
                st.experimental_rerun()


def render_analysis_results() -> None:
    """Render the analysis results, if available."""
    if "analysis_results" in st.session_state:
        st.header("Analysis Results")
        results = st.session_state["analysis_results"]
        st.json(results)

        pdf_bytes, filename = build_report(
            st.session_state["image_bytes"],
            results.get("text", ""),
            results,
        )
        st.download_button(
            "Download Report",
            pdf_bytes,
            file_name=filename,
            mime="application/pdf",
        )


def main() -> None:
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="GreenCheck Greenwashing Detector",
        page_icon="🌿",
        layout="wide",
    )
    _inject_global_styles()
    render_sidebar()
    if "analysis_results" in st.session_state:
        render_analysis_results()
    else:
        render_main_content()


if __name__ == "__main__":
    main()
