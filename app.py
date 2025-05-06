import streamlit as st
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io
import re

st.title("Vet Invoice Analyzer")

uploaded_file = st.file_uploader("Upload a vet invoice (PDF or image)", type=["pdf", "png", "jpg", "jpeg"])

def extract_text(file_bytes, filename):
    if filename.lower().endswith('.pdf'):
        images = convert_from_bytes(file_bytes)
        text = "\n".join([pytesseract.image_to_string(img) for img in images])
    else:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
    return text

def analyze_invoice(text):
    lines = text.split('\n')
    services = []
    total = None
    for line in lines:
        if '$' in line:
            match = re.search(r'(.+?)\s+\$([\d\.,]+)', line)
            if match:
                service = match.group(1).strip()
                amount = match.group(2).replace(',', '')
                services.append({'service': service, 'amount': float(amount)})
        if 'total' in line.lower():
            match = re.search(r'\$([\d\.,]+)', line)
            if match:
                total = float(match.group(1).replace(',', ''))
    return {
        'services': services,
        'total': total
    }

if uploaded_file:
    with st.spinner("Analyzing..."):
        text = extract_text(uploaded_file.read(), uploaded_file.name)
        analysis = analyze_invoice(text)
        st.subheader("Extracted Services and Charges")
        st.json(analysis)
