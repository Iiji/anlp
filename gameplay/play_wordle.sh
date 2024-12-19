#!/bin/bash

CKPT="llava-wordle-v0.4f-lora"

CUDA_VISIBLE_DEVICES=0 python -m gameplay.wordle_play \
    --data_path ./data/gameplay/wordle/ \
    --num_games 100 \
    --response_template v1 \
    --split_few_shot \
    --model-path checkpoints/$CKPT \
    --model-base liuhaotian/llava-v1.5-7b \
    --temperature 0 \
    --conv-mode vicuna_v1
