#!/bin/bash
# Setup script for graph-tool in WSL Ubuntu
# Run this inside WSL: bash /mnt/c/Users/snapo/Develop/softnet/wsl/setup_graphtool.sh

set -e

echo "Adding graph-tool PPA..."
echo "deb [ arch=amd64 ] https://downloads.skewed.de/apt $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/graph-tool.list

sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-key 612DEFB798507F25

echo "Installing graph-tool..."
sudo apt update
sudo apt install -y python3-graph-tool

echo "graph-tool installed successfully."
python3 -c "import graph_tool; print(f'graph-tool version: {graph_tool.__version__}')"
