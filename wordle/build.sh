python convert-train.py \
    --data_path ../data/trajectories/wordle/train \
    --response_template v0 \
    --max_trajs 4000 \
    --one_img

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v0 \
    --eval_skills

python convert-test.py \
    --data_path ../data/trajectories/wordle/test \
    --response_template v0