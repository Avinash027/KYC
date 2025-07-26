
import random
import os
from google.cloud import vision

class FaceVerifier:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def detect_face(self, image_path: str):
        """
        Detects faces in an image using Google Cloud Vision API.
        Returns the detected face annotations or None if no face is found.
        """
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return None

        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        request = vision.AnnotateImageRequest(
            image=image,
            features=[vision.Feature(type_=vision.Feature.Type.FACE_DETECTION)],
        )
        response = self.client.annotate_image(request=request)
        faces = response.face_annotations

        if not faces:
            print(f"No face detected in {image_path}")
            return None

        # For simplicity, return the first detected face
        return faces[0]

    def match_faces(self, doc_face_annotation, live_face_annotation) -> float:
        """
        Simulates face matching based on whether faces are detected.
        In a real scenario, this would involve comparing face embeddings.
        """
        if doc_face_annotation and live_face_annotation:
            # Simulate a high confidence if both faces are detected
            return random.uniform(0.7, 0.95) # Simulate a good match
        else:
            return random.uniform(0.05, 0.3) # Simulate a low match if one or both are missing

if __name__ == '__main__':
    verifier = FaceVerifier()

    # Create dummy image files for testing
    dummy_dir = "./dummy_images"
    os.makedirs(dummy_dir, exist_ok=True)

    # Create a dummy image with a face (you'd replace this with actual images)
    # For a real test, you'd need actual images with faces
    # Here, we'll just create blank images and simulate success/failure
    
    # Simulate a document photo (e.g., extracted from ID)
    doc_photo_path = "/home/ubuntu/upload/id.jpg"
    live_photo_path = "/home/ubuntu/upload/avinash.jpg"
    non_match_photo_path = "/home/ubuntu/upload/id.jpg"

    # Detect faces
    doc_face_annotation = verifier.detect_face(doc_photo_path)
    live_face_annotation = verifier.detect_face(live_photo_path)
    non_match_face_annotation = verifier.detect_face(non_match_photo_path)

    # Test face matching
    match_score1 = verifier.match_faces(doc_face_annotation, live_face_annotation)
    print(f"\nFace Match Score (Matching): {match_score1:.2f}")

    match_score2 = verifier.match_faces(doc_face_annotation, non_match_face_annotation)
    print(f"Face Match Score (Non-Matching): {match_score2:.2f}")

    # Clean up dummy images
    os.remove(doc_photo_path)
    os.remove(live_photo_path)
    os.remove(non_match_photo_path)
    os.rmdir(dummy_dir)