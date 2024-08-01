import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Получаем список всех таблиц в базе данных
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Удаляем все данные из всех таблиц
for table in tables:
    table_name = table[0]
    cursor.execute(f"DELETE FROM {table_name}")

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("Все данные из таблиц удалены.")
