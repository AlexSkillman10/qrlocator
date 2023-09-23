import cv2
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pyzbar.pyzbar import decode

def convert_focal_length_to_pixels(focal_length_mm, image_width_pixels, sensor_width_mm):
    return (focal_length_mm / sensor_width_mm) * image_width_pixels

def calculate_distance_to_camera(known_width, focal_length, per_width):
    return (known_width * focal_length) / per_width

def calculate_angle_and_map_2d(centroid_x, distance_inches, img_center):
    delta_x = centroid_x - img_center
    angle = math.degrees(math.atan2(delta_x, distance_inches))

    ##dampen degree - temp fix for larger issue
    angle = 0
    
    x = distance_inches * math.sin(math.radians(angle))
    y = distance_inches * math.cos(math.radians(angle))
    return angle, x, y


class QRCode ():
    def __init__(self, data, angle, x, y):
        self.data = data
        self.angle = angle
        self.x = x
        self.y = y


class QRLocator ():

    def __init__(self, image_path, focal_length_mm, sensor_width_mm, qr_code_size_inches):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        self.decoded_objects = decode(self.image)

        self.focal_length_mm = focal_length_mm
        self.sensor_width_mm = sensor_width_mm
        self.qr_code_size_inches = qr_code_size_inches
        self.qr_code_size_in_mm = qr_code_size_inches * 25.4

        self.img_center = self.image.shape[1] / 2

        self.codes = {}

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
            
            angle, x, y = calculate_angle_and_map_2d(centroid_x, distance_inches, self.img_center)
            
            qr_code = QRCode(qr_code.data.decode('utf-8'), angle, x, y)
            self.codes[qr_code.data] = qr_code


    def show_visualization():
        plt.figure(figsize=(10, 10))
        plt.axhline(0, color='k')
        plt.scatter(0, 0, c='r', label='Camera')











