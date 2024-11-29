import sqlite3

# Подключение к базе данных (или создание новой, если её нет)
conn = sqlite3.connect('cinema_booking.db')

# Создание курсора для выполнения SQL-запросов
cursor = conn.cursor()

# Создание таблицы для фильмов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description_path TEXT,
        duration INTEGER,
        poster_image_path TEXT
    )
''')

# Создание таблицы для сеансов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY,
        movie_id INTEGER,
        hall_id INTEGER,
        start_date DATE,
        start_time TIME,
        FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
    )
''')

# Создание таблицы для бронирования мест
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY,
        session_id INTEGER,
        user_id INTEGER,
        seat_number TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
        UNIQUE (session_id, seat_number)
    )
''')

# Изменение формата даты
cursor.execute("SELECT strftime('%d.%m.%Y', start_date) FROM sessions")

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()