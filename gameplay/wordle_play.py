from re import sub
from httpx import get
import torch
from wordle.response_templates import fill_guess_template_v0, meta_prompt_v0, meta_prompt_beta
from wordle.response_templates import fill_guess_template_v1, meta_prompt_v1, split_fs_from_meta
from wordle.response_templates import fill_user_input_v1_from_response
from gameenv.solvers import wordle_solver
from .vlm_agent import BaseConverter, VLMAgent
from copy import deepcopy

class WordleConverter(BaseConverter):
    def __init__(self, version='v0', num_max_guesses=6, split_few_shot=False):
        if version == 'v0':
            meta_prompt = meta_prompt_v0
            template_filling = fill_guess_template_v0
        elif version == 'beta':
            meta_prompt = meta_prompt_beta
            template_filling = fill_guess_template_v0
        elif version == 'v1':
            meta_prompt = meta_prompt_v1
            template_filling = fill_guess_template_v1
        else:
            raise ValueError(f"Template {version} not found.")
        self.meta_prompt = meta_prompt
        self.template_filling = template_filling
        self.version = version
        self.num_max_guesses = num_max_guesses
        self.split_few_shot = split_few_shot
        self.game_cnt = 0

    def prepare_user_input(self):
        if self.version in ['v0', 'beta']:
            if self.step==0:
                user_input = self.meta_prompt.strip() + ("\n\n Now the game starts." if not self.eval_skills else "")
            else:
                user_input = "This is the result of your guess: [image]"
        elif self.version == 'v1':
            user_input = fill_user_input_v1_from_response(
                step=self.step,
                response=self.conversation[-1]['value'] if self.step>1 else None,
            )
        self.conversation.append({
            "from": "human",
            "value": user_input
        })

    def get_input(self, fig_path: str = None):
        sample_id = f"game{self.game_cnt}_step{self.step}"
        sample = {
            "id": sample_id,
        }
        if self.step > 0:
            sample["image"] = fig_path
        if self.version in ['v0', 'beta']:
            cur_conversation = deepcopy(self.conversation)
            cur_conversation[-1]["value"] = cur_conversation[-1]["value"].replace("[image]", "<image>")
        elif self.version == 'v1':
            conversation_start = [
                {
                    "from": "human",
                    "value": self.meta_prompt
                },
                {
                    "from": "gpt",
                    "value": "OK, I'm ready to play Wordle."
                }
            ]
            if self.split_few_shot:
                cur_conversation = deepcopy(conversation_start)
                cur_conversation[0]["value"], fs_examples = split_fs_from_meta(self.meta_prompt)
                fs_example = fs_examples[min(self.step,2)]
                cur_conversation.append({
                    "from": "human",
                    "value": fs_example[0]
                })
                cur_conversation.append({
                    "from": "assistant",
                    "value": fs_example[1]
                })
                cur_conversation += self.conversation[-1:]
            else:
                cur_conversation = conversation_start + self.conversation[-1:]
        sample["conversations"] = cur_conversation
        return sample

    def get_action(self, model_output: str):
        self.conversation.append({
            "from": "assistant",
            "value": model_output
        })
        guess = model_output.split('GUESS:')[-1].split()[0].strip().lower()
        # if len(guess) != wordle_solver.WORD_LENGTH:
        #     raise ValueError(f"Invalid guess: {guess}")
        self.step += 1
        return guess




'''
dict: key:{'id': {'answer': str,
                    'num_attempts': int,
                    'guesses': [word1, word2, word3, word4, word5, word6], 
                    'responses': [res1, res2, res3, res4, res5, res6],
                    'figures': [id_0, id_1, id_2, id_3, id_4, id_5, id_6]}}
'''
import sys
import argparse
sys.path.append('./')
from gameenv.solvers.wordle_solver import WORDS, WORDS_STANDARD
from gameenv.envs.wordle import WordleEnv
import numpy as np
import random
import os
from tqdm import tqdm

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--data_path",
        type=str,
        default='./data/gameplay/wordle/',
        help="json file with image paths and annotations",
    )
    parser.add_argument(
        "--num_games",
        type=int,
        default=10,
        help="number of games to play",
    )
    parser.add_argument(
        "--response_template",
        type=str,
        default='v0',
    )
    parser.add_argument(
        "--split_few_shot",
        action="store_true",
    )
    parser.add_argument(
        "--num_max_guesses",
        type=int,
        default=6,
    )
    parser.add_argument("--model-path", type=str, default="facebook/opt-350m")
    parser.add_argument("--model-base", type=str, default=None)
    parser.add_argument("--conv-mode", type=str, default="llava_v1")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p", type=float, default=None)
    parser.add_argument("--num_beams", type=int, default=1)
    parser.add_argument("--max_new_tokens", type=int, default=512)

    args = parser.parse_args()
    return args

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

def overlap(word1:str, word2:str):
    return len(set(word1) & set(word2))

def match(word1:str, word2:str):
    return sum([word1[i]==word2[i] for i in range(min(len(word1), len(word2)))])

def find_replacement(word:str, CANDIDATE_WORDS:list):
    if len(word) < len(CANDIDATE_WORDS[0]):
        subwords = [candidate for candidate in CANDIDATE_WORDS if word in candidate]
        if len(subwords) > 0:
            return np.random.choice(subwords)
    if len(word) > len(CANDIDATE_WORDS[0]):
        subwords = [candidate for candidate in CANDIDATE_WORDS if candidate in word]
        if len(subwords) > 0:
            return np.random.choice(subwords)

    match_4 = [candidate for candidate in CANDIDATE_WORDS if match(word, candidate) >= 4]
    if len(match_4) > 0:
        return np.random.choice(match_4)
    match_3 = [candidate for candidate in CANDIDATE_WORDS if match(word, candidate) >= 3]
    if len(match_3) > 0:
        return np.random.choice(match_3)
    overlap_n1 = [candidate for candidate in CANDIDATE_WORDS if overlap(word, candidate) >= len(set(word))-1]
    if len(overlap_n1) > 0:
        return np.random.choice(overlap_n1)
    return None

def get_score(feedback:str):
    score = 0
    for letter in feedback:
        if letter == 'G':
            score += 2
        elif letter == 'Y':
            score += 1
    return score

if __name__ == "__main__":
    args = get_args()
    CANDIDATE_WORDS = list(WORDS_STANDARD)
    NUM_GAMES = args.num_games
    SAVE_PATH = args.data_path
    os.makedirs(SAVE_PATH, exist_ok=True)
    print(f"Total candidate words: {len(CANDIDATE_WORDS)}")
    env = WordleEnv(word_list=CANDIDATE_WORDS, max_attempts=6)
    converter = WordleConverter(
        version=args.response_template, 
        num_max_guesses=args.num_max_guesses, 
        split_few_shot=args.split_few_shot
    )
    agent = VLMAgent(
        converter=converter, 
        model_path=args.model_path, 
        model_base=args.model_base,
        conv_mode=args.conv_mode,
        temperature=args.temperature,
        top_p=args.top_p,
        num_beams=args.num_beams,
        max_new_tokens=args.max_new_tokens,
    )
    all_games = {}
    set_seed(114514)
    for i in tqdm(range(NUM_GAMES)):
        observation = env.reset()
        img = env.render(mode="RGB")
        os.makedirs(f"{SAVE_PATH}/game_{i}", exist_ok=True)
        img_path = f"{SAVE_PATH}/game_{i}/0.png"
        img.save(img_path)
        answer = env.target_word

        agent.reset()
        game_data = {'answer': answer,
                    'figures': [f"{SAVE_PATH}/game_{i}/0.png"],}
        for j in range(1, 1+env.max_attempts):
            action = agent.take_action(img=img_path)
            if action not in CANDIDATE_WORDS:
                print(f"Invalid guess: {action}, ", end="")
                replacement = find_replacement(action, CANDIDATE_WORDS)
                if replacement is not None:
                    print(f"Replace with {replacement}")
                    action = replacement
                else:
                    action = np.random.choice(CANDIDATE_WORDS)
                    print(f"No replacement found. Randomly choose {action}")
                    # import pdb; pdb.set_trace()
            observation, reward, done, info = env.step(action)
            if info['valid'] == False:
                import pdb; pdb.set_trace()
            img = env.render(mode="RGB")
            img_path = f"{SAVE_PATH}/game_{i}/{j}.png"
            img.save(img_path)
            game_data['figures'].append(f"{SAVE_PATH}/game_{i}/{j}.png")
            if done:
                game_data['guesses'] = observation['guesses']
                game_data['responses'] = observation['feedbacks']
                game_data['num_attempts'] = j
                game_data["score"] = get_score(observation['feedbacks'][-1])
                game_data['done'] = True
                break
            elif j == env.max_attempts:
                game_data['guesses'] = observation['guesses']
                game_data['responses'] = observation['feedbacks']
                game_data['num_attempts'] = j
                game_data["score"] = get_score(observation['feedbacks'][-1])
                game_data['done'] = False
        all_games[f"id_{i}"] = game_data

    # save as json file
    import json
    done_rate = sum([game['done'] for game in all_games.values()]) / NUM_GAMES * 100
    print(f"Done rate: {done_rate:.2f}%")
    all_games['done_rate'] = done_rate
    score_distribution = [game['score'] for game in all_games.values()]
    score_distribution = {score: score_distribution.count(score) for score in sorted(set(score_distribution))}
    print(f"Score distribution: {score_distribution}")
    all_games['score_distribution'] = score_distribution
    with open(f"{SAVE_PATH}/data.json", 'w') as f:
        json.dump(all_games, f, indent=4)