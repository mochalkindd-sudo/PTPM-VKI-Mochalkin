import os
import sys
import re
import hashlib
import logging
from typing import Tuple

# Черный список системных и запрещенных логинов
LOGIN_BLACKLIST = {
    "admin", "administrator", "root", "moderator",
    "support", "guest", "superuser", "system", "owner"
}

# Допустимые спецсимволы
SPECIAL_CHARS = r"!@#$%^&*()_\-+=\[\]{};':\"\\|,.<>\/?~`"


def setup_logger() -> None:
    """Настройка логирования одновременно в консоль и в файл."""
    os.makedirs("logs", exist_ok=True)

    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    # Логирование в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Логирование в файл
    file_handler = logging.FileHandler("logs/file_txt.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")


def mask_password(password: str) -> str:
    """
    Маскирует пароль: одинаковые пароли дают одинаковый хеш,
    разные — разный. Сам пароль в логи не попадает.
    """
    if not isinstance(password, str):
        return "***[INVALID_TYPE]***"
    salt = "vki_ptpm_salt_"
    pwd_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()[:8]
    return f"***[{pwd_hash}]***"


def is_valid_phone(login: str) -> bool:
    """Проверка формата телефона: +x-xxx-xxx-xxxx"""
    return bool(re.fullmatch(r"^\+\d-\d{3}-\d{3}-\d{4}$", login))


def is_valid_email(login: str) -> bool:
    """Проверка стандартной маски email."""
    return bool(re.fullmatch(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", login))


def is_valid_string_login(login: str) -> bool:
    """Строка: минимум 5 символов, только латиница, цифры и знак подчеркивания."""
    return bool(re.fullmatch(r"^[a-zA-Z0-9_]{5,}$", login))


def validate_registration(login: str, password: str, confirm_password: str) -> Tuple[str, str]:
    """Комплексная валидация учетных данных."""
    masked_pwd = mask_password(password)
    masked_confirm = mask_password(confirm_password)

    logging.debug(
        f"Старт валидации: login='{login}', password={masked_pwd}, confirm_password={masked_confirm}"
    )

    try:
        # 1. Проверка типов
        if not isinstance(login, str) or not isinstance(password, str) or not isinstance(confirm_password, str):
            msg = "Некорректный тип данных: все аргументы должны быть строками."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 2. Проверка логина на пустоту
        if len(login.strip()) == 0:
            msg = "Логин не может быть пустым."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 3. Черный список
        if login.lower() in LOGIN_BLACKLIST:
            msg = "Логин запрещен: имя содержится в черном списке системы."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 4. Проверка масок логина
        if not (is_valid_phone(login) or is_valid_email(login) or is_valid_string_login(login)):
            if len(login) < 5 and not ("@" in login or login.startswith("+")):
                msg = "Строковый логин должен содержать не менее 5 символов."
            else:
                msg = "Некорректный формат логина (ожидается email, телефон +x-xxx-xxx-xxxx или латиница/цифры/_)."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 5. Совпадение паролей
        if password != confirm_password:
            msg = "Пароль и подтверждение пароля не совпадают."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 6. Длина пароля
        if len(password) < 7:
            msg = "Длина пароля должна быть не менее 7 символов."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 7. Алфавит пароля: только кириллица, цифры и спецсимволы (без латиницы)
        if not re.fullmatch(rf"^[а-яА-ЯёЁ0-9{SPECIAL_CHARS}]+$", password):
            msg = "Пароль может содержать только кириллицу, цифры и спецсимволы (латиница запрещена)."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 8. Заглавная буква кириллицы
        if not re.search(r"[А-ЯЁ]", password):
            msg = "Пароль должен содержать минимум одну заглавную букву кириллицы."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 9. Строчная буква кириллицы
        if not re.search(r"[а-яё]", password):
            msg = "Пароль должен содержать минимум одну строчную букву кириллицы."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 10. Цифра
        if not re.search(r"\d", password):
            msg = "Пароль должен содержать минимум одну цифру."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # 11. Спецсимвол
        if not re.search(rf"[{SPECIAL_CHARS}]", password):
            msg = "Пароль должен содержать минимум один специальный символ."
            logging.warning(f"Ошибка валидации: {msg}")
            return "False", msg

        # Успех
        logging.info(f"Успешная регистрация: login='{login}', password={masked_pwd}, результат=True")
        return "True", ""

    except Exception as ex:
        logging.error("Непредвиденный сбой в процессе валидации.")
        logging.exception(f"Traceback: {ex}")
        return "False", f"Критическая ошибка: {str(ex)}"


def main() -> None:
    setup_logger()

    test_cases = [
        ("student_vki", "Пароль123!", "Пароль123!"),       # Успех
        ("+7-999-123-4567", "Привет2026#", "Привет2026#"),  # Успех (телефон)
        ("user@domain.com", "Секрет_99", "Секрет_99"),      # Успех (почта)
        ("", "Пароль123!", "Пароль123!"),                   # Ошибка: пустой логин
        ("admin", "Пароль123!", "Пароль123!"),              # Ошибка: черный список
        ("dev", "Пароль123!", "Пароль123!"),                # Ошибка: < 5 символов
        ("student_vki", "Пароль123!", "Пароль123?"),        # Ошибка: пароли не совпали
        ("student_vki", "Па1!", "Па1!"),                    # Ошибка: длина < 7
        ("student_vki", "Password123!", "Password123!"),    # Ошибка: латиница
        ("student_vki", "пароль123!", "пароль123!"),        # Ошибка: нет заглавной
        ("student_vki", "ПАРОЛЬ123!", "ПАРОЛЬ123!"),        # Ошибка: нет строчной
        ("student_vki", "Парольчик!", "Парольчик!"),        # Ошибка: нет цифры
        ("student_vki", "Пароль1234", "Пароль1234"),        # Ошибка: нет спецсимвола
    ]

    print("\n" + "=" * 50)
    print("РЕЗУЛЬТАТЫ ПРОВЕРОК:")
    print("=" * 50)

    for idx, (login, pwd, confirm) in enumerate(test_cases, start=1):
        status, msg = validate_registration(login, pwd, confirm)
        print(f"Тест #{idx:02d} -> Успех: {status} | Причина: '{msg}'")


if __name__ == "__main__":
    main()
