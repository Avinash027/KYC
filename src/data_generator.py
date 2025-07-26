import pandas as pd
from faker import Faker
import random
import re

# Initialize Faker
fake = Faker()

# Blacklisted entities (for demonstration - in real app, these would be external)
BLACKLISTED_PAN = {"ABCDE1234F", "PQRST6789L"}
BLACKLISTED_AADHAAR = {"1234 5678 9012", "1111 2222 3333"}

def generate_synthetic_kyc_data(n_records=1000):
    """
    Generates synthetic KYC (Know Your Customer) data.

    Args:
        n_records (int): The number of synthetic records to generate.

    Returns:
        pd.DataFrame: A DataFrame containing the synthetic KYC data.
    """
    data = []
    for _ in range(n_records):
        name = fake.name()
        pan = fake.unique.bothify(text='?????####?').upper()
        aadhaar = f"{fake.random_number(digits=4):04d} {fake.random_number(digits=4):04d} {fake.random_number(digits=4):04d}"
        email = fake.email()
        mobile = fake.msisdn()[-10:]
        address = fake.address().replace("\n", ", ")
        txn_count = random.randint(1, 50)
        txn_amount = round(random.uniform(100, 100000), 2)
        # Simulate a small percentage of blacklisted entries for testing
        if random.random() < 0.02: # 2% chance of blacklisted PAN
            pan = random.choice(list(BLACKLISTED_PAN))
        if random.random() < 0.02: # 2% chance of blacklisted Aadhaar
            aadhaar = random.choice(list(BLACKLISTED_AADHAAR))

        data.append({
            "CustomerID": fake.uuid4(),
            "Name": name,
            "DOB": fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d"),
            "PAN": pan,
            "Aadhaar": aadhaar,
            "Email": email,
            "Mobile": mobile,
            "Address": address,
            "TxnCount": txn_count,
            "TxnAmount": txn_amount,
        })
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Example usage when run directly
    df = generate_synthetic_kyc_data(n_records=50)
    print("Generated 50 synthetic KYC records:")
    print(df.head())
    # In a real pipeline, this would be saved to a specific path
    # df.to_csv("../data/sample_kyc_data.csv", index=False)


