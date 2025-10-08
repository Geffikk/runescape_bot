input_file = "/data/pos.txt"
output_file = "/data/pos.txt"

with open(input_file, "r") as infile, open(output_file, "w") as outfile:
    for line in infile:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        image_name = parts[0]
        new_line = f"positive/{line}\n"
        outfile.write(new_line)