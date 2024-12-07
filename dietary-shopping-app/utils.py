import cv2

def decode_barcode_opencv(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    detector = cv2.barcode_BarcodeDetector()
    ok, decoded_info, _, _ = detector.detectAndDecode(gray)
    if ok:
        return decoded_info[0]  # Return the first decoded barcode
    return None
