import sqlite3
from functools import wraps

nameDB = 'test.db'

def with_database():
  """
  Декоратор для выполнения SQL-запросов к базе данных SQLite.
  Функция должна возвращать кортеж (sql_query, params).
  """
  def decorator(func):
      @wraps(func)
      def wrapper(*args, **kwargs):
          # Создание соединения с базой данных
          conn = sqlite3.connect(nameDB)
          cursor = conn.cursor()

          try:
              # Вызов функции для получения SQL-запроса и параметров
              sql_query, params = func(*args, **kwargs)

              # Выполнение SQL-запроса
              cursor.execute(sql_query, params)

              # Сохранение изменений
              conn.commit()

              # Возврат результата (если есть)
              if 'SELECT' in sql_query.upper():
                  return cursor.fetchall()  # Для SELECT-запросов возвращаем данные
              elif 'INSERT' in sql_query.upper():
                return cursor.lastrowid  # Для INSERT-запросов возвращаем ID созданной записи
              else:
                  return f"Запрос выполнен: {sql_query}"

          except Exception as e:
              # Откат изменений в случае ошибки
              conn.rollback()
              print(e)
          finally:
              # Закрытие соединения
              cursor.close()
              conn.close()

      return wrapper
  return decorator
