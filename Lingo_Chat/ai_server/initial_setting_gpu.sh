# apt install
apt-get update
apt-get upgrade -y
apt-get install -y git vim tmux
clear
echo -e "1. apt install done.\n\n"

# miniconda install
mkdir -p /workspace/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /workspace/miniconda3/miniconda.sh
bash /workspace/miniconda3/miniconda.sh -b -u -p /workspace/miniconda3
rm /workspace/miniconda3/miniconda.sh

# conda activate
source /workspace/miniconda3/bin/activate
conda create -n lingo-chat python=3.10 -y
conda activate lingo-chat
clear
echo -e  "2. conda activation done.\n\n"


# vllm install
# Install vLLM with CUDA 11.8.
export VLLM_VERSION=0.5.5
export PYTHON_VERSION=310
pip install https://github.com/vllm-project/vllm/releases/download/v${VLLM_VERSION}/vllm-${VLLM_VERSION}+cu118-cp${PYTHON_VERSION}-cp${PYTHON_VERSION}-manylinux1_x86_64.whl --extra-index-url https://download.pytorch.org/whl/cu118
clear
echo -e  "3. vllm installation done.\n\n"

# etc pip install
pip install langchain langgraph 
pip install langgraph-checkpoint-sqlite langchain_openai langchain_google_genai langchain_community
pip install transformers datasets bitsandbytes
pip install python-socketio redis aiosqlite python-Levenshtein tmuxp pyngrok pytz pymysql python-dotenv
pip install -U pip setuptools
# pip install setuptools==3.3
pip install -U "huggingface_hub[cli]"
clear
echo -e  "4. etc packages installation done.\n\n"

# etc setting
ngrok config add-authtoken <your_token>
huggingface-cli login --token <your_token>

# # git clone
# git clone https://github.com/LewisVille-flow/lingo-chat-prompt.git
# cd lingo-chat-prompt
# git checkout -t origin/feat-#22

# model download
cd ./models
mkdir -p ./PAL_orbit_v0.2.2.3
python download.py

# init ai client
cd ../

# vllm server init
chmod +x run_server.sh
. run_server.sh

# client init
chmod +x run_client.sh
. run_client.sh