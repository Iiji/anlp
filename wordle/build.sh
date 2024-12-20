python convert-train.py \
    --data_path ../data/trajectories/wordle/train \
    --response_template v1 \
    --split_few_shot

python convert-train.py \
    --data_path ../data/trajectories/wordle/train \
    --response_template v1 \
    --max_trajs 5000 \
    --split_few_shot

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v0 \
    --eval_skills

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v0

# python convert-test.py \
#     --data_path ../data/trajectories/wordle/test \
#     --response_template v1

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v1 \
    --split_few_shot