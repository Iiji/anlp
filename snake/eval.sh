#!/bin/bash

gpu_list="${CUDA_VISIBLE_DEVICES:-0}"
IFS=',' read -ra GPULIST <<< "$gpu_list"

CHUNKS=${#GPULIST[@]}

CKPT="llava-snake-v0.31-lora"
SPLIT="test"

# for IDX in $(seq 0 $((CHUNKS-1))); do
#     CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
#         --model-path checkpoints/$CKPT \
#         --model-base liuhaotian/llava-v1.5-7b \
#         --question-file ./data/trajectories/snake/test/test_v0_10.json \
#         --image-folder ./data/trajectories/snake/test/ \
#         --answers-file ./data/eval/snake/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
#         --num-chunks $CHUNKS \
#         --chunk-idx $IDX \
#         --temperature 0 \
#         --conv-mode vicuna_v1 &
# done

# wait

# output_file=./data/eval/snake/answers/$SPLIT/$CKPT/merge.jsonl

# # Clear out the output file if it exists.
# > "$output_file"

# # Loop through the indices and concatenate each file.
# for IDX in $(seq 0 $((CHUNKS-1))); do
#     cat ./data/eval/snake/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
# done

# python snake/eval.py --result_path ./data/eval/snake/answers/$SPLIT/$CKPT/



# CKPT="llava-snake-v0.32-1k-lora"
# SPLIT="test"

# for IDX in $(seq 0 $((CHUNKS-1))); do
#     CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
#         --model-path checkpoints/$CKPT \
#         --model-base liuhaotian/llava-v1.5-7b \
#         --question-file ./data/trajectories/snake/test/test_v1_10.json \
#         --image-folder ./data/trajectories/snake/test/ \
#         --answers-file ./data/eval/snake/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
#         --num-chunks $CHUNKS \
#         --chunk-idx $IDX \
#         --temperature 0 \
#         --conv-mode vicuna_v1 &
# done

# wait

# output_file=./data/eval/snake/answers/$SPLIT/$CKPT/merge.jsonl

# # Clear out the output file if it exists.
# > "$output_file"

# # Loop through the indices and concatenate each file.
# for IDX in $(seq 0 $((CHUNKS-1))); do
#     cat ./data/eval/snake/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
# done

# python snake/eval.py --result_path ./data/eval/snake/answers/$SPLIT/$CKPT/




# CKPT="llava-snake-v0.3b-lora"
# SPLIT="test"

# for IDX in $(seq 0 $((CHUNKS-1))); do
#     CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
#         --model-path checkpoints/$CKPT \
#         --model-base liuhaotian/llava-v1.5-7b \
#         --question-file ./data/trajectories/snake/test/test_beta_10.json \
#         --image-folder ./data/trajectories/snake/test/ \
#         --answers-file ./data/eval/snake/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
#         --num-chunks $CHUNKS \
#         --chunk-idx $IDX \
#         --temperature 0 \
#         --conv-mode vicuna_v1 &
# done

# wait

# output_file=./data/eval/snake/answers/$SPLIT/$CKPT/merge.jsonl

# # Clear out the output file if it exists.
# > "$output_file"

# # Loop through the indices and concatenate each file.
# for IDX in $(seq 0 $((CHUNKS-1))); do
#     cat ./data/eval/snake/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
# done

# python snake/eval.py --result_path ./data/eval/snake/answers/$SPLIT/$CKPT/


CKPT="llava-snake-v0.3b-1k-lora"
SPLIT="test"

for IDX in $(seq 0 $((CHUNKS-1))); do
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
        --model-path checkpoints/$CKPT \
        --model-base liuhaotian/llava-v1.5-7b \
        --question-file ./data/trajectories/snake/test/test_beta_10.json \
        --image-folder ./data/trajectories/snake/test/ \
        --answers-file ./data/eval/snake/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
        --num-chunks $CHUNKS \
        --chunk-idx $IDX \
        --temperature 0 \
        --conv-mode vicuna_v1 &
done

wait

output_file=./data/eval/snake/answers/$SPLIT/$CKPT/merge.jsonl

# Clear out the output file if it exists.
> "$output_file"

# Loop through the indices and concatenate each file.
for IDX in $(seq 0 $((CHUNKS-1))); do
    cat ./data/eval/snake/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
done

python snake/eval.py --result_path ./data/eval/snake/answers/$SPLIT/$CKPT/