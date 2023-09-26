import cv2

import math
import matplotlib.pyplot as plt
from pyzbar.pyzbar import decode

def convert_focal_length_to_pixels(focal_ratio, image_width_pixels):
    return focal_ratio * image_width_pixels

def calculate_distance_to_camera(known_width, focal_length, per_width):
    return (known_width * focal_length) / per_width

def calculate_angle_and_map_2d(centroid_x, centroid_y, distance_inches, x_focal_angle_scalar, z_focal_angle_scalar, img_center, image_width_pixels):
    delta_x = centroid_x - img_center
    delta_z = centroid_y - img_center 
    x_angle = math.degrees(math.atan(delta_x / image_width_pixels))
    x = math.tan(math.radians(x_angle)) * distance_inches * x_focal_angle_scalar

    z_angle = -math.degrees(math.atan(delta_z / image_width_pixels))
    z = math.tan(math.radians(z_angle)) * distance_inches * z_focal_angle_scalar

    y = distance_inches
    
    return x_angle, x, y, z

class QRCode:
    def __init__(self, data, angle, x, y, z):
        self.data = data
        self.angle = angle
        self.x = x
        self.y = y
        self.z = z

class QRLocator:
    def __init__(self, image_path, focal_ratio, x_focal_angle_scalar, z_focal_angle_scalar, qr_code_size_inches):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        
        if self.image is None:
            raise ValueError("Unable to load image")
        
        self.decoded_objects = decode(self.image)
        self.focal_ratio = focal_ratio
        self.x_focal_angle_scalar = x_focal_angle_scalar
        self.z_focal_angle_scalar = z_focal_angle_scalar
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
            centriod_y = sum([point[1] for point in points]) / len(points)
            focal_length_pixels = convert_focal_length_to_pixels(self.focal_ratio, self.image.shape[1])
            per_width = cv2.norm(points[0], points[1])
            distance_mm = calculate_distance_to_camera(self.qr_code_size_in_mm, focal_length_pixels, per_width)
            distance_inches = distance_mm / 25.4
            angle, x, y, z = calculate_angle_and_map_2d(centroid_x, centriod_y, distance_inches, self.x_focal_angle_scalar, self.z_focal_angle_scalar, self.img_center, self.image.shape[1])
            qr_code_obj = QRCode(qr_code.data.decode('utf-8'), angle, x, y, z)
            self.codes[qr_code_obj.data] = qr_code_obj
            
    def show_visualization(self):
        fig, axs = plt.subplots(1, 2, figsize=(20, 10))  # 1 row, 2 columns

        # Plot for X and Y
        axs[0].axhline(0, color='k')
        axs[0].scatter(0, 0, c='r', label='Camera')
        for data, qr_code in self.codes.items():
            x = qr_code.x / 12  # convert inches to feet
            y = qr_code.y / 12
            axs[0].scatter(x, y, label=f"QR Code: {data}")
            axs[0].annotate(data, (x, y), textcoords="offset points", xytext=(0, -10), ha='center')
        axs[0].set_xlabel('X (feet)')
        axs[0].set_ylabel('Y (feet)')
        axs[0].legend(loc='lower left')
        axs[0].axis('equal')
        axs[0].set_title('QR Code Location in XY Plane')

        # Plot for Z and X
        # axs[1].axhline(0, color='k')
        # axs[1].scatter(0, 0, c='r', label='Camera')
        for data, qr_code in self.codes.items():
            x = qr_code.x / 12  # convert inches to feet
            z = qr_code.z / 12
            axs[1].scatter(x, z, label=f"QR Code: {data}")
            axs[1].annotate(data, (x, z), textcoords="offset points", xytext=(0, -10), ha='center')
        axs[1].set_xlabel('X (feet)')
        axs[1].set_ylabel('Z (feet)')
        axs[1].legend(loc='lower left')
        axs[1].axis('equal')
        axs[1].set_title('QR Code Location in XZ Plane')

        plt.tight_layout()  # Adjust the spacing between the plots
        plt.show()


if __name__ == "__main__":
    FOCAL_RATIO = 0.7747762957960492
    # FOCAL_RATIO = FOCAL_LENGTH_MM / SENSOR_WIDTH_MM
    
    BEST_X_FOCAL_SCALAR = 1.3069
    BEST_Z_FOCAL_SCALAR = 0.5130000000000011119

    # QR_CODE_SIZE_INCHES = 5.35
    # IMAGE_PATH = r'calibration\test_images\IMG_0897.jpg'

    QR_CODE_SIZE_INCHES = 7.93
    IMAGE_PATH = r'calibration\dev_calibration_images2\7ft.jpg'
    
    qr_locator = QRLocator(IMAGE_PATH, FOCAL_RATIO, BEST_X_FOCAL_SCALAR, BEST_Z_FOCAL_SCALAR, QR_CODE_SIZE_INCHES)
    qr_locator.show_visualization()











