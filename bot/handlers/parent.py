"""
Parent handlers for SamIT Global Telegram bot.
Provides parent-specific commands and quick access to child information.
"""
import logging
from aiogram import types
from sqlalchemy.orm import Session

from bot.bot import dp
from data.db import Users
from app.database import SessionLocal

logger = logging.getLogger(__name__)


def is_parent(telegram_id: int, db: Session) -> bool:
    """
    Check if user is parent.
    """
    user = Users.getUserById(telegram_id)
    return user and user.get('role') == 'parent'


@dp.message_handler(commands=['parent'])
async def cmd_parent(message: types.Message):
    """
    Parent panel access.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_parent(message.from_user.id, db):
                await message.reply("❌ У вас нет доступа к родительской панели.")
                return

            parent_text = (
                f"👨‍👩‍👧 <b>Родительская панель</b>\n\n"
                f"📱 <b>Доступные команды:</b>\n"
                f"/my_children - Мои дети\n"
                f"/attendance - Посещаемость\n"
                f"/grades - Оценки\n"
                f"/payments - Платежи\n\n"
                f"🚀 Все функции доступны в приложении!"
            )

            from bot.keyboards import get_welcome_keyboard
            await message.reply(parent_text, reply_markup=get_welcome_keyboard())

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in parent command: {e}")
        await message.reply("❌ Произошла ошибка.")


@dp.message_handler(commands=['my_children'])
async def cmd_my_children(message: types.Message):
    """
    Show parent's children.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_parent(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            from models.student import Student

            children = db.query(Student).filter(
                Student.parent_id == message.from_user.id,
                Student.is_active == 1
            ).all()

            if not children:
                await message.reply(
                    "👶 У вас пока нет зарегистрированных детей.\n"
                    "Обратитесь к администратору для добавления."
                )
                return

            children_text = f"👨‍👩‍👧 <b>Ваши дети ({len(children)}):</b>\n\n"

            for child in children:
                group_name = child.group.name if child.group else "Не назначена"
                children_text += (
                    f"👦 <b>{child.full_name}</b>\n"
                    f"   Группа: {group_name}\n"
                    f"   Предмет: {child.group.subject if child.group else 'Не указан'}\n\n"
                )

            await message.reply(children_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in my_children command: {e}")
        await message.reply("❌ Ошибка получения списка детей.")


@dp.message_handler(commands=['attendance'])
async def cmd_attendance(message: types.Message):
    """
    Show attendance summary for children.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_parent(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            from models.student import Student

            children = db.query(Student).filter(
                Student.parent_id == message.from_user.id,
                Student.is_active == 1
            ).all()

            if not children:
                await message.reply("👶 У вас нет зарегистрированных детей.")
                return

            attendance_text = f"📊 <b>Посещаемость детей:</b>\n\n"

            for child in children:
                attendances = child.attendances

                if not attendances:
                    attendance_text += (
                        f"👦 <b>{child.full_name}</b>\n"
                        f"   Посещаемость: Нет данных\n\n"
                    )
                    continue

                present_count = sum(1 for att in attendances if att.status == "PRESENT")
                attendance_percentage = round((present_count / len(attendances)) * 100, 1)

                attendance_text += (
                    f"👦 <b>{child.full_name}</b>\n"
                    f"   Всего занятий: {len(attendances)}\n"
                    f"   Присутствовал: {present_count}\n"
                    f"   Посещаемость: {attendance_percentage}%\n\n"
                )

            await message.reply(attendance_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in attendance command: {e}")
        await message.reply("❌ Ошибка получения посещаемости.")


@dp.message_handler(commands=['grades'])
async def cmd_grades(message: types.Message):
    """
    Show grades summary for children.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_parent(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            from models.student import Student

            children = db.query(Student).filter(
                Student.parent_id == message.from_user.id,
                Student.is_active == 1
            ).all()

            if not children:
                await message.reply("👶 У вас нет зарегистрированных детей.")
                return

            grades_text = f"📊 <b>Оценки детей:</b>\n\n"

            for child in children:
                grades = child.grades

                if not grades:
                    grades_text += (
                        f"👦 <b>{child.full_name}</b>\n"
                        f"   Оценки: Нет данных\n\n"
                    )
                    continue

                average_grade = round(sum(grade.value for grade in grades) / len(grades), 2)
                latest_grades = sorted(grades, key=lambda x: x.date_given, reverse=True)[:3]

                grades_text += (
                    f"👦 <b>{child.full_name}</b>\n"
                    f"   Всего оценок: {len(grades)}\n"
                    f"   Средний балл: {average_grade}\n"
                )

                if latest_grades:
                    grades_text += f"   Последние оценки:\n"
                    for grade in latest_grades:
                        date_str = grade.date_given.strftime("%d.%m")
                        grades_text += f"   • {grade.value} ({grade.type_display}, {date_str})\n"

                grades_text += "\n"

            await message.reply(grades_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in grades command: {e}")
        await message.reply("❌ Ошибка получения оценок.")


@dp.message_handler(commands=['payments'])
async def cmd_payments(message: types.Message):
    """
    Show payment status for children.
    """
    try:
        db: Session = SessionLocal()
        try:
            if not is_parent(message.from_user.id, db):
                await message.reply("❌ Доступ запрещен.")
                return

            from models.student import Student
            from models.payment import Payment
            from datetime import datetime

            children = db.query(Student).filter(
                Student.parent_id == message.from_user.id,
                Student.is_active == 1
            ).all()

            if not children:
                await message.reply("👶 У вас нет зарегистрированных детей.")
                return

            current_date = datetime.now()
            payments_text = f"💰 <b>Статус платежей ({current_date.month}.{current_date.year}):</b>\n\n"

            for child in children:
                # Get current month payment
                payment = db.query(Payment).filter(
                    Payment.student_id == child.id,
                    Payment.month == current_date.month,
                    Payment.year == current_date.year
                ).first()

                group_price = child.group.monthly_price if child.group else 0

                if payment:
                    status_emoji = "✅" if payment.status == "PAID" else "❌"
                    payments_text += (
                        f"👦 <b>{child.full_name}</b>\n"
                        f"   {status_emoji} {payment.status_display}\n"
                        f"   Сумма: {payment.amount} UZS\n\n"
                    )
                else:
                    payments_text += (
                        f"👦 <b>{child.full_name}</b>\n"
                        f"   ❌ Не оплачено\n"
                        f"   Сумма: {group_price} UZS\n\n"
                    )

            await message.reply(payments_text)

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error in payments command: {e}")
        await message.reply("❌ Ошибка получения платежей.")
