tmux new -s lingo-ai-client
source /workspace/miniconda3/bin/activate
conda activate lingo-chat

cd /workspace/lingo-chat-prompt/Lingo_Chat/ai_server
python client_main.py