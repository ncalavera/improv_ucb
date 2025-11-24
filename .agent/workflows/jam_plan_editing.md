---
description: Jam Plan Editing and Reorganization Flow. Use when modifying existing jam plan markdown files (reorganizing blocks, updating timing, fixing content).
---

# Jam Plan Editing and Reorganization Flow

This workflow guides the AI agent through editing and reorganizing existing jam plan markdown files.

## When to Use

- Reorganize blocks in a jam plan (change order, renumber)
- Update timing for blocks
- Fix content errors or formatting issues
- Merge or split blocks
- Add or remove exercises from blocks

## Process

### Step 1: Load and Analyze Current Plan

1. **Locate jam plan file**: Usually in `output/jam_plans/session_X_jam_plan_ru.md`
2. **Read the file**: Load the full markdown content
3. **Identify structure**: 
   - Find intro section (before first block)
   - Find all blocks (using pattern `## Блок \d+:` or `## Block \d+:`)
   - Find outro section (after last block, usually "Заключительные заметки" or "Final Notes")

### Step 2: Understand Current Structure

1. **Parse blocks**: Extract each block with its header and content
2. **Identify block boundaries**: Use regex pattern to find exact boundaries
   - Pattern: `r'(## Блок \d+:.*?)(?=## Блок \d+:|## Заключительные заметки|$)'`
3. **Extract metadata**: Note timing, exercise names, concepts for each block

### Step 3: Plan Changes

1. **Determine desired changes**:
   - Block reordering (e.g., Block 2 → Block 4)
   - Timing updates (e.g., 15 minutes → 40 minutes)
   - Content modifications
   - Block merging/splitting

2. **Create transformation plan**: Document what needs to change

### Step 4: Apply Changes

**Use Python to modify the markdown file directly:**

```python
import re
from pathlib import Path

def reorganize_blocks(input_file: str, block_mapping: dict, timing_updates: dict = None):
    """
    Reorganize blocks in a jam plan markdown file.
    
    Args:
        input_file: Path to jam plan markdown file
        block_mapping: Dict mapping old_block_num -> new_block_num
        timing_updates: Dict mapping block_num -> new_timing_string
    """
    input_path = Path(input_file)
    
    # Read content
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all blocks
    block_pattern = r'(## Блок \d+:.*?)(?=## Блок \d+:|## Заключительные заметки|$)'
    blocks = re.findall(block_pattern, content, re.DOTALL)
    
    # Find intro and outro
    intro_match = re.search(r'(.*?)(?=## Блок 1:)', content, re.DOTALL)
    intro = intro_match.group(1) if intro_match else ""
    
    outro_match = re.search(r'(## Заключительные заметки.*)', content, re.DOTALL)
    outro = outro_match.group(1) if outro_match else ""
    
    # Reorganize blocks according to mapping
    reorganized_blocks = [None] * len(blocks)
    for old_idx, block in enumerate(blocks):
        old_num = old_idx + 1
        if old_num in block_mapping:
            new_num = block_mapping[old_num]
            # Update block number in header
            new_block = re.sub(
                rf'## Блок {old_num}:',
                f'## Блок {new_num}:',
                block,
                count=1
            )
            # Update timing if specified
            if timing_updates and new_num in timing_updates:
                new_timing = timing_updates[new_num]
                new_block = re.sub(
                    r'\(\d+ минут\)',
                    f'({new_timing} минут)',
                    new_block,
                    count=1
                )
            reorganized_blocks[new_num - 1] = new_block
    
    # Reconstruct content
    new_content = intro + ''.join(reorganized_blocks) + outro
    
    # Write back
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Successfully reorganized blocks in {input_file}")

# Example usage:
reorganize_blocks(
    input_file="output/jam_plans/session_3_jam_plan_ru.md",
    block_mapping={
        1: 1,  # Keep Block 1 as Block 1
        2: 4,  # Move Block 2 to Block 4
        3: 2,  # Move Block 3 to Block 2
        4: 3,  # Move Block 4 to Block 3
    },
    timing_updates={
        3: 40,  # Block 3 now 40 minutes
        4: 70,  # Block 4 now 70 minutes
    }
)
```

### Step 5: Manual Content Edits

For content changes (not just reorganization):

1. **Read the file**: Load into memory
2. **Make targeted edits**: Use string replacement or regex
3. **Preserve structure**: Maintain markdown formatting
4. **Write back**: Save the modified content

**Example: Update exercise instructions**

```python
from pathlib import Path

def update_exercise_content(input_file: str, exercise_name: str, new_content: str):
    """Update content of a specific exercise in a jam plan."""
    input_path = Path(input_file)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find exercise section and replace
    pattern = rf'(### Упражнение: {re.escape(exercise_name)}.*?)(?=###|##|$)'
    replacement = f'### Упражнение: {exercise_name}\n\n{new_content}\n\n'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated exercise: {exercise_name}")
```

### Step 6: Verify Changes

1. **Read modified file**: Confirm changes are correct
2. **Check block numbering**: Ensure sequential numbering (1, 2, 3, 4...)
3. **Check timing**: Verify timing updates are applied
4. **Check formatting**: Ensure markdown structure is preserved

### Step 7: Regenerate PDF (Optional)

If PDF needs to be updated:

1. Use the [PDF Generation Flow](./pdf_generation.md) to regenerate
2. New version will be created automatically (v002, v003, etc.)

## Common Operations

### Reorder Blocks

**Scenario**: Move Block 2 to position 4, Block 3 to position 2, Block 4 to position 3

```python
reorganize_blocks(
    input_file="output/jam_plans/session_3_jam_plan_ru.md",
    block_mapping={1: 1, 2: 4, 3: 2, 4: 3}
)
```

### Update Block Timing

**Scenario**: Change Block 3 from 15 minutes to 40 minutes

```python
# Read file
with open("output/jam_plans/session_3_jam_plan_ru.md", 'r', encoding='utf-8') as f:
    content = f.read()

# Update timing
content = re.sub(
    r'## Блок 3:.*?\(15 минут\)',
    lambda m: m.group(0).replace('(15 минут)', '(40 минут)'),
    content,
    flags=re.DOTALL
)

# Write back
with open("output/jam_plans/session_3_jam_plan_ru.md", 'w', encoding='utf-8') as f:
    f.write(content)
```

### Fix Content Errors

**Scenario**: Fix typo or incorrect exercise name

```python
# Simple find and replace
content = content.replace("старое название", "новое название")
```

## Best Practices

1. **Always backup**: Create a copy before making major changes
2. **Test regex patterns**: Verify patterns match correctly before applying
3. **Preserve formatting**: Maintain markdown structure and spacing
4. **Verify after changes**: Read the file back to confirm changes
5. **Use version control**: Commit changes to git for safety

## Integration with Other Workflows

- **After Jam Plan Generation**: Use this flow to refine generated plans
- **Before PDF Generation**: Edit plans before generating final PDF
- **Iterative Refinement**: Make multiple passes to perfect the plan

