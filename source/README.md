# Workflow to Access VM and Persistent Storage on Chameleon Cloud

## Terminal 1 (Local)
```bash
ssh -i ~/.ssh/id_rsa_mlops_proj cc@129.114.25.26

# Inside the VM
lsblk
df -h
git pull
cd mlops_project

# Install Jupyter
sudo apt update
sudo apt install -y jupyter-core jupyter-notebook

# Start Jupyter Notebook
jupyter notebook --no-browser --port=8888 --ip=0.0.0.0

# Optional: Run Jupyter in the background
nohup jupyter-notebook --no-browser --port=8888 --ip=0.0.0.0 > jupyter.log 2>&1 &
jupyter notebook list
```

## Terminal 2 (Local)
```bash
ssh -i ~/.ssh/id_rsa_mlops_proj -L 8888:localhost:8888 cc@129.114.25.26
```

Then, in your browser, open: [http://localhost:8888](http://localhost:8888)

## Run Notebooks in Order

### 1. Build baseline model (offline data):
- `1a. Data Preparation.ipynb`
- `2. Player Level Stats.ipynb`
- `3. Visualize Heatmap.ipynb`
- `4. Player Matching.ipynb`

### 2. Handle live data:
- `1b. live_data.py`
- `2b. process_live_data.py`
- `3b. assign_new_players.py`
