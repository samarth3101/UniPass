"""
Student Management Routes
Handles student CRUD and bulk import operations
"""

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import csv
from io import StringIO

from app.db.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse
from app.security.jwt import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/students", tags=["Students"])


def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role for student management"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can manage students"
        )
    return current_user


@router.post("/bulk-import", response_model=dict)
def bulk_import_students(
    students_data: List[StudentCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk import students from JSON array
    Expected format: [{"prn": "...", "name": "...", "email": "...", "department": "...", "year": ...}]
    """
    results = {
        "total": len(students_data),
        "imported": 0,
        "duplicates": 0,
        "errors": []
    }
    
    for student_data in students_data:
        try:
            # Check if student already exists
            existing = db.query(Student).filter(Student.prn == student_data.prn).first()
            if existing:
                results["duplicates"] += 1
                continue
            
            # Create new student
            new_student = Student(
                prn=student_data.prn,
                name=student_data.name,
                email=student_data.email,
                department=student_data.department,
                year=student_data.year
            )
            db.add(new_student)
            db.commit()
            results["imported"] += 1
            
        except IntegrityError as e:
            db.rollback()
            results["duplicates"] += 1
        except Exception as e:
            db.rollback()
            results["errors"].append({
                "prn": student_data.prn,
                "error": str(e)
            })
    
    return {
        "success": True,
        "message": f"Imported {results['imported']} students",
        "results": results
    }


@router.post("/bulk-import-csv", response_model=dict)
async def bulk_import_students_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Bulk import students from CSV file
    Expected CSV format: prn,name,email,department,year
    Example:
    PRN001,John Doe,john@university.edu,Computer Science,3
    PRN002,Jane Smith,jane@university.edu,Electrical,2
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV (.csv extension)"
        )
    
    results = {
        "total": 0,
        "imported": 0,
        "duplicates": 0,
        "errors": []
    }
    
    try:
        # Read CSV content
        contents = await file.read()
        csv_text = contents.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(csv_text))
        
        # Validate CSV headers
        required_headers = {'prn', 'name', 'email', 'department', 'year'}
        headers = set(csv_reader.fieldnames or [])
        missing_headers = required_headers - headers
        
        if missing_headers:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required CSV columns: {', '.join(missing_headers)}"
            )
        
        # Process each row
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            results["total"] += 1
            
            try:
                # Validate required fields
                if not row['prn'] or not row['name']:
                    results["errors"].append({
                        "row": row_num,
                        "error": "PRN and Name are required"
                    })
                    continue
                
                # Check if student already exists
                existing = db.query(Student).filter(Student.prn == row['prn'].strip()).first()
                if existing:
                    results["duplicates"] += 1
                    continue
                
                # Parse year (handle empty or invalid values)
                try:
                    year = int(row['year']) if row['year'].strip() else None
                except (ValueError, AttributeError):
                    year = None
                
                # Create new student
                new_student = Student(
                    prn=row['prn'].strip(),
                    name=row['name'].strip(),
                    email=row['email'].strip() if row['email'] else None,
                    department=row['department'].strip() if row['department'] else None,
                    year=year
                )
                db.add(new_student)
                db.commit()
                results["imported"] += 1
                
            except IntegrityError as e:
                db.rollback()
                results["duplicates"] += 1
            except Exception as e:
                db.rollback()
                results["errors"].append({
                    "row": row_num,
                    "prn": row.get('prn', 'N/A'),
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Imported {results['imported']} students from CSV",
            "results": results
        }
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV encoding. Please use UTF-8 encoding."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process CSV: {str(e)}"
        )


@router.get("/", response_model=dict)
def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all students with pagination
    """
    total = db.query(Student).count()
    students = db.query(Student).order_by(Student.id.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "students": students
    }


@router.get("/{prn}", response_model=StudentResponse)
def get_student(
    prn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get student by PRN
    """
    student = db.query(Student).filter(Student.prn == prn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.delete("/{prn}")
def delete_student(
    prn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete student (Admin only)
    """
    student = db.query(Student).filter(Student.prn == prn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    
    return {
        "success": True,
        "message": f"Student {prn} deleted successfully"
    }
