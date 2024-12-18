import json
import os
import argparse
from matplotlib.pyplot import flag
from tqdm import tqdm
from copy import deepcopy
import re

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--result_path",
        type=str,
        default='',
        help="json file with image paths and annotations",
    )
    parser.add_argument(
        "--skip_first_step",
        action="store_true",
    )

    args = parser.parse_args()
    return args

def get_match(answer: list, reference_answer: list):
    matched = 0
    for a, r in zip(answer, reference_answer):
        if a == r:
            matched += 1
    return matched / max(len(answer), len(reference_answer))

def get_f1(answer, reference_answer):
    if not isinstance(answer, set):
        answer = set(answer)
    if not isinstance(reference_answer, set):
        reference_answer = set(reference_answer)
    tp = len(answer.intersection(reference_answer))
    fp = len(answer - reference_answer)
    fn = len(reference_answer - answer)
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if tp > 0 else 0
    return f1

def get_pairs(line: str):
    pattern = r"\(\d+, \d+\)"
    pairs = re.findall(pattern, line)
    return pairs

empty_info = {
    "grid": [],
    "last_move": "",
    "eaten_food": "",
    "snake_length": -1,
    "snake_head": "",
    "snake_tail": "",
    "food_pos": "",
    "food_dir": "",
    "adj_obj": [""]*4,
    "next_move": "",
}
def extract_info(answer: str):
    info = deepcopy(empty_info)
    lines = answer.lower().split('\n')
    lines = [line for line in lines if len(line) > 0]
    adj_start = ["Left:", "Right:", "Top:", "Bottom:"]
    grid_flag = True

    for line in lines:
        try:
            if "following information:" in line:
                grid_flag = False
            elif grid_flag:
                if line.count(" ") *2+1 >= len(line):
                    grid_line = line.strip().split()
                    if len(grid_line) < 12:
                        grid_line.extend([""]*(12-len(grid_line)))
                    info["grid"].extend(grid_line[:12])
            elif "Eaten food in last move:".lower() in line:
                info["eaten_food"] = line.split(":")[-1].strip()
            elif "Last move:".lower() in line:
                info["last_move"] = line.split(":")[-1].strip()
            elif "snake length:".lower() in line:
                info["snake_length"] = int(line.split(":")[-1].strip())
            elif "head position:".lower() in line:
                info["snake_head"] = line.split(":")[-1].strip()
            elif "tail position:".lower() in line:
                info["snake_tail"] = line.split(":")[-1].strip()
            elif "food position:".lower() in line:
                info["food_pos"] = line.split(":")[-1].strip()
            elif "Direction of the food relative".lower() in line:
                info["food_dir"] = line.split(":")[-1].strip()
            elif line.startswith("MOVE:".lower()):
                info["next_move"] = line.split(":")[-1].strip()
            elif "4 adjacent".lower() in line:
                split_line = line.split(":")
                if len(split_line) > 1 and split_line[1].strip() != "":
                    adj_obj = split_line[1].strip().split(",")
                    info["adj_obj"] = [a.strip() for a in adj_obj]
            else:
                for i, start in enumerate(adj_start):
                    if start.lower() in line:
                        info["adj_obj"][i] = line.split(":")[1].strip()
                        break
        except:
            print(line)

    # for key, value in info.items():
    #     if value == empty_info[key]:
    #         import pdb; pdb.set_trace()
    return info



if __name__ == '__main__':
    args = get_args()
    answer_file = os.path.join(args.result_path, 'merge.jsonl')
    answer = [json.loads(line) for line in open(answer_file, 'r')]

    result = {
        "next_move_acc": [],
        "grid_match": [],
        "last_move_acc": [],
        "eaten_food_acc": [],
        "snake_length_acc": [],
        "food_dir_acc": [],
        "adj_obj_match": [],
        "snake_head_acc": [],
        "snake_tail_acc": [],
        "food_pos_acc": [],
    }
    for ans in tqdm(answer):
        id = ans['question_id']
        step = id.split('_')[1]
        if args.skip_first_step and step == 'step0':
            continue
        answer = ans['text']
        reference_answer = ans['reference_answer']
        answer_info = extract_info(answer)
        reference_answer_info = extract_info(reference_answer)
        result["grid_match"].append(get_match(answer_info["grid"], reference_answer_info["grid"]))
        result["last_move_acc"].append(answer_info["last_move"] == reference_answer_info["last_move"])
        result["eaten_food_acc"].append(answer_info["eaten_food"] == reference_answer_info["eaten_food"])
        result["snake_length_acc"].append(answer_info["snake_length"] == reference_answer_info["snake_length"])
        result["snake_head_acc"].append(answer_info["snake_head"] == reference_answer_info["snake_head"])
        result["snake_tail_acc"].append(answer_info["snake_tail"] == reference_answer_info["snake_tail"])
        result["food_pos_acc"].append(answer_info["food_pos"] == reference_answer_info["food_pos"])
        result["food_dir_acc"].append(answer_info["food_dir"] == reference_answer_info["food_dir"])
        result["adj_obj_match"].append(get_match(answer_info["adj_obj"], reference_answer_info["adj_obj"]))
        result["next_move_acc"].append(answer_info["next_move"] == reference_answer_info["next_move"])

    score = {k: sum(v) / len(v) * 100 for k, v in result.items()}
    score["key_position_acc"] = (score["snake_head_acc"] + score["snake_tail_acc"] + score["food_pos_acc"]) / 3
    print(json.dumps(score, indent=4))