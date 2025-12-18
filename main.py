from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from Chatbot import chatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chatbot API",
    description="API for the chatbot service",
    version="1.0.0"
)


# Request model
class ChatRequest(BaseModel):
    message: str
    product: Optional[str] = "Ibrahim"


# Response model
class ChatResponse(BaseModel):
    response: str


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "message": "Chatbot API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that processes user messages and returns chatbot responses.
    
    - **message**: The user's message/query
    - **product**: Optional product name (defaults to "Ibrahim")
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"Received chat request for product: {request.product}, message: {request.message[:50]}...")
        
        # Call the chatbot function
        response = chatbot(request.message, request.product)
        
        return ChatResponse(response=response)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

