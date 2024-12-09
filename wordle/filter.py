import json
import os
import argparse
from tqdm import tqdm
from copy import deepcopy

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data_path",
        type=str,
        default='./data/wordle_data/',
        help="json file with image paths and annotations",
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    json_pth = os.path.join(args.data_path, 'train', 'data.json')
    with open(json_pth, 'r') as f:
        train_data = json.load(f)

    json_pth = os.path.join(args.data_path, 'test', 'data.json')
    with open(json_pth, 'r') as f:
        test_data = json.load(f)

    train_answers = set([v["answer"] for k, v in train_data.items()])
    filtered_test_data = {k: v for k, v in test_data.items() if v["answer"] in train_answers}
    print(f"Filtered test data from {len(test_data)} to {len(filtered_test_data)}")
    json_pth = os.path.join(args.data_path, 'test', 'filtered_data.json')
    with open(json_pth, 'w') as f:
        json.dump(filtered_test_data, f)