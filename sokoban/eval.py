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
    "player_position": "",
    "remain_box": ["empty"],
    "remain_target": ["empty"],
    "obj_dist1": [""]*4,
    "obj_dist2": [""]*8,
    "move_pred": [""]*4,
    "move": ""
}
def extract_info(answer: str):
    info = deepcopy(empty_info)
    lines = answer.lower().split('\n')
    lines = [line for line in lines if len(line) > 0]
    dist1_start = ["Left:", "Right:", "Top:", "Bottom:"]
    dist2_start = ["Left-Left:", "Right-Right:", "Top-Top:", "Bottom-Bottom:", 
                   "Top-Left:", "Top-Right:", "Bottom-Left:", "Bottom-Right:"]
    pred_start = ["Left:", "Right:", "Up:", "Down:"]
    pred_flag = False

    for line in lines:
        try:
            if "Player Position:".lower() in line:
                pairs = get_pairs(line)
                if len(pairs) > 0:
                    info["player_position"] = pairs[0]
            elif "Box Position:".lower() in line:
                pairs = get_pairs(line)
                info["remain_box"] = pairs
            elif "Target Position:".lower() in line:
                pairs = get_pairs(line)
                info["remain_target"] = pairs
            elif line.startswith("MOVE:".lower()):
                info["move"] = line.split(":")[-1].strip()
            elif "move on the 4 directions:" in line:
                pred_flag = True
            elif pred_flag:
                for i, start in enumerate(pred_start):
                    if line.startswith(start.lower()):
                        info["move_pred"][i] = line.split(":")[1].strip()
                        break
            else:
                for i, start in enumerate(dist1_start):
                    if line.startswith(start.lower()):
                        info["obj_dist1"][i] = line.split(":")[1].strip()
                        break
                for i, start in enumerate(dist2_start):
                    if line.startswith(start.lower()):
                        info["obj_dist2"][i] = line.split(":")[1].strip()
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
        "next_move": [],
        "player_position_acc": [],
        "remain_box_f1": [],
        "remain_target_f1": [],
        "adjacent_obj": [],
        "2_adjacent_obj": [],
        "action_result_pred": [],
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
        result["next_move"].append(answer_info["move"] == reference_answer_info["move"])
        result["player_position_acc"].append(answer_info["player_position"] == reference_answer_info["player_position"])
        result["remain_box_f1"].append(get_f1(answer_info["remain_box"], reference_answer_info["remain_box"]))
        result["remain_target_f1"].append(get_f1(answer_info["remain_target"], reference_answer_info["remain_target"]))
        result["adjacent_obj"].append(get_match(answer_info["obj_dist1"], reference_answer_info["obj_dist1"]))
        result["2_adjacent_obj"].append(get_match(answer_info["obj_dist2"], reference_answer_info["obj_dist2"]))
        result["action_result_pred"].append(get_match(answer_info["move_pred"], reference_answer_info["move_pred"]))

    score = {k: sum(v) / len(v) * 100 for k, v in result.items()}
    print(json.dumps(score, indent=4))