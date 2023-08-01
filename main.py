from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = 'postgresql://postgres:12345@localhost/fastapi'

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

class Task(BaseModel):
    title: str = Field(..., title="Task Title")
    description: str = Field(None, title="Task Description")

    class Config:
        orm_mode = True

class DBTask(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    db_task = DBTask(title=task.title, description=task.description)
    db = SessionLocal()
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    db.close()
    return task

@app.get("/tasks/", response_model=List[Task])
def read_tasks():
    db = SessionLocal()
    tasks = db.query(DBTask).all()
    db.close()
    return tasks

# ... (other routes and operations)
