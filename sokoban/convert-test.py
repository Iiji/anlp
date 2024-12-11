import numpy as np
import os
import json
import argparse
from tqdm import tqdm
from response_templates import fill_template_v0, meta_prompt_v0, meta_prompt_vllava

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data_path",
        type=str,
        default='data/trajectories/sokoban/test',
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

def to_json(id, figures, meta_prompt):
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
            "value": "Ok, I will follow the instructions to derive the next move."
        },
        {
            "from": "human",
            "value": "This is the current state: <image>"
        }
    ]
    }

if __name__ == '__main__':
    args = get_args()
    data_pth = os.path.join(args.data_path, 'data.npz')
    data = np.load(data_pth, allow_pickle=True)

    if args.response_template == 'v0':
        meta_prompt = meta_prompt_v0
        template_filling = fill_template_v0
    elif args.response_template == 'vllava':
        meta_prompt = meta_prompt_vllava
        template_filling = fill_template_v0
    else:
        raise ValueError(f"Template {args.response_template} not found.")

    data_output = []
    cnt = 0
    for key in tqdm(data):
        value = data[key].item()
        states = value['states']
        actions = value['actions']
        n = value['num_attempts']
        figures = [fig[fig.find('traj_'):] for fig in value['figures']]

        for i in range(1, n):
            output = template_filling(states[i], actions[i])
            conversation = to_json(key.split('_')[-1]+f"_step{i}", figures[i], meta_prompt)
            conversation["reference_answer"] = output
            data_output.append(conversation)
        cnt += 1
        if args.max_trajs > 0 and cnt >= args.max_trajs:
            break

    if args.max_trajs > 0:
        output_pth = os.path.join(args.data_path, f'test_{args.response_template}_{args.max_trajs}.json')
    else:
        output_pth = os.path.join(args.data_path, f'test_{args.response_template}.json')
    with open(output_pth, 'w') as f:
        json.dump(data_output, f, indent=2)
