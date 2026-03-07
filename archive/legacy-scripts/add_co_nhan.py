#!/usr/bin/env python3
import sys

with open('/data/workspace/MEMORY.md', 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # Insert after the line about Allowlisted (Telegram)
    if line.strip() == "- **Allowlisted (Telegram):** Chi Phan (82510296), Hanh Bui (1034926814)":
        new_lines.append("- **Cô Nhàn:** Telegram 158396493 — When answering her questions, always reply in detail and use web search.\n")
    # Also add a communication guidelines section after Contacts but before Who I am
    # We'll handle that separately

# Now ensure there's a communication note
# Find the line with "---" after Contacts
for i in range(len(new_lines)):
    if new_lines[i].strip() == "---" and i > 0 and "Contacts / Relationships" in new_lines[i-2]:
        # Insert a note before the separator
        new_lines.insert(i, "\n**Communication Guidelines:**\n- For Cô Nhàn (158396493): Always provide detailed answers with web search.\n")
        break

with open('/data/workspace/MEMORY.md', 'w') as f:
    f.writelines(new_lines)

print('Updated MEMORY.md with Cô Nhàn note')