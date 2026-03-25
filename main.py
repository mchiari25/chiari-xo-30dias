from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chiari_xo.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_date = Column(Date)
    water = Column(String)
    run = Column(String)
    diet = Column(String)
    notes = Column(String)
    weight_lb = Column(String)
    sugar = Column(String)

Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db = SessionLocal()
    logs = db.query(DailyLog).order_by(DailyLog.log_date.desc()).all()
    db.close()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "logs": logs}
    )

@app.post("/add")
def add_log(
    water: str = Form(...),
    run: str = Form(...),
    diet: str = Form(...),
    notes: str = Form(""),
    weight_lb: str = Form(""),
    sugar: str = Form("")
):
    db = SessionLocal()

    new_log = DailyLog(
        log_date=datetime.date.today(),
        water=water,
        run=run,
        diet=diet,
        notes=notes,
        weight_lb=weight_lb,
        sugar=sugar
    )

    db.add(new_log)
    db.commit()
    db.close()

    return RedirectResponse("/", status_code=303)

@app.post("/reset")
def reset_logs():
    db = SessionLocal()
    db.query(DailyLog).delete()
    db.commit()
    db.close()
    return RedirectResponse("/", status_code=303)