python merge_dataset.py \
    --data_paths ./data/trajectories/sokoban/train/train_data_v0_1000.json ./data/trajectories/wordle/train/train_data_v1_5000_fs.json ./data/LLaVA/llava_v1_5_mix665k_sub4k.json \
    --image_dirs ./data/trajectories/sokoban/train/ ./data/trajectories/wordle/train/ ./data/LLaVA \
    --save_file ./data/trained_data_mixed_v0.1.json