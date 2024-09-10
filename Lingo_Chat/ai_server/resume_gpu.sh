# apt install
apt-get update
apt-get upgrade -y
apt-get install -y git vim
clear
echo -e "1. apt install done.\n\n"

# conda activate
source /workspace/miniconda3/bin/activate
# conda create -n lingo-chat python=3.10 -y
conda activate lingo-chat
clear
echo -e  "2. conda activation done.\n\n"

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

# model download
cd Lingo_Chat/ai_server/model
mkdir -p ./PAL_orbit_v0.2.2.3
python download.py

# init ai client
cd ../

# vllm server init
chmod +x run_server.sh
. run_server.sh
. run_server.sh

# client init
chmod +x run_client.sh
. run_client.sh
. run_client.sh