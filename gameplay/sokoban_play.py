import torch
from sokoban.response_templates import fill_template_v0, meta_prompt_v0, meta_prompt_vllava
from .vlm_agent import BaseConverter, VLMAgent
from copy import deepcopy

class SokobanConverter(BaseConverter):
    def __init__(self, version='v0'):
        if args.response_template == 'v0':
            meta_prompt = meta_prompt_v0
            template_filling = fill_template_v0
        elif args.response_template == 'vllava':
            meta_prompt = meta_prompt_vllava
            template_filling = fill_template_v0
        else:
            raise ValueError(f"Template {args.response_template} not found.")
        self.meta_prompt = meta_prompt
        self.template_filling = template_filling
        self.version = version
        self.game_cnt = 0

    def to_json(self,id, figures, meta_prompt):
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

    def prepare_user_input(self):
        self.conversation.append({
            "from": "human",
            "value": "This is the current state: <image>"
        })

    def get_input(self, fig_path: str = None):
        sample_id = f"game{self.game_cnt}_step{self.step}"
        sample = self.to_json(sample_id, fig_path, self.meta_prompt)
        return sample

    def get_action(self, model_output: str):
        self.conversation.append({
            "from": "assistant",
            "value": model_output
        })
        guess = model_output.split('MOVE:')[-1].split()[0].strip().lower()
        self.step += 1
        return guess



import sys
import gym
import gym_sokoban
from PIL import Image
import argparse
sys.path.append('./')
from gameenv.solvers.sokoban_solver.sokoban import solve_sokoban
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
        "--num_extra_steps",
        type=int,
        default=10,
        help="number of steps allowed to take more than optimal",
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

ACTION_MAP = {
    'up': 0,
    'down': 1,
    'left': 2,
    'right': 3,
}

if __name__ == "__main__":
    args = get_args()
    NUM_GAMES = args.num_games
    SAVE_PATH = args.data_path
    os.makedirs(SAVE_PATH, exist_ok=True)
    converter = SokobanConverter(
        version=args.response_template, 
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

    set_seed(114514)
    env_name = 'Sokoban-v0'
    env = gym.make(env_name)
    env.seed(114514)
    ACTION_LOOKUP = env.unwrapped.get_action_lookup()
    all_games = {}
    i = 0
    while i < NUM_GAMES:
        env.reset()
        solver_action = solve_sokoban(env)
        os.makedirs(f"{SAVE_PATH}/game_{i}", exist_ok=True)
        if solver_action is None:
            print('this sokoban is unsolvable')
            env.close()
            env = gym.make(env_name)
            continue
        '''
        symbol_map = {
            0: '#',  # Wall
            1: ' ',  # Movable space
            2: '.',  # Destination
            3: 'X',  # box on target
            4: 'B',  # box not on target
            5: '&',  # player
        }
        '''
        state = deepcopy(env.room_state)
        img = env.render(mode='rgb_array')
        image = Image.fromarray(img)
        img_path = f"{SAVE_PATH}/game_{i}/0.png"
        image.save(img_path)
        agent.reset()
        
        game_data = {'figures': [img_path],
                    'states': [state],
                    'actions': []}
        
        num_max_steps = len(solver_action) + args.num_extra_steps
        for t in tqdm(range(num_max_steps), desc=f"Game {i}"):
            # solver approach
            action = agent.take_action(img=img_path)
            observation, reward, done, info = env.step(ACTION_MAP[action])

            state = deepcopy(env.room_state)
            img = env.render(mode='rgb_array')
            # save this image as a file
            image = Image.fromarray(img)
            img_path = f"{SAVE_PATH}/game_{i}/{t+1}.png"
            image.save(img_path)

            game_data['states'].append(state)
            game_data['figures'].append(img_path)
            game_data['actions'].append(action)

            # print(action, reward, done, info)
            if done:
                print("Episode {} finished after {} timesteps".format(i, t+1))
                game_data['num_attempts'] = t + 1
                game_data['extra_steps'] = t + 1 - len(solver_action)
                game_data['done'] = True
                break
            elif t == num_max_steps - 1:
                game_data['num_attempts'] = t + 1
                game_data['extra_steps'] = -1
                game_data['done'] = False
        all_games[f"id_{i}"] = game_data
        i += 1
    env.close()

    done_rate = sum([game['done'] for game in all_games.values()]) / len(all_games) * 100
    print(f"Done rate: {done_rate:.2f}%")
    extra_steps = [game['extra_steps'] for game in all_games.values() if game['done']]
    avg_extra_steps = sum(extra_steps) / len(extra_steps)
    print(f"Avg extra steps: {avg_extra_steps:.2f}")
    np.savez(f"{SAVE_PATH}/data.npz", **all_games)