
from pathlib import Path
from collections import defaultdict
from datetime import date
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="PennyWise")

BASE_DIR = Path(__file__).resolve().parent

CATEGORIES = [
    "Food", "Transport", "Shopping", "Education",
    "Entertainment", "Health", "Bills", "Other"
]


class Expense(BaseModel):
    amount: float = Field(gt=0)
    category: str
    description: str = ""
    date: date


class SummaryRequest(BaseModel):
    expenses: list[Expense] = Field(default_factory=list)
    budget: float = Field(default=0, ge=0)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "public" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "online", "application": "PennyWise"}


@app.get("/api/categories")
def categories():
    return {"categories": CATEGORIES}


@app.post("/api/summary")
def summary(data: SummaryRequest):
    today = date.today()

    monthly = [
        expense for expense in data.expenses
        if expense.date.year == today.year
        and expense.date.month == today.month
    ]

    total = round(sum(e.amount for e in monthly), 2)

    category_totals = defaultdict(float)

    for expense in monthly:
        category_totals[expense.category] += expense.amount

    return {
        "total": total,
        "budget": data.budget,
        "remaining": round(data.budget - total, 2),
        "percentage": round(total / data.budget * 100, 1)
        if data.budget else 0,
        "transactions": len(monthly),
        "categories": dict(category_totals)
    }
