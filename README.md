# tools

Tools used for projects (in Python)

(Written by Claude)

## Image to C Array Converter

Convert images to C header files for ESP32 Arduino projects. This tool accepts any image format and outputs JPEG data as a C array that can be embedded in your firmware.

### Features

- **Multiple Input Formats**: Supports JPEG, PNG, BMP, GIF, TIFF, WebP, and any other PIL-compatible format
- **JPEG Output**: All images are converted to JPEG format for efficient memory usage
- **Auto Resize**: Resizes images to specified dimensions (default: 240x320)
- **Image Transformations**: Flip horizontally or vertically
- **Quality Control**: Adjustable JPEG quality (1-95)
- **PROGMEM Compatible**: Output arrays use `PROGMEM` for ESP32/Arduino

### Requirements

```bash
pip install Pillow
```

### Usage

#### Basic Usage

```bash
python3 image_to_c-array.py input_image.png
```

This creates `photoData.h` with your image resized to 240x320 pixels.

#### Specify Output File

```bash
python3 image_to_c-array.py input_image.png myImage.h
```

#### Custom Dimensions and Quality

```bash
python3 image_to_c-array.py photo.jpg photoData.h 320 240 85
```

Parameters: `<input> <output> <width> <height> <quality>`

#### Image Transformations

```bash
# Flip horizontally (mirror)
python3 image_to_c-array.py photo.jpg photoData.h 240 320 75 --flip-h

# Flip vertically (upside down)
python3 image_to_c-array.py photo.jpg photoData.h 240 320 75 --flip-v

# Both flips
python3 image_to_c-array.py photo.jpg photoData.h 240 320 75 --flip-h --flip-v
```

#### Disable JPEG Optimization

```bash
python3 image_to_c-array.py photo.jpg photoData.h 240 320 75 --no-optimize
```

This makes compression faster but may result in slightly larger files.

### Parameters

#### Positional Arguments

- `input_image` - Path to input image (JPEG, PNG, BMP, GIF, TIFF, WebP, etc.)
- `output_header` - Output .h file (default: `photoData.h`)
- `width` - Target width in pixels (default: `240`)
- `height` - Target height in pixels (default: `320`)
- `quality` - JPEG quality 1-95 (default: `75`)

#### Optional Flags

- `--flip-h` - Flip image horizontally (mirror)
- `--flip-v` - Flip image vertically (upside down)
- `--no-optimize` - Disable JPEG optimization

### Using in Arduino/ESP32 Projects

1. Generate the header file:

   ```bash
   python3 image_to_c-array.py myimage.png myImage.h
   ```

2. Include it in your Arduino sketch:

   ```cpp
   #include "myImage.h"

   void setup() {
     // The image data is now available as:
     // photoData[] - byte array containing JPEG data
     // sizeof(photoData) - size in bytes

     // Example: Display on TFT screen
     tft.drawJpeg(photoData, sizeof(photoData), 0, 0);
   }
   ```

### Output Format

The generated header file contains:

```c
// Generated from: input_image.png
// Size: 240x320 pixels
// JPEG size: 12345 bytes

const unsigned char photoData[] PROGMEM = {
  0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
  // ... JPEG data continues ...
};
```

The array contains actual JPEG file data - those bytes could be saved as a `.jpg` file and would be a valid image. The C array format allows you to embed the image directly in your program memory (`PROGMEM`) instead of requiring a file system.

### Examples

```bash
# Convert PNG to 240x320 JPEG at 75% quality
python3 image_to_c-array.py logo.png

# High quality 320x240 landscape image
python3 image_to_c-array.py photo.jpg landscape.h 320 240 90

# Small, lower quality image for memory-constrained projects
python3 image_to_c-array.py icon.png icon.h 64 64 60

# Mirror a webcam image horizontally
python3 image_to_c-array.py webcam.jpg webcam.h 240 320 75 --flip-h
```

### Notes

- Input images are automatically converted to RGB mode if needed
- High-quality Lanczos resampling is used for resizing
- JPEG subsampling is set to 4:2:0 for better compression
- The `PROGMEM` attribute stores data in flash memory instead of RAM on ESP32/Arduino
