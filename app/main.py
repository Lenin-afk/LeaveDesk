from app.routers import auth, leave, wfh
from fastapi import FastAPI
from app.database import Base, engine
from app import models

app = FastAPI(title="LeaveDesk")
Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(leave.router)
app.include_router(wfh.router)
