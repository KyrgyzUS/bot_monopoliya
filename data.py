import sqlite3

# Создаем соединение с базой данных
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()

# Создаем таблицу с нужными полями
cursor.execute('''
CREATE TABLE IF NOT EXISTS game_data (
    chat_id INTEGER PRIMARY KEY,
    name TEXT,
    money INTEGER,
    turn INTEGER,
    apartments INTEGER,
    round INTEGER,
    room TEXT,
    pole INTEGER,
    role TEXT,
    game_turn INTEGER
)
''')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("База данных и таблица успешно созданы.")
