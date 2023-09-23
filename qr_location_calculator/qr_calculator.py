import cv2
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from pyzbar.pyzbar import decode


FOCAL_LENGTH_MM = 26.0
SENSOR_WIDTH_MM = 36.0
QR_CODE_SIZE_INCHES = 5.4
IMAGE_PATH = r'qr_location_calculator\calibration_images\6ft.jpg'

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

def main(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print("Unable to load image")
        return
    
    known_width_mm = QR_CODE_SIZE_INCHES * 25.4

    decoded_objects = decode(image)
    if not decoded_objects:
        print("No QR Code found")
        return
    
    plt.figure(figsize=(10, 10))
    plt.axhline(0, color='k')
    plt.scatter(0, 0, c='r', label='Camera')
    
    img_center = image.shape[1] / 2
    for qr_code in decoded_objects:
        print(f"{qr_code.data.decode('utf-8')}")
        points = qr_code.polygon

        if len(points) < 2:
            print("Not enough points to calculate per_width")
            continue
        
        centroid_x = sum([point[0] for point in points]) / len(points)
        focal_length_pixels = convert_focal_length_to_pixels(FOCAL_LENGTH_MM, image.shape[1], SENSOR_WIDTH_MM)
        per_width = cv2.norm(points[0], points[1])
        distance_mm = calculate_distance_to_camera(known_width_mm, focal_length_pixels, per_width)
        distance_inches = distance_mm / 25.4
        
        angle, x, y = calculate_angle_and_map_2d(centroid_x, distance_inches, img_center)
        print(f"{distance_inches / 12} feet, {angle} degrees")
        print(f"x={x} inches, y={y} inches")
        print()

        x = x / 12
        y = y / 12
        
        plt.scatter(x, y, label=f"QR Code: {qr_code.data.decode('utf-8')}")
        
        plt.annotate(qr_code.data.decode('utf-8'), (x, y), textcoords="offset points", xytext=(0, -10), ha='center')
        
        # rectangle = Rectangle((x - .2/2, y), .2, .2, fill=True, color='orange', edgecolor='orange', linewidth=2)
        # plt.gca().add_patch(rectangle)
    
    plt.xlabel('X (feet)')
    plt.ylabel('Y (feet)')
    plt.legend(loc='lower left')
    plt.title('QR Code Location')
    plt.show()

if __name__ == "__main__":
    main(IMAGE_PATH)