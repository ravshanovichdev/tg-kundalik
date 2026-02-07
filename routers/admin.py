"""
Admin router for SamIT Global system.
Provides administrative operations: user management, groups, payments, notifications.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.group import Group
from models.payment import Payment
from models.schedule import Schedule
from schemas.user import UserResponse, UserUpdate, UserStats, UserCreate
from schemas.student import StudentResponse, StudentCreate, StudentUpdate
from schemas.teacher import TeacherResponse, TeacherCreate, TeacherUpdate
from schemas.schedule import ScheduleResponse, ScheduleCreate, ScheduleUpdate
from schemas.grade import GradeStats
from schemas.attendance import AttendanceStats
from routers.auth import get_current_user_from_telegram
# from services.notification_service import NotificationService  # Временно отключено

logger = logging.getLogger(__name__)

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user_from_telegram)):
    """Dependency to ensure user has admin role"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


# ===== USER MANAGEMENT =====

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get list of users with optional filtering"""
    query = db.query(User)

    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update user information"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Delete user (soft delete by setting inactive)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "User deactivated successfully"}


@router.post("/users/{user_id}/block")
async def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Block user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = True
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "User blocked successfully"}


@router.post("/users/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Unblock user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_blocked = False
    user.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "User unblocked successfully"}


@router.get("/stats/users", response_model=UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get user statistics"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    blocked_users = db.query(User).filter(User.is_blocked == True).count()
    admins_count = db.query(User).filter(User.role == "admin").count()
    teachers_count = db.query(User).filter(User.role == "teacher").count()
    parents_count = db.query(User).filter(User.role == "parent").count()

    return UserStats(
        total_users=total_users,
        active_users=active_users,
        blocked_users=blocked_users,
        admins_count=admins_count,
        teachers_count=teachers_count,
        parents_count=parents_count
    )


# ===== STUDENT MANAGEMENT =====

@router.post("/students", response_model=StudentResponse)
async def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create new student"""
    # Verify parent exists
    parent = db.query(User).filter(User.id == student.parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    # Verify group exists
    group = db.query(Group).filter(Group.id == student.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Create student
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return db_student


@router.get("/students", response_model=List[StudentResponse])
async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    group_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get list of students with optional filtering"""
    query = db.query(Student)

    if group_id:
        query = query.filter(Student.group_id == group_id)
    if parent_id:
        query = query.filter(Student.parent_id == parent_id)

    students = query.offset(skip).limit(limit).all()
    return students


@router.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update student information"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Update fields
    for field, value in student_update.dict(exclude_unset=True).items():
        setattr(student, field, value)

    student.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(student)

    return student


# ===== TEACHER MANAGEMENT =====

@router.post("/teachers", response_model=TeacherResponse)
async def create_teacher(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create new teacher with user account"""
    # Verify user exists
    user = db.query(User).filter(User.id == teacher_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role != "teacher":
        raise HTTPException(status_code=400, detail="User must have teacher role")
    
    # Check if teacher profile already exists
    existing_teacher = db.query(Teacher).filter(Teacher.user_id == teacher_data.user_id).first()
    if existing_teacher:
        raise HTTPException(status_code=400, detail="Teacher profile already exists for this user")
    
    # Create teacher profile
    teacher = Teacher(
        user_id=teacher_data.user_id,
        first_name=teacher_data.first_name,
        last_name=teacher_data.last_name,
        phone=teacher_data.phone,
        email=teacher_data.email,
        specialization=teacher_data.specialization,
        experience_years=teacher_data.experience_years,
        bio=teacher_data.bio
    )
    
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    return teacher


@router.post("/teachers/with-user", response_model=TeacherResponse)
async def create_teacher_with_user(
    telegram_id: int,
    username: Optional[str],
    full_name: Optional[str],
    first_name: str,
    last_name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    specialization: Optional[str] = None,
    experience_years: int = 0,
    bio: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create teacher with new user account"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this telegram_id already exists")
    
    # Create user
    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        role="teacher",
        is_active=True
    )
    db.add(user)
    db.flush()  # Get user.id without committing
    
    # Create teacher profile
    teacher = Teacher(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        specialization=specialization,
        experience_years=experience_years,
        bio=bio
    )
    
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    return teacher


@router.get("/teachers", response_model=List[TeacherResponse])
async def get_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get list of teachers"""
    teachers = db.query(Teacher).offset(skip).limit(limit).all()
    return teachers


@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get specific teacher by ID"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@router.put("/teachers/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int,
    teacher_update: TeacherUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update teacher information"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Update fields
    for field, value in teacher_update.dict(exclude_unset=True).items():
        setattr(teacher, field, value)
    
    teacher.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(teacher)
    
    return teacher


# ===== PARENT MANAGEMENT =====

@router.post("/parents", response_model=UserResponse)
async def create_parent(
    telegram_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    phone: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create new parent user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this telegram_id already exists")
    
    # Create parent user
    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        role="parent",
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/parents", response_model=List[UserResponse])
async def get_parents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get list of parents"""
    parents = db.query(User).filter(User.role == "parent").offset(skip).limit(limit).all()
    return parents


# ===== GROUP MANAGEMENT =====

@router.post("/groups")
async def create_group(
    name: str,
    subject: str,
    teacher_id: int,
    monthly_price: float = 0.0,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create new group"""
    # Verify teacher exists
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    group = Group(
        name=name,
        subject=subject,
        teacher_id=teacher_id,
        monthly_price=monthly_price,
        description=description
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return group


@router.get("/groups")
async def get_groups(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get all groups"""
    groups = db.query(Group).all()
    return groups


@router.put("/groups/{group_id}")
async def update_group(
    group_id: int,
    name: Optional[str] = None,
    subject: Optional[str] = None,
    teacher_id: Optional[int] = None,
    monthly_price: Optional[float] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update group information"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Update fields
    if name is not None:
        group.name = name
    if subject is not None:
        group.subject = subject
    if teacher_id is not None:
        teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        group.teacher_id = teacher_id
    if monthly_price is not None:
        group.monthly_price = monthly_price
    if description is not None:
        group.description = description

    group.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(group)

    return group


# ===== SCHEDULE MANAGEMENT =====

@router.post("/schedules", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create new schedule entry"""
    # Verify group exists
    group = db.query(Group).filter(Group.id == schedule_data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verify teacher exists
    teacher = db.query(Teacher).filter(Teacher.id == schedule_data.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Create schedule
    schedule = Schedule(**schedule_data.dict())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.get("/schedules", response_model=List[ScheduleResponse])
async def get_schedules(
    group_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get list of schedules"""
    query = db.query(Schedule)
    
    if group_id:
        query = query.filter(Schedule.group_id == group_id)
    if teacher_id:
        query = query.filter(Schedule.teacher_id == teacher_id)
    
    schedules = query.all()
    return schedules


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Get specific schedule by ID"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_update: ScheduleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update schedule information"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Update fields
    for field, value in schedule_update.dict(exclude_unset=True).items():
        setattr(schedule, field, value)
    
    schedule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(schedule)
    
    return schedule


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Delete schedule entry"""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    db.delete(schedule)
    db.commit()
    
    return {"message": "Schedule deleted successfully"}


# ===== PAYMENT MANAGEMENT =====

@router.post("/payments")
async def create_payment(
    student_id: int,
    month: int,
    year: int,
    amount: float,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Create payment record"""
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    payment = Payment(
        student_id=student_id,
        group_id=student.group_id,
        amount=amount,
        month=month,
        year=year,
        status="PAID"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


@router.put("/payments/{payment_id}/status")
async def update_payment_status(
    payment_id: int,
    status: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Update payment status"""
    if status not in ["PAID", "UNPAID", "OVERDUE"]:
        raise HTTPException(status_code=400, detail="Invalid payment status")

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = status
    if status == "PAID":
        payment.payment_date = datetime.utcnow()

    db.commit()
    db.refresh(payment)

    # Send notification if payment is unpaid
    if status == "UNPAID":
        # await NotificationService.send_payment_reminder(  # Временно отключено
        #     db, payment.student_id, payment.month, payment.year
        # )
        pass

    return payment


# ===== NOTIFICATIONS =====

@router.post("/notifications/send")
async def send_notification(
    user_ids: List[int],
    message: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Send notification to multiple users"""
    success_count = 0

    for user_id in user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            await NotificationService.send_message_to_user(db, user.telegram_id, message)
            success_count += 1

    return {
        "message": f"Notification sent to {success_count} out of {len(user_ids)} users"
    }


@router.post("/notifications/broadcast")
async def broadcast_notification(
    message: str,
    user_role: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin)
):
    """Send broadcast notification to all users or specific role"""
    query = db.query(User).filter(User.is_active == True, User.is_blocked == False)

    if user_role:
        query = query.filter(User.role == user_role)

    users = query.all()
    success_count = 0

    for user in users:
        await NotificationService.send_message_to_user(db, user.telegram_id, message)
        success_count += 1

    return {
        "message": f"Broadcast sent to {success_count} users"
    }
