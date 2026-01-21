from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.database import Base, engine
from mangum import Mangum


origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8000",
]

app = FastAPI(title="Financial Data Platform")

# Configure CORS using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Financial Data Platform"}

def handler(event, context):
    asgi_handler = Mangum(app)
    return asgi_handler(event, context)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
