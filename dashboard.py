import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from PIL import Image

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from id_document_processor import IDDocumentProcessor
from face_verifier import FaceVerifier

# Define paths (relative to the dashboard.py script)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FINAL_PREDICTIONS_PATH = os.path.join(DATA_DIR, 'final_kyc_predictions.csv')

st.set_page_config(layout="wide")
st.title("Simplified KYC Fraud Detection Dashboard")

@st.cache_data
def load_data(path):
    """
    Loads data from the specified CSV path.
    """
    if os.path.exists(path):
        return pd.read_csv(path)
    return None

# --- ID Verification and Facial Matching Section ---
st.header("Identity Document and Facial Matching")
st.write("Upload an identity document image and a live photo/selfie to perform OCR and facial matching.")

id_processor = IDDocumentProcessor()
face_verifier = FaceVerifier()

# File uploaders
document_image_file = st.file_uploader("Upload Identity Document Image (e.g., Passport, ID Card)", type=["jpg", "jpeg", "png"])
live_photo_file = st.file_uploader("Upload Live Photo / Selfie", type=["jpg", "jpeg", "png"])

verification_results = {}

if document_image_file and live_photo_file:
    st.subheader("Processing Identity Verification...")

    # Save uploaded files temporarily to process them
    doc_img_path = os.path.join(DATA_DIR, "uploaded_doc_image.jpg")
    live_photo_path = os.path.join(DATA_DIR, "uploaded_live_photo.jpg")

    with open(doc_img_path, "wb") as f:
        f.write(document_image_file.getbuffer())
    with open(live_photo_path, "wb") as f:
        f.write(live_photo_file.getbuffer())

    try:
        # Display uploaded images
        st.image(document_image_file, caption='Uploaded ID Document', width=300)
        st.image(live_photo_file, caption='Uploaded Live Photo', width=300)

        # 1. Process Document (OCR and Authenticity)
        doc_result = id_processor.process_document(doc_img_path)
        verification_results["authenticity_score"] = doc_result["authenticity_score"]
        verification_results["extracted_data"] = doc_result["extracted_data"]

        # Extract face from document image for matching
        doc_face_annotation = face_verifier.detect_face(doc_img_path)

        # 2. Process Live Photo
        live_photo_face_annotation = face_verifier.detect_face(live_photo_path)

        # 3. Face Matching
        face_match_confidence = 0.0
        if doc_face_annotation is not None and live_photo_face_annotation is not None:
            face_match_confidence = face_verifier.match_faces(doc_face_annotation, live_photo_face_annotation)
        else:
            st.warning("Could not detect faces in one or both images for matching.")

        verification_results["face_match_confidence"] = face_match_confidence

        st.success("Identity Verification Completed!")
        st.write(f"**Document Authenticity Score:** {verification_results['authenticity_score']:.2f}")
        st.write(f"**Face Match Confidence:** {verification_results['face_match_confidence']:.2f}")

        st.subheader("Extracted Document Data (OCR)")
        extracted_data = verification_results["extracted_data"]
        st.write(f"**Name:** {extracted_data.get('name', 'N/A')}")
        st.write(f"**Date of Birth:** {extracted_data.get('dob', 'N/A')}")
        st.write(f"**Document ID:** {extracted_data.get('document_id', 'N/A')}")
        st.write(f"**Address:** {extracted_data.get('address', 'N/A')}")
        st.write(f"**Expiry Date:** {extracted_data.get('expiry_date', 'N/A')}")
        st.write(f"**Document Type:** {extracted_data.get('document_type', 'N/A')}")
        st.write(f"**Gender:** {extracted_data.get('gender', 'N/A')}")

    except Exception as e:
        st.error(f"Error during identity verification: {e}")

    # Clean up temporary files
    if os.path.exists(doc_img_path): os.remove(doc_img_path)
    if os.path.exists(live_photo_path): os.remove(live_photo_path)

# --- Existing Dashboard Content ---
st.header("KYC Fraud Prediction Analytics")

df = load_data(FINAL_PREDICTIONS_PATH)

if df is not None:
    st.success(f"Data loaded successfully from {FINAL_PREDICTIONS_PATH}")
    
    st.write("## Data Preview")
    st.dataframe(df.head())

    st.write("## Fraud Prediction Distribution")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Rule-Based Flag Distribution")
        fig, ax = plt.subplots()
        sns.countplot(x='RuleFlag', data=df, ax=ax, palette='viridis')
        st.pyplot(fig)
    with col2:
        st.subheader("ML Prediction Distribution")
        fig, ax = plt.subplots()
        sns.countplot(x='ML_Prediction', data=df, ax=ax, palette='magma')
        st.pyplot(fig)

    st.write("## Fraud Probability Distribution (ML Model)")
    fig, ax = plt.subplots()
    sns.histplot(df['Fraud_Probability'], kde=True, ax=ax, bins=30)
    ax.set_title('Distribution of ML Fraud Probabilities')
    ax.set_xlabel('Fraud Probability')
    ax.set_ylabel('Number of Records')
    st.pyplot(fig)

    st.write("## Transaction Amount vs. Fraud Probability")
    fig, ax = plt.subplots()
    sns.scatterplot(x='TxnAmount', y='Fraud_Probability', hue='ML_Prediction', data=df, ax=ax, alpha=0.6)
    ax.set_title('Transaction Amount vs. Fraud Probability')
    ax.set_xlabel('Transaction Amount')
    ax.set_ylabel('Fraud Probability')
    st.pyplot(fig)

    st.write("## Transaction Count vs. Fraud Probability")
    fig, ax = plt.subplots()
    sns.scatterplot(x='TxnCount', y='Fraud_Probability', hue='ML_Prediction', data=df, ax=ax, alpha=0.6)
    ax.set_title('Transaction Count vs. Fraud Probability')
    ax.set_xlabel('Transaction Count')
    ax.set_ylabel('Fraud Probability')
    st.pyplot(fig)

    st.write("## Download Processed Data")
    st.download_button(
        label="Download final_kyc_predictions.csv",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='final_kyc_predictions.csv',
        mime='text/csv',
    )

else:
    st.warning("No data found. Please run the main pipeline (`python main.py`) to generate `final_kyc_predictions.csv`.")
    st.info("Expected data path: `kyc_simplified_v2/data/final_kyc_predictions.csv`")



