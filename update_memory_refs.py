#!/usr/bin/env python3
import sys

with open('/data/workspace/MEMORY.md', 'r') as f:
    lines = f.readlines()

# Find SOP References section
ref_start = -1
for i, line in enumerate(lines):
    if line.strip() == '## SOP References':
        ref_start = i
        break

if ref_start == -1:
    print('SOP References section not found')
    sys.exit(1)

# Find the line after the list (next ## header)
ref_end = -1
for i in range(ref_start + 1, len(lines)):
    if lines[i].startswith('## '):
        ref_end = i
        break

if ref_end == -1:
    ref_end = len(lines)

# Build new lines
new_lines = []
i = ref_start
while i < ref_end:
    line = lines[i]
    if line.strip() == '- SOP 3: Printing orders protocol (Trâm Anh + Google Sheets)':
        new_lines.append(line)
        # Add SOP 4 after SOP 3
        new_lines.append('- SOP 4: Task Creation (@task trigger) - see SOP.md for details\n')
        i += 1
    else:
        new_lines.append(line)
        i += 1

# Replace the section
result = lines[:ref_start] + new_lines + lines[ref_end:]

with open('/data/workspace/MEMORY.md', 'w') as f:
    f.writelines(result)

print('Updated SOP References in MEMORY.md')