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

empty_info = {
    "last_word": "?????",
    "word_letters": ['?', '?', '?', '?', '?'],
    "colors": ['unknown', 'unknown', 'unknown', 'unknown', 'unknown'],
    "feedback": ["empty"],
    "attempts_made": -1,
    "chances_remaining": -1,
    "correct_letters": "!!!!!",
    "unknown_letters": ["empty"],
    "unused_letters": ["empty"]
}
def extract_info(answer: str):
    info = deepcopy(empty_info)
    lines = answer.split('\n')
    lines = [line for line in lines if len(line) > 0]

    for line in lines:
        try:
            if "last guess is:" in line:
                info['last_word'] = line.split(":")[1].split(",")[0].strip(" ,.").lower()
                if "letters" in line:
                    letters = line.split("letters")[1].split(',')
                    letters = [letter.strip(", ") for letter in letters]
                    info['word_letters'] = [letter.upper()[-1] for letter in letters]
            if "color for each letter" in line:
                colors = line.split(":")[1].lower().split(',')
                info['colors'] = [color.strip(" ,.") for color in colors]
            if "we know that" in line:
                raw_feedbacks = line.split(":")[1].lower().split(';')
                feedbacks = []
                for feedback in raw_feedbacks:
                    if "letter is" in feedback:
                        parts = feedback.split("letter is")
                        parts[0] = parts[0].strip().split(" ")[-1]
                        parts[1] = parts[1].strip(" ,;.").upper()
                        feedbacks.append(f"{parts[0]}_is_{parts[1]}")
                    elif "not appear" in feedback:
                        letter_pos = feedback.find("letter ") + len("letter ")
                        feedbacks.append(f"{feedback[letter_pos]}_not_appear")
                    elif "position" in feedback:
                        position_pos = feedback.find(" position")
                        position = feedback[:position_pos].split(" ")[-1]
                        letter_pos = feedback.find("letter ") + len("letter ")
                        feedbacks.append(f"{feedback[letter_pos]}_not_at_{position}")
                info['feedback'] = feedbacks
            if "have made" in line:
                pos = line.find("have made ") + len("have made ")
                attempts_made = line[pos:].split(" ")[0]
                pos = line.find(" chance")
                chances_remaining = line[:pos].split(" ")[-1]
                info['attempts_made'] = int(attempts_made)
                info['chances_remaining'] = int(chances_remaining)
            if "correct position:" in line:
                info['correct_letters'] = line.split(":")[1].strip(" ,.").upper()
            if "unknown position:" in line:
                raw_unknown_letters = line.split(":")[1].lower().split(';')
                if len(raw_unknown_letters) ==1 and len(raw_unknown_letters[0].strip(" ,.")) == 0:
                    info['unknown_letters'] = []
                else:
                    unknown_letters = []
                    for unknown_letter in raw_unknown_letters:
                        letter_pos = unknown_letter.find("letter ") + len("letter ")
                        letter = unknown_letter[letter_pos]
                        times_pos = unknown_letter.find(" times")
                        times = unknown_letter[:times_pos].split(" ")[-1]
                        positions_pos = unknown_letter.find("positions ") + len("positions ")
                        positions = unknown_letter[positions_pos:].split(",")
                        positions = [position.strip(" ,") for position in positions]
                        unknown_letters.append(f"{letter}_appear_{times}_times")
                        for position in positions:
                            unknown_letters.append(f"{letter}_among_position_{position}")
                    info['unknown_letters'] = unknown_letters
            if "not appear in the word:" in line:
                unused_letters = line.split(":")[1].upper().split(",")
                info['unused_letters'] = [letter.strip(" ,.") for letter in unused_letters]
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
        "last_word": [],
        "word_letter_match": [],
        "color_match": [],
        "feedback_f1": [],
        "attempts_made": [],
        "chances_remaining": [],
        "correct_letters_match": [],
        "unknown_letters_f1": [],
        "unused_letters_f1": []
    }
    for ans in tqdm(answer):
        id = ans['question_id']
        step = id.split('_')[1]
        if args.skip_first_step and step == 'step1':
            continue
        answer = ans['text']
        reference_answer = ans['reference_answer']
        answer_info = extract_info(answer)
        reference_answer_info = extract_info(reference_answer)
        result["last_word"].append(answer_info['last_word'] == reference_answer_info['last_word'])
        result["word_letter_match"].append(get_match(answer_info['word_letters'], reference_answer_info['word_letters']))
        result["color_match"].append(get_match(answer_info['colors'], reference_answer_info['colors']))
        result["feedback_f1"].append(get_f1(answer_info['feedback'], reference_answer_info['feedback']))
        result["attempts_made"].append(answer_info['attempts_made'] == reference_answer_info['attempts_made'])
        result["chances_remaining"].append(answer_info['chances_remaining'] == reference_answer_info['chances_remaining'])
        result["correct_letters_match"].append(get_match(answer_info['correct_letters'], reference_answer_info['correct_letters']))
        result["unknown_letters_f1"].append(get_f1(answer_info['unknown_letters'], reference_answer_info['unknown_letters']))
        result["unused_letters_f1"].append(get_f1(answer_info['unused_letters'], reference_answer_info['unused_letters']))

    score = {k: sum(v) / len(v) for k, v in result.items()}
    print(json.dumps(score, indent=4))