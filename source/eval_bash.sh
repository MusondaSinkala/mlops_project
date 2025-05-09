#!/usr/bin/env bash

#clone the project github to get the data and unzip
git clone https://github.com/HarisNaveed17/mlops_project.git
sudo apt install unzip
unzip source/data/final_datasets.zip -d source/data/final_datasets
unzip source/data/player_data.zip -d source/data/player_data

#put the data onto the volumes
docker volume create players
sudo mkdir -p /var/lib/docker/volumes/players/_data/
sudo cp -r mlops_project/source/data/final_datasets/final_datasets /var/lib/docker/volumes/players/_data/
sudo cp -r mlops_project/source/data/player_data/player_data /var/lib/docker/volumes/players/_data/
docker run --rm -it -v players:/mnt alpine ls -l /mnt/final_datasets

#start up jupyter
docker run  -d --rm  -p 8888:8888 \
    -v ~/eval-offline-chi/workspace:/home/jovyan/work/ \
    -v players:/mnt/ \
    -e FOOD11_DATA_DIR=/mnt/temp_data \
    --name jupyter \
    quay.io/jupyter/pytorch-notebook:pytorch-2.5.1

docker logs jupyter
