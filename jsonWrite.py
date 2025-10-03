#json
import json
employee = {
    "name": "mepa",
    "age": 23,
    "job": "cook"
}

file_path = "output.json"
try:
    with open(file_path, "w") as file:
        json.dump(employee, file, indent=4)
        print(f"json file '{file_path}' was created")
except FileExistsError:
    print("This file already exists")