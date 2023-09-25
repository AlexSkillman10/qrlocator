import cv2
import math
import matplotlib.pyplot as plt
from pyzbar.pyzbar import decode

def convert_focal_length_to_pixels(focal_length_mm, image_width_pixels, sensor_width_mm):
    return (focal_length_mm / sensor_width_mm) * image_width_pixels

def calculate_distance_to_camera(known_width, focal_length, per_width):
    return (known_width * focal_length) / per_width

def calculate_angle_and_map_2d(centroid_x, distance_inches, focal_angle_scalar, img_center, image_width_pixels):
    delta_x = centroid_x - img_center
    angle = math.degrees(math.atan(delta_x / image_width_pixels))
    x = math.tan(math.radians(angle)) * distance_inches * focal_angle_scalar
    y = distance_inches
    return angle, x, y

class QRCode:
    def __init__(self, data, angle, x, y):
        self.data = data
        self.angle = angle
        self.x = x
        self.y = y

class QRLocator:
    def __init__(self, image_path, focal_length_mm, sensor_width_mm, focal_angle_scalar, qr_code_size_inches):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        
        if self.image is None:
            raise ValueError("Unable to load image")
        
        self.decoded_objects = decode(self.image)
        self.focal_length_mm = focal_length_mm
        self.sensor_width_mm = sensor_width_mm
        self.focal_angle_scalar = focal_angle_scalar
        self.qr_code_size_inches = qr_code_size_inches
        self.qr_code_size_in_mm = qr_code_size_inches * 25.4
        self.img_center = self.image.shape[1] / 2
        self.codes = {}
        self.process_codes()

    def process_codes(self):
        for qr_code in self.decoded_objects:
            points = qr_code.polygon
            if len(points) < 2:
                print("Not enough points to calculate per_width")
                continue
            centroid_x = sum([point[0] for point in points]) / len(points)
            focal_length_pixels = convert_focal_length_to_pixels(self.focal_length_mm, self.image.shape[1], self.sensor_width_mm)
            per_width = cv2.norm(points[0], points[1])
            distance_mm = calculate_distance_to_camera(self.qr_code_size_in_mm, focal_length_pixels, per_width)
            distance_inches = distance_mm / 25.4
            angle, x, y = calculate_angle_and_map_2d(centroid_x, distance_inches, self.focal_angle_scalar, self.img_center, self.image.shape[1])
            qr_code_obj = QRCode(qr_code.data.decode('utf-8'), angle, x, y)
            self.codes[qr_code_obj.data] = qr_code_obj
            
    def show_visualization(self):
        plt.figure(figsize=(10, 10))
        plt.axhline(0, color='k')
        plt.scatter(0, 0, c='r', label='Camera')

        for data, qr_code in self.codes.items():
            x = qr_code.x / 12  # convert inches to feet
            y = qr_code.y / 12
            plt.scatter(x, y, label=f"QR Code: {data}")
            plt.annotate(data, (x, y), textcoords="offset points", xytext=(0, -10), ha='center')
        
        plt.xlabel('X (feet)')
        plt.ylabel('Y (feet)')
        plt.legend(loc='lower left')
        plt.title('QR Code Location')
        plt.axis('equal') 
        plt.show()


if __name__ == "__main__":
    FOCAL_LENGTH_MM = 26.500000000000007
    SENSOR_WIDTH_MM = 34.20000000000003

    FOCAL_RATIO = FOCAL_LENGTH_MM / SENSOR_WIDTH_MM
    
    BEST_FOCAL_SCALAR = 1.3000000000000003

    # QR_CODE_SIZE_INCHES = 5.35
    # IMAGE_PATH = r'calibration\test_images\IMG_0884.jpg'

    QR_CODE_SIZE_INCHES = 7.93
    IMAGE_PATH = r'calibration\dev_calibration_images\8ft.jpg'
    
    qr_locator = QRLocator(IMAGE_PATH, FOCAL_LENGTH_MM, SENSOR_WIDTH_MM, BEST_FOCAL_SCALAR, QR_CODE_SIZE_INCHES)
    qr_locator.show_visualization()











