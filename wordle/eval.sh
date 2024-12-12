#!/bin/bash

gpu_list="${CUDA_VISIBLE_DEVICES:-0}"
IFS=',' read -ra GPULIST <<< "$gpu_list"

CHUNKS=${#GPULIST[@]}

CKPT="llava-wordle-v0.41-lora"
SPLIT="test"

for IDX in $(seq 0 $((CHUNKS-1))); do
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
        --model-path checkpoints/$CKPT \
        --model-base liuhaotian/llava-v1.5-7b \
        --question-file ./data/trajectories/wordle/test/test_v1.json \
        --image-folder ./data/trajectories/wordle/test/ \
        --answers-file ./data/eval/wordle/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
        --num-chunks $CHUNKS \
        --chunk-idx $IDX \
        --temperature 0 \
        --conv-mode vicuna_v1 &
done

wait

output_file=./data/eval/wordle/answers/$SPLIT/$CKPT/merge.jsonl

# Clear out the output file if it exists.
> "$output_file"

# Loop through the indices and concatenate each file.
for IDX in $(seq 0 $((CHUNKS-1))); do
    cat ./data/eval/wordle/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
done

python wordle/eval.py --result_path ./data/eval/wordle/answers/$SPLIT/$CKPT/



CKPT="llava-wordle-v0.41-full-lora"
SPLIT="test"

for IDX in $(seq 0 $((CHUNKS-1))); do
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
        --model-path checkpoints/$CKPT \
        --model-base liuhaotian/llava-v1.5-7b \
        --question-file ./data/trajectories/wordle/test/test_v1.json \
        --image-folder ./data/trajectories/wordle/test/ \
        --answers-file ./data/eval/wordle/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
        --num-chunks $CHUNKS \
        --chunk-idx $IDX \
        --temperature 0 \
        --conv-mode vicuna_v1 &
done

wait

output_file=./data/eval/wordle/answers/$SPLIT/$CKPT/merge.jsonl

# Clear out the output file if it exists.
> "$output_file"

# Loop through the indices and concatenate each file.
for IDX in $(seq 0 $((CHUNKS-1))); do
    cat ./data/eval/wordle/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
done

python wordle/eval.py --result_path ./data/eval/wordle/answers/$SPLIT/$CKPT/






# CKPT="llava-wordle-v0.31-lora"
# SPLIT="match_test"

# for IDX in $(seq 0 $((CHUNKS-1))); do
#     CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
#         --model-path checkpoints/$CKPT \
#         --model-base liuhaotian/llava-v1.5-7b \
#         --question-file ./data/trajectories/wordle/test/test_match_v0.json \
#         --image-folder ./data/trajectories/wordle/test/ \
#         --answers-file ./data/eval/wordle/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
#         --num-chunks $CHUNKS \
#         --chunk-idx $IDX \
#         --temperature 0 \
#         --conv-mode vicuna_v1 &
# done

# wait

# output_file=./data/eval/wordle/answers/$SPLIT/$CKPT/merge.jsonl

# # Clear out the output file if it exists.
# > "$output_file"

# # Loop through the indices and concatenate each file.
# for IDX in $(seq 0 $((CHUNKS-1))); do
#     cat ./data/eval/wordle/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
# done

# python wordle/eval_match.py --result_path ./data/eval/wordle/answers/$SPLIT/$CKPT/






# CKPT="llava-wordle-v0.31-lora"
# SPLIT="skill_test"

# for IDX in $(seq 0 $((CHUNKS-1))); do
#     CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
#         --model-path checkpoints/$CKPT \
#         --model-base liuhaotian/llava-v1.5-7b \
#         --question-file ./data/trajectories/wordle/test/test_skills_v0.json \
#         --image-folder ./data/trajectories/wordle/test/ \
#         --answers-file ./data/eval/wordle/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
#         --num-chunks $CHUNKS \
#         --chunk-idx $IDX \
#         --temperature 0 \
#         --conv-mode vicuna_v1 &
# done

# wait

# output_file=./data/eval/wordle/answers/$SPLIT/$CKPT/merge.jsonl

# # Clear out the output file if it exists.
# > "$output_file"

# # Loop through the indices and concatenate each file.
# for IDX in $(seq 0 $((CHUNKS-1))); do
#     cat ./data/eval/wordle/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
# done

# python wordle/eval_skills.py --result_path ./data/eval/wordle/answers/$SPLIT/$CKPT/ --skip_first_step