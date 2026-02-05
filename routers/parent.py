"""
Parent router for SamIT Global system.
Provides parent operations: view children, attendance, grades, payment status.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from models.user import User
from models.student import Student
from models.attendance import Attendance
from models.grade import Grade
from models.payment import Payment
from schemas.student import StudentResponse
from schemas.attendance import AttendanceResponse
from schemas.grade import GradeResponse
from routers.auth import get_current_user_from_telegram

logger = logging.getLogger(__name__)

router = APIRouter()


def require_parent(current_user: User = Depends(get_current_user_from_telegram)):
    """Dependency to ensure user has parent role"""
    if not current_user.is_parent:
        raise HTTPException(
            status_code=403,
            detail="Parent access required"
        )
    return current_user


# ===== CHILDREN MANAGEMENT =====

@router.get("/children", response_model=List[StudentResponse])
async def get_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get all children of current parent"""
    children = db.query(Student).filter(
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).all()

    return children


@router.get("/children/{child_id}")
async def get_child_details(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get detailed information about a specific child"""
    child = db.query(Student).filter(
        Student.id == child_id,
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    # Get group information
    group = child.group

    # Calculate statistics
    attendance_count = len(child.attendances)
    present_count = sum(1 for att in child.attendances if att.status == "PRESENT")
    attendance_percentage = (present_count / attendance_count * 100) if attendance_count > 0 else 0

    grade_count = len(child.grades)
    average_grade = sum(grade.value for grade in child.grades) / grade_count if grade_count > 0 else 0

    return {
        "id": child.id,
        "first_name": child.first_name,
        "last_name": child.last_name,
        "full_name": child.full_name,
        "date_of_birth": child.date_of_birth,
        "phone": child.phone,
        "address": child.address,
        "notes": child.notes,
        "group": {
            "id": group.id,
            "name": group.name,
            "subject": group.subject,
            "teacher": {
                "first_name": group.teacher.first_name,
                "last_name": group.teacher.last_name
            } if group.teacher else None
        } if group else None,
        "statistics": {
            "total_classes": attendance_count,
            "present_classes": present_count,
            "attendance_percentage": round(attendance_percentage, 1),
            "total_grades": grade_count,
            "average_grade": round(average_grade, 2) if grade_count > 0 else 0
        }
    }


# ===== ATTENDANCE VIEWING =====

@router.get("/children/{child_id}/attendance", response_model=List[AttendanceResponse])
async def get_child_attendance(
    child_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get attendance records for a child"""
    # Verify child belongs to parent
    child = db.query(Student).filter(
        Student.id == child_id,
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    query = db.query(Attendance).filter(Attendance.student_id == child_id)

    if date_from:
        query = query.filter(Attendance.date >= date_from)
    if date_to:
        query = query.filter(Attendance.date <= date_to)

    attendance_records = query.order_by(Attendance.date.desc()).limit(limit).all()

    return attendance_records


@router.get("/children/{child_id}/attendance/stats")
async def get_child_attendance_stats(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get attendance statistics for a child"""
    # Verify child belongs to parent
    child = db.query(Student).filter(
        Student.id == child_id,
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    attendances = child.attendances

    if not attendances:
        return {
            "total_classes": 0,
            "present_count": 0,
            "absent_count": 0,
            "late_count": 0,
            "attendance_percentage": 0.0
        }

    total_classes = len(attendances)
    present_count = sum(1 for att in attendances if att.status == "PRESENT")
    absent_count = sum(1 for att in attendances if att.status == "ABSENT")
    late_count = sum(1 for att in attendances if att.status == "LATE")

    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

    return {
        "total_classes": total_classes,
        "present_count": present_count,
        "absent_count": absent_count,
        "late_count": late_count,
        "attendance_percentage": round(attendance_percentage, 1)
    }


# ===== GRADE VIEWING =====

@router.get("/children/{child_id}/grades", response_model=List[GradeResponse])
async def get_child_grades(
    child_id: int,
    grade_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get grades for a child"""
    # Verify child belongs to parent
    child = db.query(Student).filter(
        Student.id == child_id,
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    query = db.query(Grade).filter(Grade.student_id == child_id)

    if grade_type:
        query = query.filter(Grade.type == grade_type)

    grades = query.order_by(Grade.date_given.desc()).limit(limit).all()

    return grades


@router.get("/children/{child_id}/grades/stats")
async def get_child_grades_stats(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get grade statistics for a child"""
    # Verify child belongs to parent
    child = db.query(Student).filter(
        Student.id == child_id,
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    grades = child.grades

    if not grades:
        return {
            "total_grades": 0,
            "average_grade": 0.0,
            "highest_grade": 0.0,
            "lowest_grade": 0.0,
            "grade_distribution": {}
        }

    total_grades = len(grades)
    grade_values = [grade.value for grade in grades]
    average_grade = sum(grade_values) / total_grades
    highest_grade = max(grade_values)
    lowest_grade = min(grade_values)

    # Grade distribution
    distribution = {}
    for grade in grades:
        letter = grade.grade_letter
        distribution[letter] = distribution.get(letter, 0) + 1

    return {
        "total_grades": total_grades,
        "average_grade": round(average_grade, 2),
        "highest_grade": highest_grade,
        "lowest_grade": lowest_grade,
        "grade_distribution": distribution
    }


# ===== PAYMENT STATUS =====

@router.get("/children/{child_id}/payments")
async def get_child_payments(
    child_id: int,
    limit: int = Query(12, ge=1, le=24),  # Show last year by default
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get payment records for a child"""
    # Verify child belongs to parent
    child = db.query(Student).filter(
        Student.id == child_id,
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    payments = db.query(Payment).filter(
        Payment.student_id == child_id
    ).order_by(Payment.year.desc(), Payment.month.desc()).limit(limit).all()

    return payments


@router.get("/children/{child_id}/payments/current")
async def get_child_current_payment_status(
    child_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get current payment status for a child"""
    # Verify child belongs to parent
    child = db.query(Student).filter(
        Student.id == child_id,
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    # Get current month payment
    current_date = date.today()
    current_payment = db.query(Payment).filter(
        Payment.student_id == child_id,
        Payment.month == current_date.month,
        Payment.year == current_date.year
    ).first()

    # Get group pricing
    group_price = child.group.monthly_price if child.group else 0

    if current_payment:
        return {
            "month": current_payment.month,
            "year": current_payment.year,
            "amount": current_payment.amount,
            "status": current_payment.status,
            "status_display": current_payment.status_display,
            "payment_date": current_payment.payment_date,
            "due_date": current_payment.due_date,
            "group_price": group_price
        }
    else:
        return {
            "month": current_date.month,
            "year": current_date.year,
            "amount": group_price,
            "status": "UNPAID",
            "status_display": "Не оплачено",
            "payment_date": None,
            "due_date": None,
            "group_price": group_price
        }


# ===== DASHBOARD =====

@router.get("/dashboard")
async def get_parent_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_parent)
):
    """Get dashboard data for parent"""
    children = db.query(Student).filter(
        Student.parent_id == current_user.id,
        Student.is_active == 1
    ).all()

    dashboard_data = []

    for child in children:
        # Basic child info
        child_data = {
            "id": child.id,
            "full_name": child.full_name,
            "group_name": child.group.name if child.group else "No group",
            "group_subject": child.group.subject if child.group else "",
        }

        # Attendance stats
        attendances = child.attendances
        if attendances:
            present_count = sum(1 for att in attendances if att.status == "PRESENT")
            attendance_percentage = round((present_count / len(attendances)) * 100, 1)
        else:
            attendance_percentage = 0.0

        child_data["attendance_percentage"] = attendance_percentage

        # Grade stats
        grades = child.grades
        if grades:
            average_grade = round(sum(grade.value for grade in grades) / len(grades), 2)
        else:
            average_grade = 0.0

        child_data["average_grade"] = average_grade
        child_data["total_grades"] = len(grades)

        # Current payment status
        current_date = date.today()
        payment = db.query(Payment).filter(
            Payment.student_id == child.id,
            Payment.month == current_date.month,
            Payment.year == current_date.year
        ).first()

        child_data["payment_status"] = payment.status_display if payment else "Не оплачено"
        child_data["payment_status_code"] = payment.status if payment else "UNPAID"

        dashboard_data.append(child_data)

    return {
        "children": dashboard_data,
        "total_children": len(dashboard_data)
    }
