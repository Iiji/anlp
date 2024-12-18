#!/bin/bash

gpu_list="${CUDA_VISIBLE_DEVICES:-0}"
IFS=',' read -ra GPULIST <<< "$gpu_list"

CHUNKS=${#GPULIST[@]}

CKPT="llava-v1.5-7b"
SPLIT="mmbench_dev_20230712"
for IDX in $(seq 0 $((CHUNKS-1))); do
    CUDA_VISIBLE_DEVICES=${GPULIST[$IDX]} python -m llava.eval.model_vqa_mmbench \
    --model-path liuhaotian/llava-v1.5-7b \
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





output_file=./data/eval/pope/answers/${CKPT}.jsonl
python eval_pope.py \
    --annotation-dir ./data/eval/pope/coco \
    --question-file ./data/eval/pope/llava_pope_test.jsonl \
    --result-file $output_file