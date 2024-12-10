python convert-train.py \
    --data_path ../data/trajectories/sokoban/train \
    --response_template v0 \
    --max_trajs 1000

python convert-test.py \
    --data_path ../data/trajectories/sokoban/test \
    --response_template v0 \
    --max_trajs 50
