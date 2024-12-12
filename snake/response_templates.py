from curses import meta
import os
import numpy as np
from pathlib import Path

base_dir = os.path.dirname(__file__)

def description(x, y, w, h, grid):
        if x < 0 or x == w or y < 0 or y == h:
            return 'at_edge'
        return grid[x][y]

def get_tail(grid, head_idx):
    has_neighbor = True
    x, y = head_idx
    w = len(grid)
    h = len(grid[0])
    while has_neighbor:
        if description(x, y-1, w, h, grid) == '>': # left
            y -= 1
        elif description(x, y+1, w, h, grid) == '<': # right
            y += 1
        elif description(x+1, y, w, h, grid) == '/': # bottom
            x += 1
        elif description(x-1, y, w, h, grid) == '\\': # top
            x -= 1
        else:
            has_neighbor=False
    return (x, y)

def get_food2snake(food, head):
    food_x, food_y = food
    head_x, head_y = head
    vertical = ''
    horizon = ''
    if food_x < head_x:
        vertical = 'top'
    elif food_x > head_x:
        vertical = 'bottom'
    else:
        vertical = 'mid'
    

    if food_y < head_y:
        horizon = 'left'
    elif food_y > head_y:
        horizon = 'right'
    else:
        horizon = 'mid'
    return vertical + '-' + horizon

def get_surrounding(grid, head):
    converter = {
        '<': 'snake body',
        '>': 'snake body',
        '/': 'snake body',
        '\\': 'snake body',
        'x': 'empty',
        'at_edge': 'boundary', 
        'o': 'food'
    }
    x, y = head
    w = len(grid)
    h = len(grid[0])
    left = converter[description(x, y-1, w, h, grid)]
    right = converter[description(x, y+1, w, h, grid)]
    top = converter[description(x-1, y, w, h, grid)]
    down = converter[description(x+1, y, w, h, grid)]
    
    return left, right, top, down

def process_file(file_path, last_length, last_move, move, isFirst, version='v0'):

    with open(file_path, 'r') as file:
        grid = ''
        length = 0
        head = None
        food = None
        grid_array = []
        target_characters = ['<', '>', '\\', '/', 'H']

        for line_idx, line in enumerate(file):
            grid_array.append(line.strip())
            for char_idx, char in enumerate(line):
                if char != '\n':
                    grid += f' {char}'
                else:
                    grid += '\n'
                if char == 'H':  # Check if the character is 'H'
                    head = (line_idx, char_idx)
                if char == 'o':
                    food = (line_idx, char_idx)
                if char in target_characters:
                    length += 1

        eaten = 'no' if isFirst or length == last_length else 'yes'

        tail = get_tail(grid_array, head)

        food2snake = get_food2snake(food, head)
        left, right, top, bottom = get_surrounding(grid_array, head)
        if version=='v2':
            grid = grid.replace('x', '.')

    return [grid, last_move.lower(), eaten, length, head, tail, food, food2snake, left, right, top, bottom, move.lower()]

def fill_template_v0(result):
    grid, last_move, eaten, length, head, tail, food, food2snake, left, right, top, bottom, move = result
    output = template_v0.format(
        grid = grid, 
        last_move = last_move, 
        eaten = eaten, 
        length = length, 
        head = head, 
        tail = tail, 
        food = food, 
        food2head = food2snake, 
        left = left, 
        right = right, 
        top = top, 
        bottom = bottom, 
        move = move
    )
    return output.strip()

meta_prompt_v0_path = os.path.join(base_dir, 'snake-meta-v0.md')
meta_prompt_v0 = open(meta_prompt_v0_path, 'r').read()
template_v0 = """
From the screenshot and the grid before move, we can derive the current grid:
{grid}

From the current grid, we can summarize the following information:
Last move: {last_move}
Eaten food in last move: {eaten}
Current snake length: {length}
Snake head position: {head}
Snake tail position: {tail}
Food position: {food}
Direction of the food relative to the snake head: {food2head}
The 4 adjacent grids to the snake head are: 
Left: {left}
Right: {right}
Top: {top}
Bottom: {bottom}

Considering the current situation, my next move would be "{move}".
MOVE: {move}
"""

meta_prompt_v1_path = os.path.join(base_dir, 'snake-meta-v1.md')
meta_prompt_v1 = open(meta_prompt_v1_path, 'r').read()
meta_prompt_beta_path = os.path.join(base_dir, 'snake-meta-beta.md')
meta_prompt_beta = open(meta_prompt_beta_path, 'r').read()
meta_prompt_v2_path = os.path.join(base_dir, 'snake-meta-v2.md')
meta_prompt_v2 = open(meta_prompt_v2_path, 'r').read()