import json
import os
import argparse
from tqdm import tqdm
from copy import deepcopy

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--image_dirs",
        type=str,
        nargs="*",
        default=None,
        help="",
    )

    parser.add_argument(
        "--data_paths",
        type=str,
        nargs="*",
        default=None,
        help="",
    )

    parser.add_argument(
        "--save_file",
        type=str,
        default=None,
        help="",
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()
    base_path = os.path.dirname(args.save_file)
    all_data = []
    for data_path, image_dir in zip(args.data_paths, args.image_dirs):
        relative_image_dir = os.path.relpath(image_dir, base_path)
        with open(data_path, 'r') as f:
            data = json.load(f)
        for d in data:
            if 'image' in d:
                d['image'] = os.path.join(relative_image_dir, d['image'])
        all_data.extend(data)
        print(f"Loaded {len(data)} data from {data_path}")
    with open(args.save_file, 'w') as f:
        json.dump(all_data, f, indent=2)