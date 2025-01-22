# 第 113 页处理结果

## 使用的提示
```

```

## 处理结果
Here's a Python function that builds basic blocks from a sequence of three-address instructions:

```python
def build_basic_blocks(instructions):
    leaders = set()
    basic_blocks = []

    # Step 1: Determine the leaders
    for i, instr in enumerate(instructions):
        if i == 0 or instr.is_jump_target or (i > 0 and instructions[i-1].is_jump):
            leaders.add(i)

    # Step 2: Build basic blocks
    current_block = []
    for i, instr in enumerate(instructions):
        current_block.append(instr)
        if i+1 in leaders or i == len(instructions) - 1:
            basic_blocks.append(current_block)
            current_block = []

    return basic_blocks
```

Explanation:

1. We initialize an empty set `leaders` to store the indices of leader instructions and an empty list `basic_blocks` to store the resulting basic blocks.

2. In step 1, we iterate over the instructions and determine the leaders:
   - The first instruction (index 0) is always a leader.
   - Any instruction that is a jump target (`instr.is_jump_target`) is a leader.
   - Any instruction that immediately follows a jump instruction (`instructions[i-1].is_jump`) is a leader.

3. In step 2, we build the basic blocks:
   - We iterate over the instructions again and append each instruction to the `current_block` list.
   - If the next instruction is a leader (its index is in the `leaders` set) or we have reached the last instruction, we append the `current_block` to the `basic_blocks` list and start a new empty `current_block`.

4. Finally, we return the list of basic blocks.

Note: This implementation assumes that the instructions are represented as objects with `is_jump_target` and `is_jump` attributes indicating whether an instruction is a jump target or a jump instruction, respectively.

You can call this function with your sequence of three-address instructions to obtain the list of basic blocks.
