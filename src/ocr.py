# src/ocr.py
import io
from typing import List

import cv2
import numpy as np
from PIL import Image

import streamlit as st
from rapidocr_onnxruntime import RapidOCR


@st.cache_resource(show_spinner=False)
def _cached_reader():
    """Instantiate RapidOCR once per process."""
    return RapidOCR()


def _preprocess_for_ocr(image: Image.Image) -> np.ndarray:
    """Enhance low-resolution or noisy marketing assets for OCR."""
    rgb = image.convert("RGB")
    arr = np.array(rgb)
    if arr.size == 0:
        return arr

    # Upscale small assets to aid character detection.
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    height, width = bgr.shape[:2]
    longest_side = max(height, width)
    target = 1400
    if longest_side < target:
        scale = min(3.0, target / max(1, longest_side))
        bgr = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Improve contrast with CLAHE in Lab space.
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)
    lab_enhanced = cv2.merge((l_enhanced, a_channel, b_channel))
    enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)

    # Denoise and binarize to stabilize recognition.
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=7, templateWindowSize=7, searchWindowSize=21)
    adaptive = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        3,
    )

    return cv2.cvtColor(adaptive, cv2.COLOR_GRAY2RGB)


def _collect_text(results: List) -> str:
    if not results:
        return ""
    phrases = []
    for entry in results:
        if not entry or len(entry) < 2:
            continue
        text = entry[1]
        score = entry[2] if len(entry) > 2 else None
        if text and (score is None or score >= 0.3):
            phrases.append(text)
    return " ".join(phrases).strip()

def extract_text(image_bytes: bytes) -> str:
    """
    Extract text from an image using RapidOCR with preprocessing fallbacks.
    Ensures PIL.Image -> numpy.ndarray conversion for robustness.
    """
    if not image_bytes:
        return ""
    reader = _cached_reader()
    image = Image.open(io.BytesIO(image_bytes))
    rgb = np.array(image.convert("RGB"))

    results, _ = reader(rgb)
    text = _collect_text(results)
    if text:
        return text

    preprocessed = _preprocess_for_ocr(image)
    results, _ = reader(preprocessed)
    return _collect_text(results)
