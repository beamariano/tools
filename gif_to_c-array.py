import sys
import os


def convert_gif(input_file, output_file="gifData.h"):
    if not os.path.exists(input_file):
        print(f"Error: '{input_file}' not found!")
        return

    with open(input_file, "rb") as f:
        data = f.read()

    with open(output_file, "w") as out:
        out.write("#ifndef GIFDATA_H\n#define GIFDATA_H\n\n")
        out.write(f"const unsigned int gifDataSize = {len(data)};\n\n")
        out.write("const unsigned char gifData[] PROGMEM = {\n  ")
        out.write(", ".join(f"0x{b:02X}" for b in data))
        out.write("\n};\n\n#endif\n")

    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Size:   {len(data)} bytes ({len(data) / 1024:.1f} KB)")

    if len(data) > 1400 * 1024:
        print("WARNING: File is over 1400KB - may be too large for ESP32 flash!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gif_to_c-array.py your_gif.gif")
    else:
        convert_gif(sys.argv[1])
