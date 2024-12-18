#!/bin/bash

gpu_list="${CUDA_VISIBLE_DEVICES:-0}"
IFS=',' read -ra GPULIST <<< "$gpu_list"

CHUNKS=${#GPULIST[@]}

CKPT="llava-mixed-v0.1-lora"
SPLIT="test"

for IDX in $(seq 0 $((CHUNKS-1))); do
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
        --model-path checkpoints/$CKPT \
        --model-base liuhaotian/llava-v1.5-7b \
        --question-file ./data/trajectories/wordle/test/test_v1_fs.json \
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




for IDX in $(seq 0 $((CHUNKS-1))); do
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python inference.py \
        --model-path checkpoints/$CKPT \
        --model-base liuhaotian/llava-v1.5-7b \
        --question-file ./data/trajectories/snake/test/test_v2_10.json \
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





SPLIT="mmbench_dev_20230712"
for IDX in $(seq 0 $((CHUNKS-1))); do
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python -m llava.eval.model_vqa_mmbench \
    --model-path checkpoints/$CKPT \
    --model-base liuhaotian/llava-v1.5-7b \
    --question-file ./data/eval/mmbench/$SPLIT.tsv \
    --answers-file ./data/eval/mmbench/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl \
    --num-chunks $CHUNKS \
    --chunk-idx $IDX \
    --single-pred-prompt \
    --temperature 0 \
    --conv-mode vicuna_v1 &
done

wait

output_file=./data/eval/mmbench/answers/$SPLIT/${CKPT}.jsonl

# Clear out the output file if it exists.
> "$output_file"

# Loop through the indices and concatenate each file.
for IDX in $(seq 0 $((CHUNKS-1))); do
    cat ./data/eval/mmbench/answers/$SPLIT/$CKPT/${CHUNKS}_${IDX}.jsonl >> "$output_file"
done

mkdir -p data/eval/mmbench/answers_upload/$SPLIT/
python convert_mmbench_for_submission.py \
    --annotation-file ./data/eval/mmbench/$SPLIT.tsv \
    --result-dir ./data/eval/mmbench/answers/$SPLIT \
    --upload-dir ./data/eval/mmbench/answers_upload/$SPLIT \
    --experiment $CKPT
