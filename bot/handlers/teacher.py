"""
Teacher handlers for SamIT Global Telegram bot.
Provides teacher-specific commands and quick actions.
"""
import logging
from aiogram import types
from sqlalchemy.orm import Session

from bot.bot import dp
from data.db import Users
from app.database import SessionLocal

logger = logging.getLogger(__name__)


def is_teacher(telegram_id: int, db: Session) -> bool:
    """
    Check if user is teacher.
    """
    user = Users.getUserById(telegram_id)
    return user and user.get('role') == 'teacher'


@dp.message_handler(commands=['teacher'])
async def cmd_teacher(message: types.Message):
    """
    Teacher panel access.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_teacher(message.from_user.id, db):
                await message.reply("❌ У вас нет доступа к преподавательской панели.")
                return

            teacher_text = (
                f"👨‍🏫 <b>Преподавательская панель</b>\n\n"
                f"📚 <b>Доступные команды:</b>\n"
                f"/my_groups - Мои группы\n"
                f"/today_attendance - Посещаемость сегодня\n"
                f"/recent_grades - Недавние оценки\n\n"
                f"🚀 Все функции доступны в приложении!"
            )

            from bot.keyboards import get_welcome_keyboard
            await message.reply(teacher_text, reply_markup=get_welcome_keyboard())

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in teacher command: {e}")
        await message.reply("❌ Произошла ошибка.")


@dp.message_handler(commands=['my_groups'])
async def cmd_my_groups(message: types.Message):
    """
    Show teacher's groups.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_teacher(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            # Get teacher profile
            from models.teacher import Teacher
            teacher = db.query(Teacher).filter(Teacher.user_id == message.from_user.id).first()

            if not teacher:
                await message.reply("❌ Профиль преподавателя не найден.")
                return

            groups = teacher.groups

            if not groups:
                await message.reply("📝 У вас пока нет назначенных групп.")
                return

            groups_text = f"📚 <b>Ваши группы ({len(groups)}):</b>\n\n"

            for group in groups:
                if group.is_active:
                    students_count = len([s for s in group.students if s.is_active])
                    groups_text += (
                        f"📖 <b>{group.name}</b>\n"
                        f"   Предмет: {group.subject}\n"
                        f"   Учеников: {students_count}/{group.max_students}\n"
                        f"   Цена: {group.monthly_price} UZS\n\n"
                    )

            await message.reply(groups_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in my_groups command: {e}")
        await message.reply("❌ Ошибка получения списка групп.")


@dp.message_handler(commands=['today_attendance'])
async def cmd_today_attendance(message: types.Message):
    """
    Show today's attendance summary for teacher's groups.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_teacher(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            from datetime import date
            from models.attendance import Attendance
            from models.teacher import Teacher

            today = date.today()

            # Get teacher profile
            teacher = db.query(Teacher).filter(Teacher.user_id == message.from_user.id).first()

            if not teacher:
                await message.reply("❌ Профиль преподавателя не найден.")
                return

            # Get attendance for all teacher's groups today
            group_ids = [group.id for group in teacher.groups if group.is_active]

            if not group_ids:
                await message.reply("📝 У вас нет активных групп.")
                return

            attendances = db.query(Attendance).filter(
                Attendance.group_id.in_(group_ids),
                Attendance.date == today
            ).all()

            if not attendances:
                await message.reply("📊 Сегодня еще не отмечена посещаемость.")
                return

            # Group by status
            status_counts = {}
            for att in attendances:
                status = att.status
                status_counts[status] = status_counts.get(status, 0) + 1

            summary_text = (
                f"📊 <b>Посещаемость сегодня ({today.strftime('%d.%m.%Y')}):</b>\n\n"
                f"📈 <b>Всего записей:</b> {len(attendances)}\n"
            )

            status_names = {
                "PRESENT": "Присутствовали",
                "ABSENT": "Отсутствовали",
                "LATE": "Опоздали"
            }

            for status, count in status_counts.items():
                status_name = status_names.get(status, status)
                percentage = (count / len(attendances)) * 100
                summary_text += f"• {status_name}: {count} ({percentage:.1f}%)\n"

            await message.reply(summary_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in today_attendance command: {e}")
        await message.reply("❌ Ошибка получения посещаемости.")


@dp.message_handler(commands=['recent_grades'])
async def cmd_recent_grades(message: types.Message):
    """
    Show recent grades assigned by teacher.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_teacher(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            from models.grade import Grade

            # Get recent grades (last 10)
            recent_grades = db.query(Grade).filter(
                Grade.given_by == message.from_user.id
            ).order_by(Grade.date_given.desc()).limit(10).all()

            if not recent_grades:
                await message.reply("📝 Вы еще не выставляли оценки.")
                return

            grades_text = f"📊 <b>Недавние оценки (последние {len(recent_grades)}):</b>\n\n"

            for grade in recent_grades:
                student_name = f"{grade.student.first_name} {grade.student.last_name}" if grade.student else "Неизвестный"
                date_str = grade.date_given.strftime("%d.%m")

                grades_text += (
                    f"🎯 <b>{grade.value}</b> - {student_name}\n"
                    f"   {grade.type_display} | {date_str}\n"
                )

                if grade.title:
                    grades_text += f"   \"{grade.title}\"\n"

                grades_text += "\n"

            await message.reply(grades_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in recent_grades command: {e}")
        await message.reply("❌ Ошибка получения оценок.")
