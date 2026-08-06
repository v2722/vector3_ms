from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chatbot"])


class ChatRequest(BaseModel):
    message: str
    portfolio_id: int | None = None


@router.post("/")
def chat(request: ChatRequest):
    reply = answer_question(request.message, portfolio_id=request.portfolio_id)
    return {"reply": reply}
