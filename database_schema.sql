-- ===========================================
-- SamIT Global - Database Schema
-- ===========================================
-- Полная структура базы данных для импорта в phpMyAdmin
-- Создано для MySQL 8.0+

-- Создание базы данных
CREATE DATABASE IF NOT EXISTS `samit_global` 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE `samit_global`;

-- ===========================================
-- Таблица: users (Пользователи)
-- ===========================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `telegram_id` BIGINT NOT NULL UNIQUE,
    `username` VARCHAR(255) NULL,
    `full_name` VARCHAR(255) NULL,
    `role` VARCHAR(20) NOT NULL DEFAULT 'parent' COMMENT 'admin, teacher, parent',
    `is_active` BOOLEAN DEFAULT TRUE,
    `is_blocked` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_telegram_id` (`telegram_id`),
    INDEX `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- Таблица: teachers (Учителя)
-- ===========================================
CREATE TABLE IF NOT EXISTS `teachers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `first_name` VARCHAR(255) NOT NULL,
    `last_name` VARCHAR(255) NOT NULL,
    `phone` VARCHAR(20) NULL,
    `email` VARCHAR(255) NULL,
    `specialization` VARCHAR(255) NULL COMMENT 'Предмет специализации',
    `experience_years` INT DEFAULT 0,
    `bio` TEXT NULL,
    `is_active` INT DEFAULT 1 COMMENT '1 - active, 0 - inactive',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- Таблица: groups (Группы/Классы)
-- ===========================================
CREATE TABLE IF NOT EXISTS `groups` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL COMMENT 'Название группы (например, "Математика 1А")',
    `subject` VARCHAR(255) NOT NULL COMMENT 'Предмет',
    `teacher_id` INT NOT NULL,
    `monthly_price` DECIMAL(10, 2) NOT NULL DEFAULT 0.00 COMMENT 'Месячная стоимость обучения',
    `schedule` TEXT NULL COMMENT 'Расписание занятий',
    `description` TEXT NULL,
    `max_students` INT DEFAULT 30 COMMENT 'Максимальное количество учеников',
    `is_active` INT DEFAULT 1 COMMENT '1 - active, 0 - inactive',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`) ON DELETE RESTRICT,
    INDEX `idx_teacher_id` (`teacher_id`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- Таблица: students (Ученики)
-- ===========================================
CREATE TABLE IF NOT EXISTS `students` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `first_name` VARCHAR(255) NOT NULL,
    `last_name` VARCHAR(255) NOT NULL,
    `date_of_birth` DATETIME NULL,
    `parent_id` INT NOT NULL,
    `group_id` INT NOT NULL,
    `phone` VARCHAR(20) NULL,
    `address` TEXT NULL,
    `notes` TEXT NULL,
    `is_active` INT DEFAULT 1 COMMENT '1 - active, 0 - inactive',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`parent_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE RESTRICT,
    INDEX `idx_parent_id` (`parent_id`),
    INDEX `idx_group_id` (`group_id`),
    INDEX `idx_is_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- Таблица: attendance (Посещаемость)
-- ===========================================
CREATE TABLE IF NOT EXISTS `attendance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `group_id` INT NOT NULL,
    `date` DATETIME NOT NULL COMMENT 'Дата занятия',
    `status` VARCHAR(20) NOT NULL COMMENT 'PRESENT, ABSENT, LATE',
    `notes` TEXT NULL COMMENT 'Примечания (опоздание на 15 мин и т.д.)',
    `marked_by` INT NOT NULL COMMENT 'Кто отметил (teacher user_id)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`marked_by`) REFERENCES `users`(`id`) ON DELETE RESTRICT,
    INDEX `idx_student_id` (`student_id`),
    INDEX `idx_group_id` (`group_id`),
    INDEX `idx_date` (`date`),
    INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- Таблица: grades (Оценки)
-- ===========================================
CREATE TABLE IF NOT EXISTS `grades` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `group_id` INT NOT NULL,
    `value` DECIMAL(3, 1) NOT NULL COMMENT 'Оценка (5.0, 4.5, etc.)',
    `max_value` DECIMAL(3, 1) DEFAULT 5.0 COMMENT 'Максимальная оценка (обычно 5.0)',
    `type` VARCHAR(50) NOT NULL COMMENT 'exam, homework, test, quiz, etc.',
    `title` VARCHAR(255) NULL COMMENT 'Название работы/теста',
    `description` TEXT NULL COMMENT 'Описание задания',
    `comment` TEXT NULL COMMENT 'Комментарий преподавателя',
    `date_given` DATETIME NOT NULL COMMENT 'Дата выставления оценки',
    `given_by` INT NOT NULL COMMENT 'Кто выставил (teacher user_id)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`given_by`) REFERENCES `users`(`id`) ON DELETE RESTRICT,
    INDEX `idx_student_id` (`student_id`),
    INDEX `idx_group_id` (`group_id`),
    INDEX `idx_date_given` (`date_given`),
    INDEX `idx_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- Таблица: payments (Платежи)
-- ===========================================
CREATE TABLE IF NOT EXISTS `payments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT NOT NULL,
    `group_id` INT NOT NULL,
    `amount` DECIMAL(10, 2) NOT NULL COMMENT 'Сумма платежа',
    `currency` VARCHAR(10) DEFAULT 'UZS' COMMENT 'Валюта',
    `month` INT NOT NULL COMMENT 'Месяц (1-12)',
    `year` INT NOT NULL COMMENT 'Год',
    `status` VARCHAR(20) NOT NULL DEFAULT 'UNPAID' COMMENT 'PAID, UNPAID, OVERDUE',
    `payment_date` DATETIME NULL COMMENT 'Дата оплаты',
    `due_date` DATETIME NULL COMMENT 'Срок оплаты',
    `notes` TEXT NULL COMMENT 'Примечания',
    `processed_by` INT NULL COMMENT 'Кто обработал платеж',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`processed_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_student_id` (`student_id`),
    INDEX `idx_group_id` (`group_id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_month_year` (`month`, `year`),
    INDEX `idx_due_date` (`due_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- Таблица: schedules (Расписание)
-- ===========================================
CREATE TABLE IF NOT EXISTS `schedules` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `group_id` INT NOT NULL,
    `day_of_week` INT NOT NULL COMMENT '0-6 (Sunday-Saturday)',
    `start_time` TIME NOT NULL COMMENT 'Время начала занятия',
    `end_time` TIME NOT NULL COMMENT 'Время окончания занятия',
    `subject` VARCHAR(255) NOT NULL COMMENT 'Предмет',
    `teacher_id` INT NOT NULL,
    `room` VARCHAR(50) NULL COMMENT 'Кабинет',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NULL ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`group_id`) REFERENCES `groups`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`teacher_id`) REFERENCES `teachers`(`id`) ON DELETE RESTRICT,
    INDEX `idx_group_id` (`group_id`),
    INDEX `idx_teacher_id` (`teacher_id`),
    INDEX `idx_day_of_week` (`day_of_week`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- Тестовые данные (опционально)
-- ===========================================

-- Вставка тестового администратора
INSERT INTO `users` (`telegram_id`, `username`, `full_name`, `role`, `is_active`) 
VALUES (123456789, 'admin', 'Администратор', 'admin', TRUE)
ON DUPLICATE KEY UPDATE `username` = `username`;

-- Вставка тестового учителя
INSERT INTO `users` (`telegram_id`, `username`, `full_name`, `role`, `is_active`) 
VALUES (987654321, 'teacher1', 'Учитель Тестовый', 'teacher', TRUE)
ON DUPLICATE KEY UPDATE `username` = `username`;

-- Вставка тестового родителя
INSERT INTO `users` (`telegram_id`, `username`, `full_name`, `role`, `is_active`) 
VALUES (111222333, 'parent1', 'Родитель Тестовый', 'parent', TRUE)
ON DUPLICATE KEY UPDATE `username` = `username`;

-- ===========================================
-- Завершение
-- ===========================================
-- База данных создана успешно!
-- Все таблицы готовы к использованию.

