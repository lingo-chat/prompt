import os

from fastapi import Depends, FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app import crud, models, schemas
from app.database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# Session management
app.add_middleware(SessionMiddleware, secret_key=os.getenv('SESSION_SECRET_KEY'))

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def get(request: Request):
    return {"HELLO": "HELLO"}


@app.post("/backup")
async def save_output(chat_history: schemas.chat_history_backup):
    db = SessionLocal()
    try:
        crud.backup_chat_history(db, chat_history)
        db.close()
        print(">> Chat history backuped successfully!")
        return True
    except Exception as e:
        print(f">> Error in crud backup: {e}\n\n")
        return False
    
    
@app.get("/reload")
async def reload_history(chat_room_id: int):
    db = SessionLocal()
    try:
        history = crud.reload_chat_history(db, chat_room_id)
        db.close()
        
        if len(history) == 0:
            return None
        if crud.delete_chat_history(db, chat_room_id):
            print(">> Chat history found! Deleted chat history successfully!")
        return history
    
    except Exception as e:
        print(f">> Error in crud reload: {e}\n\n")
        return False


# if __name__ == "__main__":
#     # this file should be run in another terminal
#     # ex) uvicorn main:app --reload --host 0.0.0.0 --port 9542 (포트포워딩 불필요)