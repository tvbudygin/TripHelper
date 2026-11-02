from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.expense import Expense
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseOut
from app.routers.auth import get_current_user
from app.services.trip_service import get_owned_trip

router = APIRouter(prefix="/trips/{trip_id}/expenses", tags=["expenses"])


@router.post("/", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(
    trip_id: str,
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавление расхода"""

    get_owned_trip(db, trip_id, current_user.id)
    new_expense = Expense(trip_id=trip_id, **data.model_dump())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    trip_id: str,
    expense_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удаление расхода"""

    get_owned_trip(db, trip_id, current_user.id)
    found = db.query(Expense).filter(Expense.id == expense_id, Expense.trip_id == trip_id).first()
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Расход не найден")
    db.delete(found)
    db.commit()
