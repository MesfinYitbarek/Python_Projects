#.text
text_data = "I like chicken"
file_path = "output.txt"
with open(file_path, "w") as file: #w - override the file..x - create new file, a --append 
    file.write(text_data)
    print(f"text file '{file_path}' was created")