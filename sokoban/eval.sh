#!/bin/bash

gpu_list="${CUDA_VISIBLE_DEVICES:-0}"
IFS=',' read -ra GPULIST <<< "$gpu_list"

CHUNKS=${#GPULIST[@]}

CKPT="llava-sokoban-v0.31-lora"
SPLIT="test"

for IDX in $(seq 0 $((CHUNKS-1))); do
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
        --model-path checkpoints/$CKPT \
        --model-base liuhaotian/llava-v1.5-7b \
        --question-file ./data/trajectories/sokoban/test/test_v0_50.json \
        --image-folder ./data/trajectories/sokoban/test/ \
        --answers-file ./data/eval/sokoban/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
        --num-chunks $CHUNKS \
        --chunk-idx $IDX \
        --temperature 0 \
        --conv-mode vicuna_v1 &
done

wait

output_file=./data/eval/sokoban/answers/$SPLIT/$CKPT/merge.jsonl

# Clear out the output file if it exists.
> "$output_file"

# Loop through the indices and concatenate each file.
for IDX in $(seq 0 $((CHUNKS-1))); do
    cat ./data/eval/sokoban/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
done

python sokoban/eval.py --result_path ./data/eval/sokoban/answers/$SPLIT/$CKPT/