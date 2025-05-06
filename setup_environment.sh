#!/bin/bash

echo "🛠️ Installing tdfs CLI"
curl -sfL 2dfs.github.io/install-tdfs.sh | sh - 

echo "🛠️ Downloading and installing the dataset"
##if splits folder not there, download it
if [ ! -d "splits" ]; then
    curl -L https://github.com/2DFS/artifacts-evaluation/releases/download/models/splits.tar.gz -o splits.tar.gz
    tar -xvf splits.tar.gz
    rm -rf splits.tar.gz

echo "🛠️ Configuring docker reigstry and snapshotter"
mv /etc/docker/daemon.json /etc/docker/daemon.json.bak &> /dev/null
sudo cp extra/daemon.json /etc/docker/daemon.json
sudo systemctl restart docker

echo "🛠️ Start 2dfs-registry"
docker run -d -p 10500:5000 --restart=always --name 2dfs-registry ghcr.io/2dfs/2dfs-registry:edge

echo "🛠️ Downloading ubuntu:22.04 base image"
docker pull ubuntu:22.04 
docker tag ubuntu:22.04  0.0.0.0:105000/ubuntu:22.04

echo "🛠️ Set venv"
python3 -m venv ./venv
source ./venv/bin/activate

echo "🛠️ Install requirements"
pip3 install -r requirements.txt
