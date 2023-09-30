# QRlocator

## Overview
This code provides a class named `QRlocator` that allows users to locate QR codes within 3D space given an image. It uses the OpenCV and Pyzbar libraries to scan and decode the QR codes, but you can also use other QR code scanning libraries to get and then add the QR code information to the class using `add_qr_code`. This class mainly provides the `X`, `Y`, and `Z` coordinates of the center point of a code, where `Y` is a horizontal axis parallel to the camera's direction, `X` is a horizontal axis perpendicular to the camera's direction, and `Z` is a vertical axis representing the codes height.


## How to Use

The creation of the QRlocator class requires 4 parameters. It is very likely that you don't know some of these values, or the values you have are incorrect. This tool can automatically find the 3 best fit values for your camera:

- `image_path` (str): The file path of the image you wish to scan.
- `focal_ratio` (float): This is the focal length in mm over the sensor width in mm (focal/sensor) of the camera that was used to take the current image.
- `x_focal_angle_scalar` (float): A scalar value to correct the x-angle calculated from the image.
- `z_focal_angle_scalar` (float): A scalar value to correct the z-angle calculated from the image.
```python
qr_locator = QRlocator('path_to_image', focal_ratio, x_focal_angle_scalar, z_focal_angle_scalar)
```

### 1. Function

Once you have an image loaded, you can populate the class with the image's QR codes by running:
```python
qr_locator.scan_image()
```

To retrieve the dictionary of all QR codes found in your class, run:
```python
qr_codes = qr_locator.get_qr_codes()
```

To retrieve a specific QR code by its data, for example a QRcode that when scanned appears as `134564`, run:

```python
qr_code = qr_locator.get_qr_code('134564')
```

### 4. Calculating Positions
To get the positions of the QR codes in 3D space, run the following:

```python
x_position = qr_locator.get_x_position('data', qr_code_size_mm)
y_position = qr_locator.get_y_position('data', qr_code_size_mm)
z_position = qr_locator.get_z_position('data', qr_code_size_mm)
```

- `data` (str): What appears when you scan the code. This is used to identify the code
- `qr_code_size_mm` (float): The length of the QR code's sides in mm

### 5. Visualization
To visualize the positions of the class QR codes in XY and XZ planes, run:

```python
qr_locator.show_visualization(qr_code_size_mm)
```
Currently this will interpret all QR codes as the same size, you can get around this by entering particular QR codes as a second paramter.

