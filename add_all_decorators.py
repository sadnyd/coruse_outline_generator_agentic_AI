#!/usr/bin/env python3
"""
Script to add @function_logger decorators to ALL functions in the codebase.
Run once to instrument entire codebase for comprehensive flow logging.
"""

import os
import re
from pathlib import Path

# Files and specific functions to skip (already decorated or special cases)
SKIP_FILES = {
    'utils/flow_logger.py',  # Already the logger itself
    '__pycache__',
    '.git',
    'logs',
    '__init__.py',
    'conftest.py',
}

SKIP_PATTERNS = [
    r'.*test.*\.py',  # Skip test files
    r'.*demo.*\.py',
    r'.*__.*__\.py',
]

DEFAULT_PURPOSES = {
    '__init__': 'Initialize instance',
    'get_': 'Get ',
    'set_': 'Set ',
    'add_': 'Add ',
    'remove_': 'Remove ',
    'delete_': 'Delete ',
    'create_': 'Create ',
    'update_': 'Update ',
    'list_': 'List ',
    'search_': 'Search for ',
    '_check': 'Check ',
    '_validate': 'Validate ',
    '_build': 'Build ',
    'run': 'Execute ',
}

def should_skip_file(file_path):
    """Check if file should be skipped."""
    for skip in SKIP_FILES:
        if skip in file_path.lower():
            return True
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, file_path.lower()):
            return True
    return False

def get_logger_purpose(func_name):
    """Generate a reasonable purpose for a function."""
    if func_name.startswith('__') and func_name.endswith('__'):
        return f'Handle {func_name}'
    
    for prefix, desc in DEFAULT_PURPOSES.items():
        if func_name.startswith(prefix):
            remaining = func_name[len(prefix):]
            # Convert snake_case to space-separated
            remaining_text = re.sub(r'_', ' ', remaining)
            return desc + remaining_text
    
    # Default: human-readable conversion
    converted = re.sub(r'_', ' ', func_name)
    return f'Execute {converted}'

def extract_function_signature(line, full_content, line_num):
    """Extract function definition line(s) and check if already decorated."""
    # Check if previous non-empty line has @function_logger
    prev_line_idx = line_num - 2
    while prev_line_idx >= 0:
        prev_line = full_content[prev_line_idx].strip()
        if prev_line and not prev_line.startswith('#'):
            if '@function_logger' in prev_line:
                return None, None  # Already decorated
            break
        prev_line_idx -= 1
    
    # Extract function name
    match = re.match(r'^\s*(@\w+\s)*def\s+(\w+)\s*\(', line)
    if not match:
        return None, None
    
    func_name = match.group(2)
    indent = len(line) - len(line.lstrip())
    
    return func_name, indent

def add_decorators_to_file(file_path):
    """Add @function_logger decorators to all functions in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        print(f"  ✗ Cannot read {file_path}")
        return False
    
    # Check if already has import
    has_import = any('from utils.flow_logger import function_logger' in line for line in lines)
    
    modified = False
    new_lines = []
    i = 0
    
    # Add import if needed
    if not has_import:
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith('import') or line.startswith('from'):
                continue
            elif not line.strip().startswith('#') and not line.strip() == '':
                # Found first non-import line, insert before it
                if 'from utils.flow_logger import function_logger' not in ''.join(lines[:i]):
                    lines.insert(i, 'from utils.flow_logger import function_logger\n')
                    new_lines = lines
                    modified = True
                    inserted = True
                break
        
        if not inserted and has_import == False:
            # No imports found, add after docstring
            for i, line in enumerate(lines):
                if '"""' in line and i > 0:
                    # Found docstring end, insert after
                    lines.insert(i + 1, '\nfrom utils.flow_logger import function_logger\n')
                    new_lines = lines
                    modified = True
                    break
    
    if not new_lines:
        new_lines = lines
    
    # Add decorators to functions
    final_lines = []
    i = 0
    while i < len(new_lines):
        line = new_lines[i]
        
        # Check for function definition
        if re.match(r'^\s*def\s+\w+\s*\(', line):
            func_name, indent = extract_function_signature(line, new_lines, i)
            
            if func_name:  # Not already decorated
                purpose = get_logger_purpose(func_name)
                indent_str = ' ' * indent
                decorator_line = f"{indent_str}@function_logger(\"{purpose}\")\n"
                final_lines.append(decorator_line)
                modified = True
        
        final_lines.append(line)
        i += 1
    
    # Write back if modified
    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(final_lines)
            return True
        except:
            print(f"  ✗ Cannot write {file_path}")
            return False
    
    return False

def main():
    """Add decorators to all Python files."""
    print("🔍 Scanning for Python files to instrument...\n")
    
    root_dir = Path(__file__).parent
    python_files = list(root_dir.rglob('*.py'))
    
    decorated_count = 0
    total_count = 0
    
    # Organize by directory
    files_by_dir = {}
    for py_file in python_files:
        if should_skip_file(str(py_file)):
            continue
        
        dir_name = py_file.parent.name or 'root'
        if dir_name not in files_by_dir:
            files_by_dir[dir_name] = []
        files_by_dir[dir_name].append(py_file)
    
    # Process by directory
    priority_dirs = ['agents', 'services', 'utils', 'tools', 'schemas', 'vectorstore']
    
    for dir_priority in priority_dirs:
        if dir_priority in files_by_dir:
            print(f"\n📁 {dir_priority.upper()}")
            for py_file in sorted(files_by_dir[dir_priority]):
                total_count += 1
                rel_path = py_file.relative_to(root_dir)
                if add_decorators_to_file(str(py_file)):
                    decorated_count += 1
                    print(f"  ✓ {rel_path}")
                else:
                    print(f"  · {rel_path}")
    
    # Process remaining
    print(f"\n📁 OTHER")
    for dir_name, files in sorted(files_by_dir.items()):
        if dir_name not in priority_dirs:
            for py_file in sorted(files):
                total_count += 1
                rel_path = py_file.relative_to(root_dir)
                if add_decorators_to_file(str(py_file)):
                    decorated_count += 1
                    print(f"  ✓ {rel_path}")
                else:
                    print(f"  · {rel_path}")
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETE: {decorated_count}/{total_count} files modified")
    print(f"{'='*60}")
    print(f"\n📊 Summary:")
    print(f"  • Total Python files: {len(python_files)}")
    print(f"  • Files processed: {total_count}")
    print(f"  • Files modified: {decorated_count}")
    print(f"  • Files skipped: {len(python_files) - total_count}")
    print(f"\n✨ All functions are now logged! Start the app to see flow logs.")
    print(f"📂 View logs at: logs/flow.log")

if __name__ == '__main__':
    main()
