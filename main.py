from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chiari_xo.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date, nullable=False)
    weight = Column(String, nullable=True)
    food = Column(String, nullable=True)
    walk_minutes = Column(String, nullable=True)
    run_minutes = Column(String, nullable=True)
    distance = Column(String, nullable=True)
    energy = Column(String, nullable=True)
    glucose = Column(String, nullable=True)
    notes = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = SessionLocal()
    logs = db.query(DailyLog).order_by(DailyLog.log_date.desc()).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "logs": logs})

@app.post("/add")
def add_log(
    log_date: str = Form(...),
    weight: str = Form(""),
    food: str = Form(""),
    walk_minutes: str = Form(""),
    run_minutes: str = Form(""),
    distance: str = Form(""),
    energy: str = Form(""),
    glucose: str = Form(""),
    notes: str = Form("")
):
    db = SessionLocal()
    entry = DailyLog(
        log_date=datetime.strptime(log_date, "%Y-%m-%d").date(),
        weight=weight,
        food=food,
        walk_minutes=walk_minutes,
        run_minutes=run_minutes,
        distance=distance,
        energy=energy,
        glucose=glucose,
        notes=notes
    )
    db.add(entry)
    db.commit()
    db.close()
    return RedirectResponse(url="/", status_code=303)