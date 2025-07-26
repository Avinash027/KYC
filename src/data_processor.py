import pandas as pd
import re

# Validation patterns
PAN_REGEX = r"[A-Z]{5}[0-9]{4}[A-Z]"
AADHAAR_REGEX = r"\d{4} \d{4} \d{4}"
EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
MOBILE_REGEX = r"[6-9]\d{9}"

# Blacklisted entities (same as in data_generator)
BLACKLISTED_PAN = {"ABCDE1234F", "PQRST6789L"}
BLACKLISTED_AADHAAR = {"1234 5678 9012", "1111 2222 3333"}

def validate_pan(pan):
    """Validate PAN format."""
    return bool(re.fullmatch(PAN_REGEX, pan))

def validate_aadhaar(aadhaar):
    """Validate Aadhaar format."""
    return bool(re.fullmatch(AADHAAR_REGEX, aadhaar))

def validate_email(email):
    """Validate email format."""
    return bool(re.fullmatch(EMAIL_REGEX, email))

def validate_mobile(mobile):
    """Validate mobile format."""
    return bool(re.fullmatch(MOBILE_REGEX, mobile))

def is_blacklisted_pan(pan):
    """Check if PAN is blacklisted."""
    return pan in BLACKLISTED_PAN

def is_blacklisted_aadhaar(aadhaar):
    """Check if Aadhaar is blacklisted."""
    return aadhaar in BLACKLISTED_AADHAAR

def clean_data(df):
    """
    Clean the KYC data by removing duplicates and handling missing values.

    Args:
        df (pd.DataFrame): The raw KYC data.

    Returns:
        pd.DataFrame: The cleaned KYC data.
    """
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle missing values
    df = df.dropna(subset=["Name", "PAN", "Aadhaar", "Email", "Mobile", "DOB"])
    df = df.fillna("")
    
    # Format corrections
    df["PAN"] = df["PAN"].str.upper()
    df["Aadhaar"] = df["Aadhaar"].str.replace(r"[^0-9 ]", "", regex=True)
    df["Mobile"] = df["Mobile"].astype(str).str[-10:]
    
    return df

def apply_rule_based_detection(df):
    """
    Apply rule-based fraud detection to the KYC data.

    Args:
        df (pd.DataFrame): The cleaned KYC data.

    Returns:
        pd.DataFrame: The data with rule-based fraud flags.
    """
    def flag_record(row):
        """Flag a record as suspicious based on rules."""
        suspicious = False
        reasons = []
        
        if not validate_pan(row["PAN"]):
            suspicious = True
            reasons.append("Invalid PAN format")
        
        if not validate_aadhaar(row["Aadhaar"]):
            suspicious = True
            reasons.append("Invalid Aadhaar format")
        
        if not validate_email(row["Email"]):
            suspicious = True
            reasons.append("Invalid Email")
        
        if not validate_mobile(row["Mobile"]):
            suspicious = True
            reasons.append("Invalid Mobile")
        
        if is_blacklisted_pan(row["PAN"]):
            suspicious = True
            reasons.append("Blacklisted PAN")
        
        if is_blacklisted_aadhaar(row["Aadhaar"]):
            suspicious = True
            reasons.append("Blacklisted Aadhaar")
        
        # High transaction amount flag
        if row["TxnAmount"] > 50000:
            suspicious = True
            reasons.append("High transaction amount")
        
        # High transaction count flag
        if row["TxnCount"] > 30:
            suspicious = True
            reasons.append("High transaction count")
        
        if suspicious:
            return "Suspicious", "; ".join(reasons)
        return "Valid", ""
    
    results = df.apply(flag_record, axis=1, result_type='expand')
    df["RuleFlag"] = results[0]
    df["RuleReason"] = results[1]
    
    return df

def process_kyc_data(df):
    """
    Complete data processing pipeline: clean data and apply rule-based detection.

    Args:
        df (pd.DataFrame): The raw KYC data.

    Returns:
        pd.DataFrame: The processed KYC data with rule-based flags.
    """
    df_cleaned = clean_data(df)
    df_processed = apply_rule_based_detection(df_cleaned)
    return df_processed

if __name__ == "__main__":
    # Example usage when run directly
    from data_generator import generate_synthetic_kyc_data
    
    # Generate sample data
    df = generate_synthetic_kyc_data(n_records=20)
    print("Original data:")
    print(df.head())
    
    # Process the data
    df_processed = process_kyc_data(df)
    print("\\nProcessed data:")
    print(df_processed[["Name", "PAN", "RuleFlag", "RuleReason"]].head())




def add_id_verification_features(df, verification_results):
    """
    Adds the new ID verification features to the DataFrame.

    Args:
        df (pd.DataFrame): The KYC data.
        verification_results (dict): A dictionary containing the results from
                                     ID document and facial verification.

    Returns:
        pd.DataFrame: The DataFrame with added verification features.
    """
    # Add features from the verification results
    df["ID_Doc_Authenticity_Score"] = verification_results.get("authenticity_score", 0.0)
    df["Liveness_Score"] = verification_results.get("liveness_score", 0.0)
    df["Face_Match_Confidence"] = verification_results.get("face_match_confidence", 0.0)

    # Simulate data consistency checks
    extracted_data = verification_results.get("extracted_data", {})
    df["OCR_Name_Mismatch_Flag"] = (df["Name"] != extracted_data.get("name", "")).astype(int)
    df["OCR_DOB_Mismatch_Flag"] = (df["DOB"] != extracted_data.get("dob", "")).astype(int)

    # Add new rules based on verification scores
    def flag_verification_issues(row):
        suspicious = False
        reasons = []

        if row["ID_Doc_Authenticity_Score"] < 0.5:
            suspicious = True
            reasons.append("Low Document Authenticity")
        if row["Liveness_Score"] < 0.5:
            suspicious = True
            reasons.append("Liveness Check Failed")
        if row["Face_Match_Confidence"] < 0.6:
            suspicious = True
            reasons.append("Face Match Failed")
        if row["OCR_Name_Mismatch_Flag"] == 1:
            suspicious = True
            reasons.append("Name Mismatch with ID")

        if suspicious:
            return "Suspicious", "; ".join(reasons)
        return "Valid", ""

    # Append new rule reasons to existing ones
    verification_results_df = df.apply(flag_verification_issues, axis=1, result_type="expand")
    df["RuleFlag"] = df.apply(lambda row: "Suspicious" if row["RuleFlag"] == "Suspicious" or verification_results_df.loc[row.name, 0] == "Suspicious" else "Valid", axis=1)
    df["RuleReason"] = df["RuleReason"] + "; " + verification_results_df[1]
    df["RuleReason"] = df["RuleReason"].str.strip("; ")

    return df


