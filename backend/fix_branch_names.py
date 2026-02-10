"""
Script to normalize branch names in the database
Run this to fix inconsistent branch names like "CES AIMl" vs "CSE AIML"
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import SessionLocal
from app.models.student import Student

def normalize_branch_names():
    """
    Normalize all branch names to uppercase and trimmed
    This fixes typos like "CES AIMl" -> "CSE AIML"
    """
    db: Session = SessionLocal()
    
    try:
        # Get all students with their current branches
        students = db.query(Student).filter(Student.branch != None).all()
        
        changes = []
        for student in students:
            original = student.branch
            normalized = student.branch.strip().upper()
            
            if original != normalized:
                changes.append({
                    'prn': student.prn,
                    'old': original,
                    'new': normalized
                })
                student.branch = normalized
        
        if changes:
            print(f"\n📝 Found {len(changes)} students with inconsistent branch names:\n")
            for change in changes:
                print(f"  PRN: {change['prn']}")
                print(f"    '{change['old']}' -> '{change['new']}'")
            
            # Commit changes
            db.commit()
            print(f"\n✅ Successfully normalized {len(changes)} branch names!")
            
            # Show summary of unique branches
            unique_branches = db.query(
                Student.branch,
                func.count(Student.prn).label('count')
            ).filter(Student.branch != None)\
             .group_by(Student.branch)\
             .order_by(func.count(Student.prn).desc())\
             .all()
            
            print(f"\n📊 Branches after normalization:")
            for branch, count in unique_branches:
                print(f"  {branch}: {count} students")
        else:
            print("\n✅ All branch names are already normalized!")
            
            # Show current branches
            unique_branches = db.query(
                Student.branch,
                func.count(Student.prn).label('count')
            ).filter(Student.branch != None)\
             .group_by(Student.branch)\
             .order_by(func.count(Student.prn).desc())\
             .all()
            
            print(f"\n📊 Current branches:")
            for branch, count in unique_branches:
                print(f"  {branch}: {count} students")
    
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("Branch Name Normalization Script")
    print("="*60)
    normalize_branch_names()
    print("\n" + "="*60)
