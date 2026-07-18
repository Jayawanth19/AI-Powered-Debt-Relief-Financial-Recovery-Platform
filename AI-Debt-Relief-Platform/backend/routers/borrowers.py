from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/borrowers", tags=["Borrowers"])


@router.post("/", response_model=schemas.BorrowerOut, status_code=201)
def create_borrower(payload: schemas.BorrowerCreate, db: Session = Depends(get_db)):
    borrower = models.Borrower(**payload.model_dump())
    db.add(borrower)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A borrower with this email already exists.")
    db.refresh(borrower)
    return borrower


@router.get("/", response_model=list[schemas.BorrowerOut])
def list_borrowers(db: Session = Depends(get_db)):
    return db.query(models.Borrower).order_by(models.Borrower.created_at.desc()).all()


@router.get("/{borrower_id}", response_model=schemas.BorrowerOut)
def get_borrower(borrower_id: int, db: Session = Depends(get_db)):
    borrower = db.query(models.Borrower).filter(models.Borrower.id == borrower_id).first()
    if not borrower:
        raise HTTPException(status_code=404, detail="Borrower not found")
    return borrower
