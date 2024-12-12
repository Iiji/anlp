python convert-train.py \
    --data_path ../data/trajectories/snake/train \
    --response_template v0 \
    --max_trajs 300

python convert-train.py \
    --data_path ../data/trajectories/snake/train \
    --response_template v2 \
    --max_trajs 300

python convert-train.py \
    --data_path ../data/trajectories/snake/train \
    --response_template v0 \
    --max_trajs 1000

python convert-train.py \
    --data_path ../data/trajectories/snake/train \
    --response_template v2 \
    --max_trajs 1000

python convert-test.py \
    --data_path ../data/trajectories/snake/test \
    --response_template v0 \
    --max_trajs 10

python convert-test.py \
    --data_path ../data/trajectories/snake/test \
    --response_template v2 \
    --max_trajs 10
