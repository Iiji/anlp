import json
import os
import argparse
from tqdm import tqdm
from copy import deepcopy

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--result_path",
        type=str,
        default='',
        help="json file with image paths and annotations",
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    answer_file = os.path.join(args.result_path, 'merge.jsonl')
    answer = [json.loads(line) for line in open(answer_file, 'r')]

    result = {
        "match":{
            "all": 0,
        },
        "collected":{
            "all": 0,
        }
    }
    for ans in answer:
        id = ans['question_id']
        step = id.split('_')[1]
        answer_prefix = "GUESS: "
        answer = ans['text']
        reference_answer = ans['reference_answer']
        answer_word = answer.split(answer_prefix)[1].strip() if answer_prefix in answer else answer.split()[-1]
        reference_answer_word = reference_answer.split(answer_prefix)[1].strip()
        if answer_word == reference_answer_word:
            result["match"]["all"] += 1
            result["match"][step] = result["match"].get(step, 0) + 1
        result["collected"]["all"] += 1
        result["collected"][step] = result["collected"].get(step, 0) + 1

    for k, v in result["collected"].items():
        score = result["match"].get(k,0) / v
        print(f"{k} match: {score*100}, collected: {v}")
