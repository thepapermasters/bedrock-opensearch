import io

from PIL import Image, ImageDraw


def process_rekognition_labels(rekognition_labels_results):
    """
    Process the Rekognition labels results.
    :param rekognition_labels_results: The Rekognition labels results.
    :return: The processed Rekognition labels results.
    """
    labels = []
    categories = []
    parents = []

    for label in rekognition_labels_results['Labels']:
        if label is not None:
            if label['Name'] is not None:
                if label['Name'] not in labels:
                    labels.append(label['Name'])
            for parent in label['Parents']:
                if parent is not None:
                    if parent['Name'] not in parents:
                        parents.append(parent['Name'])
            for category in label['Categories']:
                if category is not None:
                    if category['Name'] not in categories:
                        categories.append(category['Name'])
    return {"Label": labels, "Category": categories, "Parent": parents}


def process_rekognition_face_details(rekognition_face_details_results):
    """
    Process the Rekognition face details results.
    :param rekognition_face_details_results: The Rekognition face details results.
    :return: The processed Rekognition results.
    """
    emotions = []
    age_range = {"Low": 0, "High": 0}
    gender = ""

    for detail in rekognition_face_details_results['FaceDetails']:
        if detail is not None:
            if detail['Emotions'] is not None:
                if detail['Emotions'] not in emotions:
                    emotions.append(detail['Emotions'])
            if detail['AgeRange'] is not None:
                age_range = {"Low": detail['AgeRange']['Low'], "High": detail['AgeRange']['High']}
            if detail['Gender'] is not None:
                gender = detail['Gender']['Value']

    return {"Emotion": emotions, "AgeRange": age_range, "Gender": gender}


def process_rekognition_text(rekognition_text_results):
    """
    Process the Rekognition detected text results.
    :param rekognition_text_results: The Rekognition detected text results.
    :return: The processed Rekognition detected text results.
    """
    detected_text = ""
    type_text = ""
    confidence = ""

    for text in rekognition_text_results['TextDetections']:
        if text is not None:
            if text['DetectedText'] is not None:
                detected_text = text['DetectedText']
                type_text = text['Type']
                confidence = text['Confidence']
    return {"DetectedText": detected_text, "Type": type_text, "Confidence": confidence}


def process_rekognition_moderation_label(rekognition_moderation_label_results):
    """
    Process the Rekognition face details results.
    :param rekognition_moderation_label_results.
    :return: The processed Rekognition results.
    """
    name = []
    parent_name = []
    confidence = []

    for label in rekognition_moderation_label_results['Labels']:
        if label is not None:
            if label['Name'] is not None:
                if label['Name'] not in name:
                    name.append(label['Name'])
            if label['ParentName'] is not None:
                if label['ParentName'] not in parent_name:
                    parent_name.append(label['ParentName'])
            if label['Confidence'] is not None:
                if label['Confidence'] not in confidence:
                    confidence.append(label['Confidence'])
    return {"Name": name, "ParentName": parent_name, "Confidence": confidence}


def add_bounding_box(image, box, color):
    """
    Draws bounding boxes on an image and shows it with the default image viewer.

    :param image: The image to draw, as bytes.
    :param box: A list of lists of bounding boxes to draw on the image.
    :param color: A list of colors to use to draw the bounding boxes.
    """
    print("box:::", box)
    draw = ImageDraw.Draw(image)

    left = image.width * box["Left"]
    top = image.height * box["Top"]
    right = (image.width * box["Width"]) + left
    bottom = (image.height * box["Height"]) + top
    draw.rectangle([left, top, right, bottom], outline=color, width=12)
    return image


def add_polygons(image_bytes, polygons, color):
    """
    Draws polygons on an image and shows it with the default image viewer.

    :param image_bytes: The image to draw, as bytes.
    :param polygons: The list of polygons to draw on the image.
    :param color: The color to use to draw the polygons.
    """
    image = Image.open(io.BytesIO(image_bytes))
    draw = ImageDraw.Draw(image)
    for polygon in polygons:
        draw.polygon(
            [
                (image.width * point["X"], image.height * point["Y"])
                for point in polygon
            ],
            outline=color,
        )
    return image


def save_image_with_bounding_box(feature, image_id, image, labels):
    if feature == 'labels':
        for label in labels['Labels']:
            for instance in label['Instances']:
                image = add_bounding_box(image, instance['BoundingBox'], 'red')
                image.save(f"{image_id}.jpeg")
    if feature == 'faces':
        for instance in labels['Instances']:
            pass
