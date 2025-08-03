from fastapi import FastAPI
from routers import process_router, chat_router
from db.pg_connection import Base, engine

api = FastAPI()

api.include_router(process_router.router)
api.include_router(chat_router.router)

# Create the database tables if they do not exist
Base.metadata.create_all(bind=engine)
