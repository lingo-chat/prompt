tmux new -s lingo-ai-server
source /workspace/miniconda3/bin/activate
conda activate lingo-chat

cd /workspace/lingo-chat-prompt/Lingo_Chat/ai_server
python server_main.py