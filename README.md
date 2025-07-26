# Simplified KYC Fraud Detection Project

This project provides a simplified, end-to-end pipeline for KYC (Know Your Customer) data processing and fraud detection using machine learning and rule-based flagging. It aims to be a cleaner, more straightforward version of the original concept, addressing common errors and improving maintainability.

## Features

-   **Synthetic Data Generation**: Creates realistic-looking KYC data for development and testing purposes.
-   **Data Processing**: Cleans raw KYC data and applies rule-based flags for suspicious entries.
-   **Machine Learning Fraud Detection**: Trains and uses a Random Forest Classifier to predict fraud based on processed data.
-   **Interactive Dashboard**: A Streamlit application for visualizing fraud detection results and key data insights.

## Project Structure

```
kyc_simplified/
├── data/                     # Stores raw, processed, and final prediction CSVs
├── models/                   # Stores the trained ML model (fraud_detection_model.pkl)
├── src/                      # Contains core Python scripts
│   ├── data_generator.py     # Generates synthetic KYC data
│   ├── data_processor.py     # Cleans data and applies rule-based detection
│   └── fraud_model.py        # Handles ML model training and prediction
├── dashboard.py              # Streamlit application for visualization
├── main.py                   # Orchestrates the entire data pipeline
├── README.md                 # Project overview and instructions
└── requirements.txt          # Python dependencies
```

## Setup and Installation

1.  **Navigate to the project directory:**
    ```bash
    cd kyc_simplified
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

### 1. Run the Data Pipeline

This script will generate synthetic data, process it, train the ML model, and make predictions, saving all intermediate and final results in the `data/` and `models/` directories.

```bash
python main.py
```

### 2. Launch the Dashboard

After running the data pipeline, you can launch the Streamlit dashboard to visualize the results. Make sure your virtual environment is still active.

```bash
streamlit run dashboard.py
```

This will open the dashboard in your web browser.

## Key Concepts

-   **Rule-Based Flagging**: Identifies suspicious activities based on predefined rules (e.g., invalid data formats, blacklisted entries, high transaction values).
-   **Machine Learning Prediction**: Uses a trained model to predict the likelihood of fraud based on various features, providing a `Fraud_Probability` score.
-   **Combined Approach**: The project uses both rule-based and ML-based methods to provide a comprehensive fraud detection system.

## Troubleshooting

-   **`PermissionError`**: Ensure you have write permissions for the project directory and its subfolders (e.g., `data/`, `models/`). On Windows, try running your terminal as an administrator.
-   **`ModuleNotFoundError`**: Ensure your virtual environment is activated and all dependencies are installed (`pip install -r requirements.txt`). Also, verify that the `src` directory is correctly structured and its files are present.
-   **Dashboard showing "No data found"**: Make sure you have successfully run `python main.py` at least once to generate the necessary `final_kyc_predictions.csv` file.


