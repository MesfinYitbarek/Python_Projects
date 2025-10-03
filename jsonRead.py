import json
#json
file_path = "output.txt"
with open(file_path, "r") as file: 
    content = json.load(file)
    print(content)