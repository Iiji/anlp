import os
import json
import argparse
import numpy as np

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data_path",
        type=str,
        default="data/LLaVA/llava_v1_5_mix665k.json",
        help="json file with image paths and annotations",
    )

    parser.add_argument(
        "--nsamples",
        type=int,
        default=4096,
        help="Number of samples for the subset",
    )

    args = parser.parse_args()

    with open(args.data_path, 'r') as f:
        data = json.load(f)

    data_subset = np.random.choice(data, args.nsamples, replace=False).tolist()

    filename = args.data_path.replace('.json', f'_{args.nsamples}.json')
    with open(filename, 'w') as f:
        json.dump(data_subset, f, indent=2)

