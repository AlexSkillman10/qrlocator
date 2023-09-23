import os
import cv2
from qrlocator import QRLocator

from calibration_settings import data as calibration_data

import numpy as np

QR_CODE_SIZE_INCHES = 7.93


def calibrate_qr_locator(calibration_images_folder):
    best_error = float('inf')
    best_focal_length = None
    best_sensor_width = None

    calibration_images = []

    for image_name in os.listdir(calibration_images_folder):
        if not image_name.endswith('.jpg'):
            continue

        image_path = os.path.join(calibration_images_folder, image_name)
        calibration_images.append(
            [image_name, QRLocator(image_path, 1, 1, QR_CODE_SIZE_INCHES)])

    for focal_length in np.arange(20, 30, 0.1):
        for sensor_width in np.arange(30, 40, 0.1):

            total_error = 0

            for calibration_section in calibration_images:

                image_name = calibration_section[0]
                qr_locator = calibration_section[1]

                qr_locator.focal_length_mm = focal_length
                qr_locator.sensor_width_mm = sensor_width
                qr_locator.process_codes()

                real_y = int(image_name.replace('ft.jpg', '')) * 12

                for data, qr_code in qr_locator.codes.items():
                    known_y = real_y
                    error = abs(qr_code.y - known_y)
                    total_error += error
                    # print(f"QR Code: {data}, Error: {error}, Y: {qr_code.y}, Known Y: {known_y}")

            if total_error < best_error:
                best_error = total_error
                best_focal_length = focal_length
                best_sensor_width = sensor_width

            print(
                f"Focal Length: {focal_length}, Sensor Width: {sensor_width}, Total Error: {total_error}")

    with open('calibration_results.txt', 'w') as file:
        file.write(f"Best Focal Length: {best_focal_length}\n")
        print(f"Best Focal Length: {best_focal_length}")
        file.write(f"Best Sensor Width: {best_sensor_width}\n")
        print(f"Best Sensor Width: {best_sensor_width}")
        file.write(f"Minimum Total Error: {best_error}\n")
        print(f"Minimum Total Error: {best_error}")


if __name__ == "__main__":
    calibrate_qr_locator(r'calibration\dev_calibration_images')
