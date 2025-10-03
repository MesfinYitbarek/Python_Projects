import os

file_path = "test.txt"

if os.path.exists(file_path): #os.path.isfile(file_path), os.path.isdir(file_path)
    print(f"Location: {file_path}")
else:
    print("Location not found")