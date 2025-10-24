# src/ocr.py
import io
from typing import List
import numpy as np
from PIL import Image
import easyocr
import streamlit as st

@st.cache_resource(show_spinner=False)
def _cached_reader():
    """
    Load EasyOCR once per process.
    Add/remove languages as needed. 'en','fr' covers most of your tests.
    """
    return easyocr.Reader(['en', 'fr'], gpu=False)

def extract_text(image_bytes: bytes) -> str:
    """
    Extracts text from an image (bytes) using EasyOCR.
    Ensures PIL.Image -> numpy.ndarray conversion for robustness.
    """
    if not image_bytes:
        return ""
    reader = _cached_reader()
    image = Image.open(io.BytesIO(image_bytes))
    # Convert to ndarray for EasyOCR
    arr = np.array(image)
    # readtext returns list of (bbox, text, confidence)
    results: List = reader.readtext(arr)
    text = " ".join([entry[1] for entry in results if len(entry) > 1 and entry[1]])
    return text.strip()
