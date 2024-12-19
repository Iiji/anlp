#!/bin/bash

# CKPT="llava-sokoban-v0.31-lora"

# CUDA_VISIBLE_DEVICES=0 python -m gameplay.sokoban_play \
#     --data_path ./data/gameplay/sokoban/ \
#     --num_games 10 \
#     --response_template v0 \
#     --model-path checkpoints/$CKPT \
#     --model-base liuhaotian/llava-v1.5-7b \
#     --temperature 0 \
#     --conv-mode vicuna_v1



# CKPT="llava-v1.5-7b"

# CUDA_VISIBLE_DEVICES=0 python -m gameplay.sokoban_play \
#     --data_path ./data/gameplay/sokoban-llava/ \
#     --num_games 10 \
#     --response_template vllava \
#     --model-path liuhaotian/llava-v1.5-7b \
#     --temperature 0 \
#     --conv-mode vicuna_v1

