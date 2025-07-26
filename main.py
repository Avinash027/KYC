import pandas as pd
import os
import sys
import logging
import random

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_generator import generate_synthetic_kyc_data
from data_processor import process_kyc_data, add_id_verification_features
from fraud_model import train_fraud_model, predict_fraud, load_model
from id_document_processor import IDDocumentProcessor
from face_verifier import FaceVerifier

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

RAW_DATA_PATH = os.path.join(DATA_DIR, 'raw_kyc_data.csv')
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, 'processed_kyc_data.csv')
FINAL_PREDICTIONS_PATH = os.path.join(DATA_DIR, 'final_kyc_predictions.csv')
MODEL_PATH = os.path.join(MODELS_DIR, 'fraud_detection_model.pkl')

def run_pipeline(num_records=1000):
    """
    Runs the end-to-end KYC fraud detection pipeline.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

    logging.info("Starting KYC Fraud Detection Pipeline...")

    # Step 1: Generate Synthetic Data
    try:
        logging.info(f"Generating {num_records} synthetic KYC records...")
        raw_df = generate_synthetic_kyc_data(n_records=num_records)
        raw_df.to_csv(RAW_DATA_PATH, index=False)
        logging.info(f"Synthetic data saved to {RAW_DATA_PATH}")
    except Exception as e:
        logging.error(f"Error generating synthetic data: {e}")
        return

    # Step 2: Process Data (Clean and Apply Rule-Based Detection)
    try:
        logging.info("Processing KYC data (cleaning and rule-based detection)...")
        processed_df = process_kyc_data(raw_df)
        logging.info(f"Processed data saved to {PROCESSED_DATA_PATH}")
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        return

    # Step 3: Simulate ID Document and Facial Verification
    # In the main pipeline, we still simulate the *paths* to images
    # but the underlying IDDocumentProcessor and FaceVerifier will now
    # attempt to perform real (simplified) OCR and face detection/matching
    try:
        logging.info("Simulating ID document and facial verification...")
        id_processor = IDDocumentProcessor()
        face_verifier = FaceVerifier()

        # For simplicity, we'll simulate verification for the first record
        # In a real system, this would happen for each new application
        sample_record = processed_df.iloc[0]

        # Create dummy image files for testing the real OCR and face detection
        # In a real scenario, these would be actual user uploads
        dummy_image_dir = os.path.join(DATA_DIR, "dummy_images")
        os.makedirs(dummy_image_dir, exist_ok=True)

        dummy_id_path = "/home/ubuntu/upload/id.jpg"
        dummy_live_photo_path = "/home/ubuntu/upload/avinash.jpg"

        # Process document using real OCR
        doc_verification_result = id_processor.process_document(dummy_id_path)
        extracted_doc_face_annotation = face_verifier.detect_face(doc_verification_result["document_image_path"])

        # Process live photo using real face detection
        live_photo_face_annotation = face_verifier.detect_face(dummy_live_photo_path)

        # Face matching
        face_match_confidence = face_verifier.match_faces(extracted_doc_face_annotation, live_photo_face_annotation)

        # Aggregate verification results
        verification_results = {
            "authenticity_score": doc_verification_result["authenticity_score"],
            "extracted_data": doc_verification_result["extracted_data"],
            "face_match_confidence": face_match_confidence
        }

        # Add these new features to the processed_df
        # For simplicity, applying to all rows with the same simulated result
        # In a real system, each row would have its own verification result
        processed_df = add_id_verification_features(processed_df, verification_results)
        processed_df.to_csv(PROCESSED_DATA_PATH, index=False)
        logging.info("ID document and facial verification processed and features added.")

    except Exception as e:
        logging.error(f"Error during ID/Facial verification: {e}")
        return

    # Step 4: Train Fraud Detection Model
    try:
        logging.info("Training fraud detection model...")
        trained_model, scaler = train_fraud_model(processed_df, model_path=MODEL_PATH)
        logging.info(f"Model trained and saved to {MODEL_PATH}")
    except Exception as e:
        logging.error(f"Error training model: {e}")
        return

    # Step 5: Predict Fraud
    try:
        logging.info("Making fraud predictions...")
        final_df = predict_fraud(processed_df, trained_model, scaler)
        final_df.to_csv(FINAL_PREDICTIONS_PATH, index=False)
        logging.info(f"Final predictions saved to {FINAL_PREDICTIONS_PATH}")
    except Exception as e:
        logging.error(f"Error making predictions: {e}")
        return

    logging.info("Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline(num_records=500)



