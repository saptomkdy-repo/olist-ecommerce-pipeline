import os

# Walk through the current directory and print the tree structure
for root, dirs, files in os.walk('.'):
    # Skip hidden folders
    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', '.venv']]
    level = root.replace('.', '').count(os.sep)
    indent = ' ' * 4 * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = ' ' * 4 * (level + 1)
    for file in files:
        print(f'{subindent}{file}')

# or use git bash:
# find . -not -path '*/\.*' -not -path '*/node_modules/*' | head -100