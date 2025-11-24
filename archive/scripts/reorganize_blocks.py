#!/usr/bin/env python3
"""
Reorganize blocks in session_3_jam_plan_ru.md using regex to find exact block boundaries
"""
import re

def main():
    input_file = "output/jam_plans/session_3_jam_plan_ru.md"
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find block boundaries using regex
    block_pattern = r'(## Блок \d+:.*?)(?=## Блок \d+:|## Заключительные заметки|$)'
    blocks = re.findall(block_pattern, content, re.DOTALL)
    
    # Find intro (everything before Block 1)
    intro_match = re.search(r'(.*?)(?=## Блок 1:)', content, re.DOTALL)
    intro = intro_match.group(1) if intro_match else ""
    
    # Find outro (everything after last block)
    outro_match = re.search(r'(## Заключительные заметки.*)', content, re.DOTALL)
    outro = outro_match.group(1) if outro_match else ""
    
    print(f"Found {len(blocks)} blocks")
    for i, block in enumerate(blocks):
        header = block.split('\n')[0]
        print(f"Block {i}: {header[:60]}...")
    
    if len(blocks) != 4:
        print(f"Error: Expected 4 blocks, found {len(blocks)}")
        return
    
    # Identify blocks by their content
    block_1 = blocks[0]  # Yes And / Platform
    block_2_old = blocks[1]  # PFD (will become Block 4)
    block_3_old = blocks[2]  # Listening (will become Block 2)
    block_4_old = blocks[3]  # Denial (will become Block 3)
    
    # Renumber and reorganize
    block_1_new = block_1  # Keep as is
    block_2_new = re.sub(r'## Блок 3:', '## Блок 2:', block_3_old, count=1)  # Listening
    block_3_new = re.sub(r'## Блок 4:', '## Блок 3:', block_4_old, count=1)  # Denial  
    block_4_new = re.sub(r'## Блок 2:', '## Блок 4:', block_2_old, count=1)  # PFD
    
    # Update timing for Block 3 (Denial) - increase from 15 to 40 min
    block_3_new = re.sub(r'\(15 минут\)', '(40 минут)', block_3_new, count=1)
    
    # Update timing for Block 4 (PFD) - increase from 45 to 70 min (will add Give the Setup)
    block_4_new = re.sub(r'\(45 минут\)', '(70 минут)', block_4_new, count=1)
    
    # Reconstruct file
    new_content = intro + block_1_new + block_2_new + block_3_new + block_4_new + outro
    
    # Write back
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✓ Successfully reorganized blocks")
    print("New order:")
    print("  Block 1: Yes And / Platform (30 min)")
    print("  Block 2: Listening and Focus (35 min)")  
    print("  Block 3: Avoiding Denial (40 min)")
    print("  Block 4: PFD + Commitment (70 min)")

if __name__ == "__main__":
    main()
