#!/usr/bin/env python3
"""Fix formatting issues in route files caused by line concatenation during file creation"""
import re

files_to_fix = [
    'app/routes/courses.py',
    'app/routes/users.py',
    'app/routes/attendance.py',
    'app/routes/reports.py',
]

def fix_file(filepath):
    print(f"Fixing {filepath}...")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix pattern: )    elif -> )\n    elif
    content = re.sub(r'\)    (elif|else)', r')\n    \1', content)
    
    # Fix pattern: )    query -> )\n    query  
    content = re.sub(r'\)    (\w)', r')\n    \1', content)
    
    # Fix pattern: required_fields:        if -> required_fields:\n        if
    content = re.sub(r'(:\s+)(\s{4,})(if|for|while|def|class)', r':\n    \3', content)
    
    # Fix pattern where 4+ spaces should be newline + proper indent
    content = re.sub(r'([a-z_])        ([a-z_])', r'\1\n        \2', content)
    
    # Fix: "token)        return" -> "token)\n        return"
    content = re.sub(r'\)        (return|if|for)', r')\n        \1', content)
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✓ Fixed {filepath}")

if __name__ == '__main__':
    for file in files_to_fix:
        try:
            fix_file(file)
        except Exception as e:
            print(f"Error fixing {file}: {e}")