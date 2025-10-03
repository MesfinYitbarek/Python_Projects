# csv
import csv
file_path = "output.txt"
with open(file_path, "r") as file:
    content = csv.reader(file)
    for line in content:
        print(line)
