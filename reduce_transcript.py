import re

file_path = "/Users/easonyin/Downloads/Is Artificial Intelligence more beneficial than harmful to human beings?.md"

with open(file_path, 'r') as f:
    content = f.read()

# Remove Facts sections
# Matches **IV. Facts** followed by any text until **V. Impact Calculus**
content = re.sub(r'\*\*IV\. Facts\*\*.*?(?=\*\*V\. Impact Calculus\*\*)', '', content, flags=re.DOTALL)

# Remove References sections
# Matches **VII. References** followed by any text until the next header (### or #)
# We need to be careful not to consume the next header.
# The references seem to be at the end of the speeches.
# The next section usually starts with "###" (e.g. ### Negative Argument) or "# Round" or "# Affirmative Final Summary"
# Or just end of file.

# Let's try to match **VII. References** until the next double newline followed by a header-like pattern or end of string.
# Actually, looking at the file, References are bullet points.
# I will just remove the specific block.

content = re.sub(r'\*\*VII\. References\*\*.*?(?=(#|###|\Z))', '', content, flags=re.DOTALL)

# Clean up extra newlines created by removals
content = re.sub(r'\n{3,}', '\n\n', content)

with open(file_path, 'w') as f:
    f.write(content)

print(f"Reduced content length: {len(content)}")
