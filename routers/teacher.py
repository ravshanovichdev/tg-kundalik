"""
Teacher router for SamIT Global system.
Provides teacher operations: attendance marking, grade assignment, group management.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.group import Group
from models.attendance import Attendance
from models.grade import Grade
from schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceUpdate, BulkAttendanceCreate
from schemas.grade import GradeCreate, GradeResponse, GradeUpdate
from routers.auth import get_current_user_from_telegram
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)

router = APIRouter()


def require_teacher(current_user: User = Depends(get_current_user_from_telegram)):
    """Dependency to ensure user has teacher role"""
    if not current_user.is_teacher:
        raise HTTPException(
            status_code=403,
            detail="Teacher access required"
        )
    return current_user


def get_teacher_profile(current_user: User, db: Session):
    """Get teacher profile for current user"""
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=404,
            detail="Teacher profile not found"
        )
    return teacher


# ===== GROUP MANAGEMENT =====

@router.get("/groups")
async def get_teacher_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Get groups assigned to current teacher"""
    teacher = get_teacher_profile(current_user, db)
    groups = db.query(Group).filter(Group.teacher_id == teacher.id, Group.is_active == 1).all()

    # Add student count to each group
    result = []
    for group in groups:
        group_dict = {
            "id": group.id,
            "name": group.name,
            "subject": group.subject,
            "monthly_price": group.monthly_price,
            "description": group.description,
            "max_students": group.max_students,
            "current_students_count": group.current_students_count,
            "available_slots": group.available_slots,
            "is_full": group.is_full
        }
        result.append(group_dict)

    return result


@router.get("/groups/{group_id}/students")
async def get_group_students(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Get students in teacher's group"""
    teacher = get_teacher_profile(current_user, db)

    # Verify group belongs to teacher
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == teacher.id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or access denied")

    students = db.query(Student).filter(
        Student.group_id == group_id,
        Student.is_active == 1
    ).all()

    return students


# ===== ATTENDANCE MANAGEMENT =====

@router.post("/attendance", response_model=AttendanceResponse)
async def mark_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Mark attendance for a student"""
    teacher = get_teacher_profile(current_user, db)

    # Verify group belongs to teacher
    group = db.query(Group).filter(
        Group.id == attendance.group_id,
        Group.teacher_id == teacher.id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or access denied")

    # Verify student exists in group
    student = db.query(Student).filter(
        Student.id == attendance.student_id,
        Student.group_id == attendance.group_id,
        Student.is_active == 1
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found in this group")

    # Check if attendance already exists for this date
    existing = db.query(Attendance).filter(
        Attendance.student_id == attendance.student_id,
        Attendance.group_id == attendance.group_id,
        Attendance.date == attendance.date.date()  # Convert to date for comparison
    ).first()

    if existing:
        # Update existing record
        existing.status = attendance.status
        existing.notes = attendance.notes
        existing.marked_by = current_user.id
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        attendance_record = existing
    else:
        # Create new record
        attendance_record = Attendance(
            student_id=attendance.student_id,
            group_id=attendance.group_id,
            date=attendance.date,
            status=attendance.status,
            notes=attendance.notes,
            marked_by=current_user.id
        )
        db.add(attendance_record)
        db.commit()
        db.refresh(attendance_record)

    # Send notification if student is absent
    if attendance.status == "ABSENT":
        await NotificationService.send_absence_notification(
            db, attendance.student_id, attendance.date
        )

    return attendance_record


@router.post("/attendance/bulk")
async def mark_bulk_attendance(
    bulk_data: BulkAttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Mark attendance for multiple students at once"""
    teacher = get_teacher_profile(current_user, db)

    # Verify group belongs to teacher
    group = db.query(Group).filter(
        Group.id == bulk_data.group_id,
        Group.teacher_id == teacher.id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or access denied")

    created_records = []
    updated_records = []

    for attendance_item in bulk_data.attendances:
        student_id = attendance_item.get("student_id")
        status = attendance_item.get("status")

        if not student_id or not status:
            continue

        # Verify student exists in group
        student = db.query(Student).filter(
            Student.id == student_id,
            Student.group_id == bulk_data.group_id,
            Student.is_active == 1
        ).first()
        if not student:
            continue

        # Check if attendance already exists
        existing = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.group_id == bulk_data.group_id,
            Attendance.date == bulk_data.date.date()
        ).first()

        if existing:
            existing.status = status
            existing.marked_by = current_user.id
            existing.updated_at = datetime.utcnow()
            updated_records.append(existing)
        else:
            attendance_record = Attendance(
                student_id=student_id,
                group_id=bulk_data.group_id,
                date=bulk_data.date,
                status=status,
                marked_by=current_user.id
            )
            db.add(attendance_record)
            created_records.append(attendance_record)

            # Send notification if absent
            if status == "ABSENT":
                await NotificationService.send_absence_notification(
                    db, student_id, bulk_data.date
                )

    db.commit()

    # Refresh created records
    for record in created_records:
        db.refresh(record)

    return {
        "created": len(created_records),
        "updated": len(updated_records),
        "total": len(created_records) + len(updated_records)
    }


@router.get("/attendance/group/{group_id}")
async def get_group_attendance(
    group_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Get attendance records for a group"""
    teacher = get_teacher_profile(current_user, db)

    # Verify group belongs to teacher
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == teacher.id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or access denied")

    query = db.query(Attendance).filter(Attendance.group_id == group_id)

    if date_from:
        query = query.filter(Attendance.date >= date_from)
    if date_to:
        query = query.filter(Attendance.date <= date_to)

    attendance_records = query.order_by(Attendance.date.desc()).all()

    return attendance_records


# ===== GRADE MANAGEMENT =====

@router.post("/grades", response_model=GradeResponse)
async def assign_grade(
    grade: GradeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Assign grade to student"""
    teacher = get_teacher_profile(current_user, db)

    # Verify group belongs to teacher
    group = db.query(Group).filter(
        Group.id == grade.group_id,
        Group.teacher_id == teacher.id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or access denied")

    # Verify student exists in group
    student = db.query(Student).filter(
        Student.id == grade.student_id,
        Student.group_id == grade.group_id,
        Student.is_active == 1
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found in this group")

    # Create grade record
    grade_record = Grade(
        student_id=grade.student_id,
        group_id=grade.group_id,
        value=grade.value,
        max_value=grade.max_value,
        type=grade.type,
        title=grade.title,
        description=grade.description,
        comment=grade.comment,
        date_given=grade.date_given,
        given_by=current_user.id
    )

    db.add(grade_record)
    db.commit()
    db.refresh(grade_record)

    # Send notification to parent about new grade
    await NotificationService.send_grade_notification(
        db, grade.student_id, grade_record
    )

    return grade_record


@router.get("/grades/group/{group_id}")
async def get_group_grades(
    group_id: int,
    student_id: Optional[int] = None,
    grade_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Get grades for a group"""
    teacher = get_teacher_profile(current_user, db)

    # Verify group belongs to teacher
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.teacher_id == teacher.id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found or access denied")

    query = db.query(Grade).filter(Grade.group_id == group_id)

    if student_id:
        query = query.filter(Grade.student_id == student_id)
    if grade_type:
        query = query.filter(Grade.type == grade_type)

    grades = query.order_by(Grade.date_given.desc()).limit(limit).all()

    return grades


@router.put("/grades/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: int,
    grade_update: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Update grade"""
    # Find grade
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    # Verify teacher owns the group
    teacher = get_teacher_profile(current_user, db)
    group = db.query(Group).filter(
        Group.id == grade.group_id,
        Group.teacher_id == teacher.id
    ).first()
    if not group:
        raise HTTPException(status_code=403, detail="Access denied")

    # Update fields
    for field, value in grade_update.dict(exclude_unset=True).items():
        setattr(grade, field, value)

    grade.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(grade)

    return grade


@router.delete("/grades/{grade_id}")
async def delete_grade(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Delete grade"""
    # Find grade
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    # Verify teacher owns the group
    teacher = get_teacher_profile(current_user, db)
    group = db.query(Group).filter(
        Group.id == grade.group_id,
        Group.teacher_id == teacher.id
    ).first()
    if not group:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(grade)
    db.commit()

    return {"message": "Grade deleted successfully"}
