python convert-train.py \
    --data_path ../data/trajectories/wordle/train \
    --response_template v1 

python convert-train.py \
    --data_path ../data/trajectories/wordle/train \
    --response_template v1 \
    --max_trajs 5000 \

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v0 \
    --eval_skills

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template beta \
    --eval_skills

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v0

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template beta

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v1

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v1 \
    --split_few_shot