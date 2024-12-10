import numpy as np
import os
import json

TYPE_LOOKUP = {
    0: 'Wall',
    1: 'Empty',
    2: 'Target',
    3: 'Box on Target',
    4: 'Box',
    5: 'player'
}

def format_response(state, action):
    h, w = state.shape

    player_position = np.where(state == 5)
    player_x = player_position[0][0]
    player_y = player_position[1][0]
    out_of_place_box = np.where(state == 4)
    empty_target_position = np.where(state == 2)

    def description(x, y, w, h, state):
        if x < 0 or x >= w or y < 0 or y >= h:
            return 'Wall'
        return TYPE_LOOKUP[state[x, y]]
    
    def state_predict(one_step, two_step):
        if one_step in ['Empty', 'Target']:
            return 'move to an empty space'
        if one_step in ['Box on Target', 'Box']:
            if two_step in ['Empty', 'Target']:
                return 'push the box along that direction'
            if two_step in ['Wall', 'Box', 'Box on Target']:
                return 'get blocked by a box'
        if one_step == 'Wall':
            return 'get blocked by a wall'
        return
    
    def get_action(action):
        if 'down' in action:
            return 'down'
        if 'up' in action:
            return 'up'
        if 'left' in action:
            return 'left'
        return 'right'
    
    left = description(player_x, player_y-1, w, h, state)
    right = description(player_x, player_y+1, w, h, state)
    top = description(player_x-1, player_y, w, h, state)
    bottom = description(player_x+1, player_y, w, h, state)

    left_left = description(player_x, player_y-2, w, h, state)
    right_right = description(player_x, player_y+2, w, h, state)
    top_top = description(player_x-2, player_y, w, h, state)
    bottom_bottom = description(player_x+2, player_y, w, h, state)
    top_left = description(player_x-1, player_y-1, w, h, state)
    top_right = description(player_x-1, player_y+1, w, h, state)
    bottom_left = description(player_x+1, player_y-1, w, h, state)
    bottom_right = description(player_x+1, player_y+1, w, h, state)

    move_left = state_predict(left, left_left)
    move_right = state_predict(right, right_right)
    move_top = state_predict(top, top_top)
    move_down = state_predict(bottom, bottom_bottom)

    nextAction = get_action(action)
    return [player_position, out_of_place_box, empty_target_position, left, right, top, bottom, left_left, right_right, top_top, bottom_bottom, top_left, top_right, bottom_left, bottom_right, move_left, move_right, move_top, move_down, nextAction]

def fill_template(lst):
    player_position, out_of_place_box, empty_target_position, left, right, top, bottom, left_left, right_right, top_top, bottom_bottom, top_left, top_right, bottom_left, bottom_right, move_left, move_right, move_top, move_down, nextAction = lst
    player_position = f"({player_position[0][0]}, {player_position[1][0]})"
    if len(out_of_place_box[0]) != 0:
        out_of_place_box = ", ".join(f"({x}, {y})" for x, y in zip(*out_of_place_box))
    else:
        out_of_place_box = ""

    if len(empty_target_position[0]) != 0:
        empty_target_position = ", ".join(f"({x}, {y})" for x, y in zip(*empty_target_position))
    else:
        empty_target_position = ""

    output = f"""
    (for all coordinates, x-axis is counted from left to right, y-axis is counted from top to bottom, starting from (0,0)) \n

    From the image, we can summarize the following information:
    Player Position: {{{player_position}}}
    Remaining out of place Box Position: {{{out_of_place_box}}}
    Remaining Empty Target Position: {{{empty_target_position}}}
    Objects on the 4 directions are: 
    Left: {{{left}}}
    Right: {{{right}}}
    Top: {{{top}}}
    Bottom: {{{bottom}}}
    Objects on positions that are 2 cells away: 
    Left-Left: {{{left_left}}}
    Right-Right: {{{right_right}}}
    Top-Top: {{{top_top}}}
    Bottom-Bottom: {{{bottom_bottom}}}
    Top-Left: {{{top_left}}}
    Top-Right: {{{top_right}}}
    Bottom-Left: {{{bottom_left}}}
    Bottom-Right: {{{bottom_right}}}

    Based on the current state, this is what would happen if I try to move on the 4 directions:
    Left: {{{move_left}}}
    Right: {{{move_right}}}
    Top: {{{move_top}}}
    Bottom: {{{move_down}}}

    Considering the current situation, my next move would be {{{nextAction}}}
    MOVE: {{{nextAction}}}
    """
    return output

def to_json(id, figures, Meta_Prompt, output):
    return {
    "id": str(id),
    "image": f"{figures}",
    "conversations": [
        {
            "from": "human",
            "value": f"{Meta_Prompt}"
        },
        {
            "from": "human",
            "value": "This is the current state: <image>"
        },
        {
            "from": "gpt",
            "value": f"{output}"
        }
    ]
    }

base_dir = os.path.dirname(__file__)
meta_prompt_v1_path = os.path.join(base_dir, 'sokoban-meta-v0.md')
Meta_Prompt = open(meta_prompt_v1_path, 'r').read()

data = np.load('sokoban_data/data.npz', allow_pickle=True)

for key in data:
    value = data[key].item()
    states = value['states']
    actions = value['actions']
    n = value['num_attempts']
    figures = value['figures']

    for i in range(n):
        output = format_response(states[i], actions[i])
        output = fill_template(output)
        output = to_json(key.split('_')[-1], figures, Meta_Prompt, output)
        json_string = json.dumps(output, indent=2)

        # Write this dictionary to a text file as JSON
        with open("output.txt", "w") as f:
            json.dump(json_string, f, indent=2)
