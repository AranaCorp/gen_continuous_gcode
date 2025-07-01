#!/usr/bin/env python3

import os
import sys


def process_gcode(file_path, iterations, low_temp=40):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    start_index = None
    end_index = None

    # Detect the start and end lines
    for i, line in enumerate(lines):
        if ";Generated with Cura_SteamEngine 5.10.0" in line: # or "G28 ;Home" in line:
            start_index = i
        if "G1 X0 Y300 ;Present print" in line: #if ";End of Gcode" in line:
            end_index = i-1
            break

    if start_index is None or end_index is None:
        print("Start or end of G-code not found.")
        return

    header = lines[:start_index]
    body = lines[start_index:end_index + 1]  # Include end line for completeness
    footer = lines[end_index + 1:]

    # Define the ejection sequence
    ejection_sequence = [
        f"M140 S{low_temp} ; Set bed temp to low\n",
        "G1 Z10 F1000 ; Lift head\n",
        "G1 X0 Y300 F3000 ; Move to min X, max Y (adjust if needed)\n",
        "G28 Z ; Home Z axis\n",
        f"M190 S{low_temp} ; Wait for bed temp\n",
        "G1 Y0 F500 ; Slide part off slowly\n",
        "G4 P1000 ; Wait a second\n"
    ]

    # Generate new filename
    base_name, ext = os.path.splitext(file_path)
    new_filename = f"{base_name}x{iterations}c{ext}"

    with open(new_filename, 'w') as output:
        output.writelines(header)
        for i in range(iterations):
            output.write(f";-- Iteration {i + 1} --\n")
            output.writelines(body)
            output.writelines(ejection_sequence)
        output.writelines(footer)

    print(f"✅ New G-code written to: {new_filename}")

# Example usage:
# process_gcode("your_part.gcode", 5)

def main():
    if len(sys.argv) < 3:
        print("Usage: python gen_continuous_gcode.py <input_file.gcode> <iterations>")
        return

    file_path = sys.argv[1]
    try:
        iterations = int(sys.argv[2])
    except ValueError:
        print("Iterations must be an integer.")
        return

    process_gcode(file_path, iterations)

if __name__ == "__main__":
    main()
