import os
import time
import cv2
from qrlocator import QRLocator

from calibration_settings import data as calibration_data

import numpy as np

QR_CODE_SIZE_INCHES = 7.93


def calibrate_qr_locator(calibration_images_folder):
    best_error = float('inf')
    best_focal_length = None
    best_sensor_width = None
    best_focal_angle_scalar = None
    best_qr_code_details = []
    
    calibration_images = []

    for image_name in os.listdir(calibration_images_folder):
        if not image_name.endswith('.jpg'):
            continue

        image_path = os.path.join(calibration_images_folder, image_name)
        calibration_images.append(
            [image_name, QRLocator(image_path, 1, 1, 1, QR_CODE_SIZE_INCHES)])
        
    step_counts = [20, 10, 5, 2.5, 1, .5, .1, .05, .01]
    
    best_focal_length = 51
    best_sensor_width = 51
    best_focal_angle_scalar = 1.1


    for i in range(len(step_counts)):

        step_count = step_counts[i]
        prev_step_count = step_counts[i-1] if i > 0 else 50
        prev_step_count = prev_step_count*1.1 if prev_step_count*1.1 < 50 else prev_step_count

        best_focal_length_loop = best_focal_length
        best_sensor_width_loop = best_sensor_width
        best_focal_angle_scalar_loop = best_focal_angle_scalar


        for focal_length in np.arange(best_focal_length_loop-prev_step_count, best_focal_length_loop+prev_step_count, step_count):
            for sensor_width in np.arange(best_sensor_width_loop-prev_step_count, best_sensor_width_loop+prev_step_count, step_count):
                for focal_angle_scalar in np.arange(best_focal_angle_scalar_loop-prev_step_count/50, best_focal_angle_scalar_loop+prev_step_count/50, step_count/50):

                    total_error = 0
                    qr_code_details = []

                    for calibration_section in calibration_images:

                        image_name = calibration_section[0]
                        qr_locator = calibration_section[1]

                        qr_locator.focal_length_mm = focal_length
                        qr_locator.sensor_width_mm = sensor_width
                        qr_locator.focal_angle_scalar = focal_angle_scalar
                        qr_locator.process_codes()

                        real_y = int(image_name.replace('ft.jpg', '')) * 12

                        qr_code_details.append(f"{image_name}")

                        for data, qr_code in qr_locator.codes.items():
                            known_y = real_y
                            known_x = calibration_data[data]['x']
                            error = abs(qr_code.y - known_y) + abs(qr_code.x - known_x)
                            total_error += error
                            qr_code_details.append(
                                f"QR Code: {data}, Error: {error}, Y: {qr_code.y}, Known Y: {known_y}, X: {qr_code.x}, Known X: {known_x}")
                    
                    if total_error < best_error:
                        best_error = total_error
                        best_focal_length = focal_length
                        best_sensor_width = sensor_width
                        best_focal_angle_scalar = focal_angle_scalar
                        best_qr_code_details = qr_code_details

                    print(f"Focal Length: {focal_length}, Sensor Width: {sensor_width}, Focal Angle Scalar: {focal_angle_scalar}, Total Error: {total_error}")

    with open('calibration_results.txt', 'w') as file:
        file.write(f"Best Focal Ratio: {best_focal_length / best_sensor_width}\n")
        print(f"Best Focal Ratio: {best_focal_length / best_sensor_width}")
        print(f"Best Focal Ratio: {best_sensor_width / best_focal_length}")
        file.write(f"Best Focal Length: {best_focal_length}\n")
        print(f"Best Focal Length: {best_focal_length}")
        file.write(f"Best Sensor Width: {best_sensor_width}\n")
        print(f"Best Sensor Width: {best_sensor_width}")
        file.write(f"Best Focal Angle Scalar: {best_focal_angle_scalar}\n")
        print(f"Best Focal Angle Scalar: {best_focal_angle_scalar}")
        file.write(f"Minimum Total Error: {best_error}\n")
        print(f"Minimum Total Error: {best_error}")
        
        # Write the best QR code details to the file
        file.write("Best QR Code Details:\n")
        for detail in best_qr_code_details:
            file.write(detail + '\n')
            print(detail)


if __name__ == "__main__":
    calibrate_qr_locator(r'calibration\dev_calibration_images')
