with open('README.md', 'r', encoding='utf-16') as f:
    text = f.read()
    print(text)
    
with open('README.md', 'w', encoding='utf-8') as f:
    f.write(text)
