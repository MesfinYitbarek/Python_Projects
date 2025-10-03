import csv
employee = [ ["name", age, "job"],
             ["mepa", 23, "SoftEng"]
            ["kira", 24, "SoftEng"]]

file_path = "output.json"
try:
    with open(file_path, "w") as file:
        writer = csv.writer( file)
        for row in employee:
            writer.writerow()
        print(f"csv file '{file_path}' was created")
except FileExistsError:
    print("This file already exists")