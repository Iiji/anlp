import numpy as np
import os
import json
import argparse
from tqdm import tqdm
from pathlib import Path
from response_templates import fill_template_v0, meta_prompt_v0, process_file

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data_path",
        type=str,
        default='data/trajectories/snake/test',
        help="json file with image paths and annotations",
    )
    parser.add_argument(
        "--max_trajs",
        type=int,
        default=-1,
        help="max number of trajectories to use",
    )
    parser.add_argument(
        "--response_template",
        type=str,
        default='v0',
    )

    args = parser.parse_args()
    return args

def to_json(id, figures, meta_prompt, grid):
    return {
    "id": str(id),
    "image": f"{figures}",
    "conversations": [
        {
            "from": "human",
            "value": f"{meta_prompt}"
        },
        {
            "from": "assistant",
            "value": "OK, please provide the text grid before move and the current screenshot."
        },
        {
            "from": "human",
            "value": f"This is the grid before move:\n{grid}\nThis is the current screenshot: <image>"
        }
    ]
    }

if __name__ == '__main__':
    args = get_args()
    root_folder = args.data_path
    trials = ['trial_' + str(i) for i in range(args.max_trajs)]

    if args.response_template == 'v0':
        meta_prompt = meta_prompt_v0
        template_filling = fill_template_v0
    else:
        raise ValueError(f"Template {args.response_template} not found.")



    # extract and sort step.txt files for each trial
    data_output = []
    for trial in tqdm(trials):
        trial_directory = root_folder + f'/{trial}'
        txt_file_count = len(list(Path(trial_directory).rglob('*.txt')))
        txt_files = [trial_directory + f'/step_{i}.txt' for i in range(txt_file_count-1)]

        action_file = trial_directory + '/actions.txt'
        actions = np.loadtxt(action_file, dtype=str)
        
        last_length = 0
        last_grid = ''
        isFirst = True

        for file_idx in range(len(txt_files)-1):
            file_path = txt_files[file_idx]
            img_path = os.path.relpath(file_path.replace('.txt', '.png'), root_folder)
            last_move = actions[file_idx]
            move = actions[file_idx+1]

            result = process_file(file_path, last_length, last_move, move, isFirst)
            if file_idx > 0:
                response = fill_template_v0(result)
                t = trial.replace("_", "")
                conversation = to_json(f"{t}_step{file_idx}", img_path, meta_prompt, last_grid)
                conversation["reference_answer"] = response
                data_output.append(conversation)

            isFirst = False
            last_length = result[3]
            last_grid = result[0]

    if args.max_trajs > 0:
        output_pth = os.path.join(args.data_path, f'test_{args.response_template}_{args.max_trajs}.json')
    else:
        output_pth = os.path.join(args.data_path, f'test_{args.response_template}.json')
    with open(output_pth, 'w') as f:
        json.dump(data_output, f, indent=2)
