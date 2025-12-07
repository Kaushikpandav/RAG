from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.agents.graph import rag_chain, retrieve_docs

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    context: Optional[str] = None

@router.post("/message", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Run chain
        response_text = rag_chain.invoke({"question": request.message})
        
        # We also want the context to show in the UI. 
        # Since the chain encapsulates retrieval, we can either:
        # 1. Modify the chain to return context
        # 2. Call retrieval separately (simplest for now without complex RunnablePassthrough maps returning dicts)
        
        # Let's re-run retrieval or just accept we do it twice? No, that's inefficient.
        # Let's use the explicit retrieve function here for getting context to return,
        # or rely on a chain that returns both.
        
        # For simplicity/robustness:
        context = retrieve_docs(request.message)
        
        # If we passed this context to the chain, it would use it.
        # But our current chain calls retrieve_docs internally.
        # Let's just update the chain invocation to accept pre-fetched context if we want to save a call,
        # but the current implementation of `rag_chain` takes `question` and calls `retrieve_docs`.
        
        # It's fast enough for now to just let it run or we optimize later.
        # Actually, let's just use the `context` we got.
        
        # To avoid double retrieval, we can modify the chain logic on the fly or just construct it here.
        # But let's stick to the current plan:
        # We have the response from the chain. We also want the context.
        # Since I configured `retrieve_docs` as a separate function, I can call it.
        # Ideally we refactor `rag_chain` to be `assign` context so it returns it.
        # But time is pressing. I will call `retrieve_docs` separately to populate the UI 'View Sources'.
        # Yes, slightly inefficient (2 queries) but acceptable for MVP.
        
        return ChatResponse(
            response=response_text,
            context=context
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
