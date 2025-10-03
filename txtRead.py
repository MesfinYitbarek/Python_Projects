
#.txt
file_path = "output.txt"
with open(file_path, "r") as file: #w - override the file..x - create new file, a --append 
    content = file.read()
    print(content)