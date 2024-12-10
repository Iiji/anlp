import json
import os
import argparse
from tqdm import tqdm
from copy import deepcopy

from response_templates import fill_guess_template_v0, meta_prompt_v0

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data_path",
        type=str,
        default='./data/wordle_data/',
        help="json file with image paths and annotations",
    )
    parser.add_argument(
        "--response_template",
        type=str,
        default='v0',
    )
    parser.add_argument(
        "--num_max_guesses",
        type=int,
        default=6,
    )
    parser.add_argument(
        "--eval_skills",
        action="store_true",
    )
    parser.add_argument(
        "--add_simple_thoughts",
        action="store_true",
        help="add simple human written thoughts",
    )
    parser.add_argument(
        "--add_potential_guesses",
        action="store_true",
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()
    json_pth = os.path.join(args.data_path, 'filtered_data.json')
    with open(json_pth, 'r') as f:
        data = json.load(f)

    if args.response_template == 'v0':
        meta_prompt = meta_prompt_v0
        template_filling = fill_guess_template_v0
    else:
        raise ValueError(f"Template {args.response_template} not found.")

    data_output = []
    for id, trajectory in tqdm(data.items()):
        i = int(id.split('_')[1])
        answer = trajectory['answer']
        figures = [fig[fig.find('traj_'):] for fig in trajectory['figures']]
        guesses = trajectory['guesses']
        response = trajectory['responses']
        num_attempts = len(response)

        correct_letters = '?'*len(answer)
        letter_wrong_positions = {}
        appreance_counts = {}
        unused_letters = []
        conversation = []
        for step, guess in enumerate(guesses):
            model_output, correct_letters, letter_wrong_positions, appreance_counts, unused_letters = template_filling(
                current_guess=guess,
                current_response=response[step-1] if step>0 else '?' * len(guess),
                attempts=step,
                remaining_attempts=args.num_max_guesses-step,
                correct_letters=correct_letters,
                letter_wrong_positions=letter_wrong_positions,
                appreance_counts=appreance_counts,
                unused_letters=unused_letters,
                last_guess=guesses[step-1] if step>0 else None,
                make_guess=not args.eval_skills
            )
            if step==0:
                user_input = meta_prompt.strip() + ("\n\n Now the game starts." if not args.eval_skills else "")
            else:
                user_input = "This is the result of your guess: [image]"
            conversation.append({
                "from": "human",
                "value": user_input
            })
            conversation.append({
                "from": "assistant",
                "value": model_output
            })

        if args.eval_skills:
            for step in range(1, len(guesses)):
                cur_conversation = deepcopy(conversation)[:(step+1)*2]
                if len(cur_conversation) > 4:
                    cur_conversation = cur_conversation[:1] + cur_conversation[-3:]
                cur_conversation[-2]["value"] = cur_conversation[-2]["value"].replace("[image]", "<image>")
                sample_id = f"{i}_step{step}"
                sample = {
                    "id": sample_id,
                }
                if step > 0:
                    sample["image"] = figures[step]
                sample["conversations"] = cur_conversation[:-1]
                sample["reference_answer"] = cur_conversation[-1]["value"]
                data_output.append(sample)
        else:
            for step in range(len(guesses)):
                cur_conversation = deepcopy(conversation)[:(step+1)*2]
                cur_conversation[-2]["value"] = cur_conversation[-2]["value"].replace("[image]", "<image>")
                sample_id = f"{i}_step{step}"
                sample = {
                    "id": sample_id,
                }
                if step > 0:
                    sample["image"] = figures[step]
                sample["conversations"] = cur_conversation[:-1]
                sample["reference_answer"] = cur_conversation[-1]["value"]
                data_output.append(sample)

    if args.eval_skills:
        output_pth = os.path.join(args.data_path, f'test_skills_{args.response_template}.json')
    else:
        output_pth = os.path.join(args.data_path, f'test_match_{args.response_template}.json')
    with open(output_pth, 'w') as f:
        json.dump(data_output, f, indent=2)