import logging

import boto3

from constants import MAX_LABELS, MIN_CONFIDENCE, REGION_AWS, ATTRIBUTES

logger = logging.getLogger(__name__)


class CreateRekognition:
    def __init__(self, image):
        """
        Initializes the image object.
        """
        self.image = image
        # Initialize the boto3 client for Rekognition
        self.client_rekognition = boto3.client("rekognition", region_name=REGION_AWS)

    def rek_detect_labels(self, max_labels: int = MAX_LABELS, min_confidence: int = MIN_CONFIDENCE):
        if max_labels is None:
            max_labels = MAX_LABELS
        if min_confidence is None:
            min_confidence = MIN_CONFIDENCE
        try:
            # Rekognition to detect labels in the image
            response_labels = self.client_rekognition.detect_labels(
                Image={'Bytes': self.image},
                MaxLabels=max_labels,
                MinConfidence=min_confidence,
            )
            return response_labels
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise Exception("An error occurred:::", str(e))

    def rek_detect_face_details(self, attributes: list = None):
        if attributes is None:
            attributes = ATTRIBUTES
        try:
            # Rekognition to detect facial emotions in the image
            response_face_details = self.client_rekognition.detect_faces(
                Image={'Bytes': self.image},
                Attributes=attributes,
            )
            return response_face_details
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise Exception("An error occurred:::", str(e))

    def rek_detect_text(self):
        try:
            # Rekognition to detects text in the image
            response_text = self.client_rekognition.detect_text(
                Image={'Bytes': self.image},
            )
            return response_text
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise Exception("An error occurred:::", str(e))

    def rek_detect_moderation_labels(self):
        """
       Detects moderation labels in the image. Moderation labels identify content
       that may be inappropriate for some audiences.

       :return: The list of moderation labels found in the image.
        """
        try:
            # Rekognition to detects text in the image
            response = self.client_rekognition.detect_moderation_labels(
                Image={'Bytes': self.image},
            )
            response_moderation_labels = [
                label for label in response["ModerationLabels"]
            ]
            return response_moderation_labels
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise Exception("An error occurred:::", str(e))
