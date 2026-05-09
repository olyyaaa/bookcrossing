from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import *
from app.routers import auth, users, books, exchanges, reviews, notifications

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Інформаційна система буккросингу",
    description="API для обміну книгами між учасниками буккросингу",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(exchanges.router)
app.include_router(reviews.router)
app.include_router(notifications.router)

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")

@app.get("/profile")
def profile_page(request: Request):
    return templates.TemplateResponse(request, "profile.html")

@app.get("/book/{book_id}")
def book_detail_page(book_id: int, request: Request):
    return templates.TemplateResponse(request, "book_detail.html", {"book_id": book_id})

@app.get("/add-book")
def add_book_page(request: Request):
    return templates.TemplateResponse(request, "add_book.html")

@app.get("/exchanges")
def exchanges_page(request: Request):
    return templates.TemplateResponse(request, "exchanges.html")