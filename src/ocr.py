# src/ocr.py
import io
import importlib.util
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image

import streamlit as st

_rapidocr_spec = importlib.util.find_spec("rapidocr_onnxruntime")
if _rapidocr_spec:
    from rapidocr_onnxruntime import RapidOCR  # type: ignore[assignment]
else:  # pragma: no cover - exercised when the optional dependency is missing.
    RapidOCR = None  # type: ignore[assignment]


@st.cache_resource(show_spinner=False)
def _cached_reader() -> Optional["RapidOCR"]:
    """Instantiate RapidOCR once per process."""
    if RapidOCR is None:
        return None
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

# --- add this helper near the top of the file (or above _collect_text) ---
def _to_float_or_none(x):
    if x is None:
        return None
    try:
        # Some OCR libs return strings like "0.87" or even "87%"
        s = str(x).strip().replace("%", "")
        return float(s) if s != "" else None
    except (ValueError, TypeError):
        return None

# --- replace your existing _collect_text with this version ---
def _collect_text(results, min_conf=0.30):
    """
    Normalizes OCR results from different backends (EasyOCR, RapidOCR, etc.)
    and concatenates text lines above a confidence threshold.
    Accepts result rows shaped like:
      - (bbox, text, score)
      - {'text': '...', 'score': 0.9, ...}
      - ('text', 'score') in rare cases
    """
    lines = []
    for row in results or []:
        text, score = None, None

        # Tuple/list shapes
        if isinstance(row, (list, tuple)):
            # (bbox, text, score)
            if len(row) >= 3 and isinstance(row[1], str):
                text = row[1]
                score = row[2]
            # (text, score)
            elif len(row) >= 2 and isinstance(row[0], str):
                text = row[0]
                score = row[1]
            # Just (text,)
            elif len(row) >= 1 and isinstance(row[0], str):
                text = row[0]

        # Dict shape
        elif isinstance(row, dict):
            text = row.get("text") or row.get("label") or row.get("content")
            score = row.get("score") or row.get("confidence")

        # Coerce score -> float|None
        score_f = _to_float_or_none(score)

        # Keep if we have text and either no score or score >= threshold
        if text:
            if score_f is None or score_f >= float(min_conf):
                lines.append(text)

    return "\n".join(lines).strip()

def extract_text(image_bytes: bytes) -> str:
    """
    Extract text from an image using RapidOCR with preprocessing fallbacks.
    Ensures PIL.Image -> numpy.ndarray conversion for robustness.
    """
    if not image_bytes:
        return ""
    reader = _cached_reader()
    if reader is None:
        st.error(
            "OCR is unavailable because the optional dependency "
            "`rapidocr-onnxruntime` is not installed. Please run "
            "`pip install rapidocr-onnxruntime` to enable image text extraction."
        )
        return ""
    image = Image.open(io.BytesIO(image_bytes))
    rgb = np.array(image.convert("RGB"))

    results, _ = reader(rgb)
    text = _collect_text(results)
    if text:
        return text

    preprocessed = _preprocess_for_ocr(image)
    results, _ = reader(preprocessed)
    return _collect_text(results)
