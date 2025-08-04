
import random
import re
import os
from PIL import Image
import pytesseract
from google.cloud import vision

class IDDocumentProcessor:
    def __init__(self):
        self.document_blacklist = {"123456789012", "987654321098"}

    def process_document(self, document_image_path: str):
        print(f"Processing document: {document_image_path}")

        extracted_data = self._perform_ocr(document_image_path)
        authenticity_score = self._simulate_authenticity_check(extracted_data)

        return {
            "extracted_data": extracted_data,
            "authenticity_score": authenticity_score,
            "document_image_path": document_image_path
        }

    def _perform_ocr(self, document_image_path: str):
        try:
            client = vision.ImageAnnotatorClient()

            with open(document_image_path, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)

            response = client.text_detection(image=image)
            texts = response.text_annotations

            full_text = texts[0].description if texts else ""
            print(f"Google Vision OCR Extracted Text:\n{full_text}")

            # Attempt to parse common fields from the extracted text
            name = "N/A"
            dob = "N/A"
            document_id = "N/A"
            address = "N/A"
            expiry_date = "N/A"
            document_type = "N/A"
            gender = "N/A"
            name_match = re.search(r'(?:Name|Full Name|Nom)\s*:\s*([A-Z\s]+)', full_text, re.IGNORECASE)
            if name_match: name = name_match.group(1).strip()
            else: # Try to find a prominent name if no label
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                if len(lines) > 1: # Assume first non-empty line might be name if it's all caps
                    if lines[0].isupper() and len(lines[0].split()) > 1: name = lines[0]

            # DOB: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
            dob_match = re.search(r'\b(?:DOB|Date of Birth)\s*[:]?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b', full_text, re.IGNORECASE)
            if dob_match: dob = dob_match.group(1)

            # Document ID: Example for a generic IDN format
            doc_id_match = re.search(r'\b(?:Document ID|ID No|IDN)\s*[:]?\s*([A-Z0-9]+)\b', full_text, re.IGNORECASE)
            if doc_id_match: document_id = doc_id_match.group(1)

            # Address: Very hard to parse reliably with simple regex. Placeholder.
            address_match = re.search(r'(?:Address|Addr)\s*[:]?\s*(.+)', full_text, re.IGNORECASE)
            if address_match: address = address_match.group(1).split('\n')[0].strip()

            # Expiry Date: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
            expiry_match = re.search(r'\b(?:Expiry Date|Exp)\s*[:]?\s*(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})\b', full_text, re.IGNORECASE)
            if expiry_match: expiry_date = expiry_match.group(1)

            # Document Type: Simple keywords
            if re.search(r'passport', full_text, re.IGNORECASE): document_type = "Passport"
            elif re.search(r'national id|id card', full_text, re.IGNORECASE): document_type = "National ID Card"
            elif re.search(r'driver.?s license', full_text, re.IGNORECASE): document_type = "Driver\'s License"

            # Gender: M/F
            gender_match = re.search(r'\b(?:Gender|Sex)\s*[:]?\s*([M|F])\b', full_text, re.IGNORECASE)
            if gender_match: gender = gender_match.group(1).upper()

            return {
                "name": name,
                "dob": dob,
                "document_id": document_id,
                "address": address,
                "expiry_date": expiry_date,
                "document_type": document_type,
                "gender": gender,
                "document_photo_for_matching_path": document_image_path # Still using original image for face extraction
            }
        except Exception as e:
            print(f"Error during Google Vision OCR: {e}")
            return {
                "name": "OCR_Error",
                "dob": "OCR_Error",
                "document_id": "OCR_Error",
                "address": "OCR_Error",
                "expiry_date": "OCR_Error",
                "document_type": "OCR_Error",
                "gender": "OCR_Error",
                "document_photo_for_matching_path": document_image_path
            }
    def _simulate_authenticity_check(self, extracted_data: dict) -> float:
        score = random.uniform(0.8, 0.99)

        if extracted_data["document_id"] in self.document_blacklist:
            score -= 0.2
        if extracted_data["expiry_date"] != "N/A" and extracted_data["expiry_date"] < "2025-07-26":
            score -= 0.1

        return max(0.0, score)

if __name__ == '__main__':
    processor = IDDocumentProcessor()
    sample_doc_path = "/home/ubuntu/kyc_simplified_v2/data/sample_id_card.jpg"
    
    if not os.path.exists(sample_doc_path):
        os.makedirs(os.path.dirname(sample_doc_path), exist_ok=True)
        # Create a dummy image file for testing pytesseract
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (600, 400), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        try:
            # Try to use a default font that should be available
            fnt = ImageFont.truetype("DejaVuSans-Bold.ttf", 20) # Common font on Linux
        except IOError:
            fnt = ImageFont.load_default() # Fallback to default if specific font not found

        d.text((50,50), "Name: JOHN DOE", fill=(0,0,0), font=fnt)
        d.text((50,100), "DOB: 1990-01-01", fill=(0,0,0), font=fnt)
        d.text((50,150), "Document ID: ABC123456789", fill=(0,0,0), font=fnt)
        d.text((50,200), "Expiry Date: 2030-12-31", fill=(0,0,0), font=fnt)
        d.text((50,250), "Document Type: National ID Card", fill=(0,0,0), font=fnt)
        d.text((50,300), "Gender: M", fill=(0,0,0), font=fnt)
        img.save(sample_doc_path)

    doc_result = processor.process_document(sample_doc_path)
    print("\n--- Document Processing Result ---")
    print("Extracted Data: ", doc_result["extracted_data"])
    print("Authenticity Score: {:.2f}".format(doc_result["authenticity_score"]))
    print("Document Photo Path for Matching:", doc_result["extracted_data"]["document_photo_for_matching_path"])

    # Example with a dummy expired document
    expired_doc_path = "/home/ubuntu/kyc_simplified_v2/data/sample_expired_id.jpg"
    if not os.path.exists(expired_doc_path):
        img_exp = Image.new('RGB', (600, 400), color = (255, 255, 255))
        d_exp = ImageDraw.Draw(img_exp)
        try:
            fnt_exp = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        except IOError:
            fnt_exp = ImageFont.load_default()
        d_exp.text((50,50), "Name: JANE DOE", fill=(0,0,0), font=fnt_exp)
        d_exp.text((50,100), "DOB: 1980-05-10", fill=(0,0,0), font=fnt_exp)
        d_exp.text((50,150), "Document ID: EXP987654321", fill=(0,0,0), font=fnt_exp)
        d_exp.text((50,200), "Expiry Date: 2024-01-01", fill=(0,0,0), font=fnt_exp)
        img_exp.save(expired_doc_path)

    doc_result_expired = processor.process_document(expired_doc_path)
    print("\n--- Expired Document Result ---")
    print("Extracted Data:", doc_result_expired["extracted_data"])
    print("Authenticity Score: {:.2f}".format(doc_result_expired["authenticity_score"]))

    # Example with a dummy blacklisted document
    blacklisted_doc_path = "/home/ubuntu/kyc_simplified_v2/data/sample_blacklisted_id.jpg"
    if not os.path.exists(blacklisted_doc_path):
        img_bl = Image.new('RGB', (600, 400), color = (255, 255, 255))
        d_bl = ImageDraw.Draw(img_bl)
        try:
            fnt_bl = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        except IOError:
            fnt_bl = ImageFont.load_default()
        d_bl.text((50,50), "Name: BLACKLISTED USER", fill=(0,0,0), font=fnt_bl)
        d_bl.text((50,100), "Document ID: 123456789012", fill=(0,0,0), font=fnt_bl)
        img_bl.save(blacklisted_doc_path)

    doc_result_blacklisted = processor.process_document(blacklisted_doc_path)
    print("\n--- Blacklisted Document Result ---")
    print("Extracted Data:", doc_result_blacklisted["extracted_data"])
    print("Authenticity Score: {:.2f}".format(doc_result_blacklisted["authenticity_score"]))


