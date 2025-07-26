import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

def prepare_features(df):
    """
    Prepare features for machine learning model.

    Args:
        df (pd.DataFrame): The processed KYC data.

    Returns:
        tuple: (features, labels) for ML model.
    """
    # Create features from the data
    features = df[['TxnCount', 'TxnAmount']].copy()
    
    # Create additional features
    features['HighTxnAmount'] = (df['TxnAmount'] > 50000).astype(int)
    features['HighTxnCount'] = (df['TxnCount'] > 30).astype(int)
    features['PAN_Valid'] = df['PAN'].apply(lambda x: 1 if len(x) == 10 else 0)
    features['Email_Valid'] = df['Email'].str.contains('@').astype(int)
    
    # Create labels: 1 if flagged as suspicious by rules, 0 otherwise
    labels = (df["RuleFlag"] == "Suspicious").astype(int)

    # Ensure both classes are present for training, otherwise model.predict_proba will fail
    # This is a temporary fix for synthetic data; in real data, ensure sufficient fraud examples
    if labels.nunique() < 2:
        # If only one class, force a few 'Suspicious' labels for demonstration
        # In a real scenario, this indicates an issue with data generation or rule flagging
        if 0 not in labels.unique(): # Only 'Suspicious' present
            labels.iloc[0:max(1, len(labels) // 10)] = 0 # Force some 'Valid'
        elif 1 not in labels.unique(): # Only 'Valid' present
            labels.iloc[0:max(1, len(labels) // 10)] = 1 # Force some 'Suspicious'
    
    return features, labels

def train_fraud_model(df, model_path=None):
    """
    Train a machine learning model for fraud detection.

    Args:
        df (pd.DataFrame): The processed KYC data.
        model_path (str): Path to save the trained model.

    Returns:
        tuple: (trained_model, scaler) for making predictions.
    """
    # Prepare features and labels
    X, y = prepare_features(df)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.2f}")
    print("\\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model if path provided
    if model_path:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump((model, scaler), model_path)
        print(f"\\nModel saved to: {model_path}")
    
    return model, scaler

def predict_fraud(df, model, scaler):
    """
    Predict fraud using the trained model.

    Args:
        df (pd.DataFrame): The processed KYC data.
        model: The trained ML model.
        scaler: The fitted scaler.

    Returns:
        pd.DataFrame: The data with ML predictions.
    """
    # Prepare features
    X, _ = prepare_features(df)
    
    # Scale features
    X_scaled = scaler.transform(X)
    
    # Make predictions
    predictions = model.predict(X_scaled)
    probabilities = model.predict_proba(X_scaled)[:, 1]  # Probability of fraud
    
    # Add predictions to dataframe
    df_with_predictions = df.copy()
    df_with_predictions['ML_Prediction'] = np.where(predictions == 1, 'Fraud', 'Valid')
    df_with_predictions['Fraud_Probability'] = probabilities
    
    return df_with_predictions

def load_model(model_path):
    """
    Load a trained model from disk.

    Args:
        model_path (str): Path to the saved model.

    Returns:
        tuple: (model, scaler) loaded from disk.
    """
    return joblib.load(model_path)

if __name__ == "__main__":
    # Example usage when run directly
    from data_generator import generate_synthetic_kyc_data
    from data_processor import process_kyc_data
    
    # Generate and process sample data
    df = generate_synthetic_kyc_data(n_records=100)
    df_processed = process_kyc_data(df)
    
    print("Training fraud detection model...")
    model, scaler = train_fraud_model(df_processed)
    
    print("\\nMaking predictions...")
    df_with_predictions = predict_fraud(df_processed, model, scaler)
    
    print("\\nSample predictions:")
    print(df_with_predictions[['Name', 'RuleFlag', 'ML_Prediction', 'Fraud_Probability']].head())

