file_path = "/Users/easonyin/Downloads/Is Artificial Intelligence more beneficial than harmful to human beings?.md"

with open(file_path, 'r') as f:
    content = f.read()

new_content = "**Flair: Discussion**\n\n" + content

with open(file_path, 'w') as f:
    f.write(new_content)
