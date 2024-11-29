import tkinter as tk
from tkcalendar import Calendar
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk  
import sqlite3
from datetime import datetime, timedelta
import babel.numbers

# Функция для очистки виджетов
def clear_widgets(app):
    for widget in app.winfo_children():
        widget.destroy()

# Функция для создания экрана броинрования мест
def create_cinema_booking_screen(app, session_id):
    # Cаоздание списков для изображений мест
    AVAILABLE_IMAGES = []
    BOOKED_IMAGES = []
    SEATS = []

    def book_seat(session_id, seat_number):
        #Добавление пользователя в базу данных
        try:
            cursor.execute("SELECT user_id FROM bookings")
            try:
                user_id = cursor.fetchall()[-1][0]+1
            except IndexError:
                user_id=0
            # Попытка бронирования места
            cursor.execute("INSERT INTO bookings (session_id, user_id, seat_number) VALUES (?, ?, ?)",
                           (session_id, user_id, seat_number))
            conn.commit()
            update_seats(AVAILABLE_IMAGES, BOOKED_IMAGES)
            messagebox.showinfo("Успех", "Место успешно забронировано!")
        except sqlite3.IntegrityError:
            # Ошибка, если место уже забронировано
            messagebox.showerror("Ошибка", "Место уже забронировано. Пожалуйста, выберите другое место.")

    def update_seats(available_images, booked_images):
        # Обновление изображений мест
        cursor.execute("SELECT seat_number FROM bookings WHERE session_id = ?", (session_id,))
        booked_seats = [row[0] for row in cursor.fetchall()]

        for i, seat in enumerate(SEATS):
            seat_number = seat.cget("text")
            if seat_number in booked_seats:
                seat.config(image=booked_images[i % 20])
            else:
                seat.config(image=available_images[i % 20], state="active")

    def create_images():
        # Загрузка изображений для мест
        for i in range(20):
            available_image = tk.PhotoImage(file=f"textures/available_{i}.png")
            AVAILABLE_IMAGES.append(available_image)
            booked_image = tk.PhotoImage(file=f"textures/booked_{i}.png")
            BOOKED_IMAGES.append(booked_image)
        return AVAILABLE_IMAGES, BOOKED_IMAGES

    def create_seats():
        # Создание кнопок для выбора мест
        seats_frame = tk.Frame(app)
        seats_frame.grid(row=0, column=0, padx=200, pady=60)

        for row in range(10):
            for col in range(20):
                seat_number = f"{chr(65 + row)}{col + 1}"
                seat_button = tk.Button(seats_frame, text=seat_number, width=28, height=37,
                                        command=lambda seat=seat_number: book_seat(session_id, seat_number=seat),
                                        takefocus=False)
                seat_button.config(borderwidth=0, highlightthickness=0)
                seat_button.grid(row=row, column=col)
                SEATS.append(seat_button)

    clear_widgets(app)

    # Загрузка фонового изображения и настройка размера окна
    background_image = Image.open("textures/background.png")
    width, height = background_image.size
    app.geometry(f"{width}x{height}")

    # Установка фонового изображения
    background_image = ImageTk.PhotoImage(background_image)
    background_label = tk.Label(app, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Создание кнопки "Назад к выбору сеанса"
    cursor.execute("SELECT movie_id FROM sessions WHERE id=?", (session_id,))
    movie_id = cursor.fetchone()
    back_button = tk.Button(app, text="Назад к выбору сеанса", bg='red', fg='white', font=("futura", 12, "bold"),
                            command=lambda: create_session_selection_screen(app, movie_id[0]))
    back_button.place(x=0, y=0)

    # Создание номера зала 
    cursor.execute("SELECT hall_id FROM sessions WHERE id=?", (session_id,))
    hall_id = cursor.fetchone()
    hall_label = tk.Label(app, text = f"Номер зала - {hall_id[0]}", bg='red', fg='white', font=("futura", 12, "bold"))
    hall_label.place(x=430, y=0)

    exit_button = tk.Button(app, text="Я забронировал билеты, выйти в главное меню", bg='red', fg='white', font=("futura", 10, "bold"),
                            command=lambda: create_movie_selection_screen(app))
    exit_button.place(x=615, y=0)

    create_images()
    create_seats()
    update_seats(AVAILABLE_IMAGES, BOOKED_IMAGES)

    app.mainloop()
    
# Функция для создания экарана выбора сеанса  
def create_session_selection_screen(app, movie_id):
    # Функция для обработки клика на кнопку "Все фильмы"
    def click_handler(event):
        clear_widgets(app)
        create_movie_selection_screen(app)

    # Функция для обновления списка сеансов
    def update_sessions(selected_date, movie_id):
        cursor.execute("SELECT * FROM sessions WHERE movie_id=? AND start_date=?", (movie_id, selected_date))
        selected_sessions = cursor.fetchall()

        # Очищаем сеансы перед обновлением
        for widget in sessions_frame.winfo_children():
            widget.destroy()

        if selected_sessions:
            sessions_label = tk.Label(sessions_frame, text="Доступные сеансы", bg='black', fg='white',  font=("futura", 18, "bold"))
            sessions_label.pack(anchor="nw")
            for session in selected_sessions:
                session_id, movie_id, hall_id, date, time = session
                session_text = f"{date} {time}"
                session_button = tk.Button(sessions_frame, text=session_text, bg='red', fg='white', font=("futura", 14, "bold"), command=lambda id=session_id: create_cinema_booking_screen(app, id))
                session_button.pack(anchor="nw", pady=10, padx=10)

    # Удаление всех виджетов из окна приложения и установка размера окна
    clear_widgets(app)
    app.geometry("1000x1000")
    
    cursor.execute("SELECT * FROM movies WHERE id=?", (movie_id,))
    movie = cursor.fetchone()
 
    movie_id, title, description_path, length, poster_path = movie
    
    # Создаение главного фрейма для всего содержимого
    main_frame = tk.Frame(app, bg='black')
    main_frame.grid(columnspan=2)
    
    # Создание фрейма для постера и его настройки
    poster_frame = tk.Frame(main_frame, bg='black')
    poster_frame.grid(row=0, column=0, padx=10, pady=10)
    
    poster_image = Image.open(poster_path)
    poster_image = poster_image.resize((300, 400))
    poster_image = ImageTk.PhotoImage(poster_image)
        
    poster_label = tk.Label(poster_frame, image=poster_image, bg='black')
    poster_label.image = poster_image
    poster_label.pack()

    # Создание фрейма для описания фильма
    description_frame = tk.Frame(main_frame, bg='black')
    description_frame.grid(row=0, column=1)

    # Создание кнопки "Все фильмы" для возврата на экран выбора фильма
    back_button = tk.Button(description_frame, text="Все фильмы", bg='red', fg='white', font=("futura", 14, "bold"))
    back_button.bind("<Button-1>", click_handler)
    back_button.grid(row=0, column=0, sticky='w', pady=10)
    
    title_label = tk.Label(description_frame, text=title, font=("futura", 18, "bold"), bg='black', fg='white')
    title_label.grid(row=1, column=0, sticky='w')
    
    description_label = tk.Label(description_frame, text="Описание", font=("futura", 14, "bold"), bg='black', fg='white')
    description_label.grid(row=2, column=0, sticky='w')
    
    # Загрузка описание из файла и вставка его в Text
    with open(description_path, 'r', encoding='utf-8') as description_file:
        description_text = tk.Text(description_frame, wrap="word", width=80, height=10, bg='black', fg='white', highlightthickness=0)
        description_text.insert("1.0", description_file.read())
        description_text.grid(row=3, column=0, sticky='nw')
    
    # Создание фрейма для кнопок дат
    date_buttons_frame = tk.Frame(main_frame, bg='black')
    date_buttons_frame.grid(row=2, column=0, sticky='w')

    # Загрузка уникальных дат сеансов для выбранного фильма из базы данных
    cursor.execute("SELECT DISTINCT start_date FROM sessions WHERE movie_id=?", (movie_id,))
    session_dates = cursor.fetchall()
    session_dates = sorted([date[0] for date in session_dates])
    
    # Создание текста "Даты сеансов"
    sessions_label = tk.Label(date_buttons_frame, text="Даты сеансов", bg='black', fg='white',  font=("futura", 18, "bold"))
    sessions_label.grid(row=0, column=0, sticky='w')

    # Создание кнопок с датами
    for i, session_date in enumerate(session_dates):
        date_button = tk.Button(date_buttons_frame, text=session_date, bg='red', fg='white', font=("futura", 14, "bold"), command=lambda d=session_date, id=movie_id: update_sessions(d, id))
        date_button.grid(row=i%3+1, column= i//3, padx=10)

    # Создание фрейма для сеансов
    sessions_frame = tk.Frame(main_frame, bg='black')
    sessions_frame.grid(row=3, column=0, sticky='w')

    update_sessions(session_dates[0], movie_id)

# Функция для создания экрана выбора фильма
def create_movie_selection_screen(app):

    clear_widgets(app)
    # Установка размеров окна на 1000*1000
    app.geometry("1000x1000")
    # Получение списка фильмов из базы данных
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()

    # Создание фрейма для сетки фильмов
    grid_frame = tk.Frame(app, bg='black')
    grid_frame.pack(expand=True, fill='both')

    row, col = 0, 0  # Переменные для позиционирования

    for movie in movies:
        movie_id, title, description, length, poster_path = movie

        # Создание фрейма для каждого фильма
        movie_frame = tk.Frame(grid_frame, bg='black')
        movie_frame.grid(row=row, column=col, padx=5, pady=5)

        # Загрузка и отображение постера фильма
        poster_image = Image.open(poster_path)
        poster_image = poster_image.resize((150, 200))
        poster_image = ImageTk.PhotoImage(poster_image)

        poster_label = tk.Label(movie_frame, image=poster_image, bg='black')
        poster_label.image = poster_image
        poster_label.pack()

        # Отображение названия фильма
        title_label = tk.Label(movie_frame, text=title, font=("futura", 10, "bold"), bg='black', fg='white', wraplength=200, height=3)
        title_label.pack()

        # Функция для обработки клика на постере фильма
        def click_handler(event, id=movie_id):
            create_session_selection_screen(app, id)

        # Привязка функции к событию клика на постере
        poster_label.bind("<Button-1>", click_handler)

        # Обновление позиций в сетке
        col += 1
        if col >= 6:
            col = 0
            row += 1

# Функция для создания экрана выбора интерфейса
def choose_interface(app):
    clear_widgets(app)

    # Создание главного фрейма для интерфейса выбора
    main_frame = tk.Frame(app, bg='black')
    main_frame.place(anchor='c', relx=0.5, rely=0.5)

    # Создание кнопки для интерфейса администратора
    admin_button = tk.Button(main_frame, text="Интерфейс администратора", bg='red', fg='white',
                             font=("futura", 14, "bold"), command=lambda: create_admin_interface(app))
    admin_button.pack(pady=20)

    # Создание кнопки для интерфейса пользователя
    user_button = tk.Button(main_frame, text="Интерфейс пользователя", bg='red', fg='white',
                            font=("futura", 14, "bold"), command=lambda: create_movie_selection_screen(app))
    user_button.pack(pady=20)

# Функция для создания интерфейса администратора
def create_admin_interface(app):
    clear_widgets(app)

    # Создание главного фрейма для интерфейса администратора
    main_frame = tk.Frame(app, bg='black')
    main_frame.place(anchor='c', relx=0.5, rely=0.5)

    # Создание кнопки для добавления фильмов
    admin_button = tk.Button(main_frame, text="Добавить фильм", bg='red', fg='white',
                             font=("futura", 14, "bold"), command=lambda: create_add_movie_screen(app))
    admin_button.pack(pady=20)

    # Создание кнопки для добавления сеансов
    user_button = tk.Button(main_frame, text="Добавить сеанс", bg='red', fg='white',
                            font=("futura", 14, "bold"), command=lambda: create_add_session_screen(app))
    user_button.pack(pady=20)

    # Создание кнопки для удалиения фильмов
    delete_movie_button = tk.Button(main_frame, text="Удалить фильм", bg='red', fg='white',
                             font=("futura", 14, "bold"), command=lambda: delete_movie_interface(app))
    delete_movie_button.pack(pady=20)

    # Кнопка для возвращения назад в выбор интерфейса
    back_button = tk.Button(app, text="Назад к выбору интерфейса", bg='red', fg='white', font=("futura", 12, "bold"),
                            command=lambda: choose_interface(app))
    back_button.place(x=0, y=0)

# Функция для создания формы добавления фильма
def create_add_movie_screen(app):
    clear_widgets(app)

    # Функция для открытия проводника для выбора пути к описанию фильма
    def open_description_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        description_path_var.set(file_path)

    # Функция для открытия проводника для выбора пути к постеру фильма
    def open_poster_file():
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg")])
        poster_path_var.set(file_path)

    # Создание главного фрейма для формы
    main_frame = tk.Frame(app, bg='black')
    main_frame.place(anchor='c', relx=0.5, rely=0.5)

    # Создание названия формы
    add_movie_label = tk.Label(main_frame, text="Добавить фильм", font=("futura", 18, "bold"), bg='black', fg='white')
    add_movie_label.grid(row=0, column=0, columnspan=2, pady=(10, 0))

    # Создание названия поля для ввода названия фильма
    title_label = tk.Label(main_frame, text="Название фильма", bg='black', fg='white')
    title_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    # Создание поля для ввода названия фильма 
    title_entry = tk.Entry(main_frame)
    title_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # Создание названия поля для кнопки пути к описанию фильма
    description_label = tk.Label(main_frame, text="Путь к описанию", bg='black', fg='white')
    description_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    # Специальная переменная для связывания выбранного пути с названием
    description_path_var = tk.StringVar() 
    description_entry = tk.Entry(main_frame, textvariable=description_path_var)
    description_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    # Создание кнопки для вызова проводника для выбора пути к описанию фильма
    description_button = tk.Button(main_frame, text="Обзор", command=open_description_file, bg='red', fg='white')
    description_button.grid(row=3, column=2, padx=10, pady=10)

    # Создание названия поля для ввода длительности фильма
    duration_label = tk.Label(main_frame, text="Длительность фильма (минуты)", bg='black', fg='white')
    duration_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    # Создание поля для ввода длительности фильма 
    duration_entry = tk.Entry(main_frame)
    duration_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    # Создание названия поля для кнопки пути к постеру фильма
    poster_label = tk.Label(main_frame, text="Путь к постеру", bg='black', fg='white')
    poster_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")

    # Специальная переменная для связывания выбранного пути с названием
    poster_path_var = tk.StringVar()
    poster_entry = tk.Entry(main_frame, textvariable=poster_path_var)
    poster_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")

    # Создание кнопки для вызова проводника для выбора пути к постеру фильма
    poster_button = tk.Button(main_frame, text="Обзор", command=open_poster_file, bg='red', fg='white')
    poster_button.grid(row=5, column=2, padx=10, pady=10)

    # Функция для сохранения информации в базе данных
    def save_movie():
        title = title_entry.get()
        description = description_path_var.get()
        duration = duration_entry.get()
        poster = poster_path_var.get()
        cursor.execute("INSERT INTO movies (title, description_path, duration, poster_image_path) VALUES (?, ?, ?, ?)",
                            (title, description, duration, poster))
        conn.commit()
        messagebox.showinfo("Успех", "Фильм успешно добавлен!")

    # Кнопка для сохранения информации в базе данных
    save_button = tk.Button(main_frame, text="Сохранить", command=save_movie, bg='green', fg='white')
    save_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Кнопка для возвращения назад в интерфейс администратора
    back_button = tk.Button(app, text="Назад к интерфейсу администратора", bg='red', fg='white', font=("futura", 12, "bold"),
                            command=lambda: create_admin_interface(app))
    back_button.place(x=0, y=0)

def create_add_session_screen(app):
    clear_widgets(app)

    # Создание главного фрейма для формы
    main_frame = tk.Frame(app, bg='black')
    main_frame.place(anchor='c', relx=0.5, rely=0.5)

    # Создание названия формы
    add_movie_label = tk.Label(main_frame, text="Добавить сеанс", font=("futura", 18, "bold"), bg='black', fg='white')
    add_movie_label.grid(row=0, column=0, columnspan=2, pady=(10, 0))

    # Подгрузка списка фильмов из базы данных
    cursor.execute("SELECT id, title FROM movies")
    movies = cursor.fetchall()
    
    # Выпадающий список названий фильмов
    movie_choice = tk.StringVar()
    movie_choice.set("Выберите фильм")
    movie_option_menu = tk.OptionMenu(main_frame, movie_choice, *[movie[1] for movie in movies])
    movie_option_menu.config(font=("futura", 12, "bold"), bg='red', fg='white')
    movie_option_menu.grid(row=1, column=0, padx=10, pady=10, sticky="w")

    # Создание названия поля для ввода номера зала
    hall_label = tk.Label(main_frame, text="Номер зала", bg='black', fg='white')
    hall_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

    # Создание поля для ввода номера зала
    hall_entry = tk.Entry(main_frame)
    hall_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

    # Создание названия поля для ввода даты показа
    date_label = tk.Label(main_frame, text="Дата показа", bg='black', fg='white')
    date_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    # Создание календаря для ввода даты показа
    date_calendar = Calendar(main_frame, selectmode='day', year=2023, month=10, day=26, locale='ru')
    date_calendar.config(font=("futura", 12, "bold"))
    date_calendar.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    # Создание названия поля для ввода времени показа
    time_label = tk.Label(main_frame, text="Время показа (в формате ЧЧ:ММ)", bg='black', fg='white')
    time_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    # Создание поля для ввода времени показа
    time_entry = tk.Entry(main_frame)
    time_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    # Функция для сохранения информации в базе данных
    def save_session():
        movie_id = [movie_id for movie_id, title in movies if title == movie_choice.get()][0]
        hall_id = hall_entry.get()
        date = date_calendar.get_date()
        # Расчет промежутка времени
        start_time = datetime.strptime(time_entry.get(), "%H:%M")
        cursor.execute("SELECT duration FROM movies WHERE id=?", ([movie_id]))
        minutes_to_add = cursor.fetchone()
        end_time = start_time + timedelta(minutes=minutes_to_add[0])
        time_range = f"{start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"

        cursor.execute("INSERT INTO sessions (movie_id, hall_id, start_date, start_time) VALUES (?, ?, ?, ?)",
            (movie_id, hall_id, date, time_range))
        conn.commit()
        messagebox.showinfo("Успех", "Сеанс успешно добавлен!")
        
    # Кнопка для сохранения информации в базе данных
    save_button = tk.Button(main_frame, text="Сохранить", command=save_session, bg='green', fg='white')
    save_button.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Кнопка для возвращения назад в интерфейс администратора
    back_button = tk.Button(app, text="Назад к интерфейсу администратора", bg='red', fg='white', font=("futura", 12, "bold"),
                            command=lambda: create_admin_interface(app))
    back_button.place(x=0, y=0)

# Функция создания интерфейса для удаления фильмов
def delete_movie_interface(app):
    clear_widgets(app)
    # Функция для удаления выбранного фильма
    def delete_movie():
        selected_movie = movie_choice.get()
        if not selected_movie or selected_movie == "Выберите фильм":
            messagebox.showerror("Ошибка", "Пожалуйста, выберите фильм для удаления.")
            return

        result = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить фильм '{selected_movie}' и все связанные с ним сеансы?")
        if result:
            # Удалить фильм и все связанные с ним сеансы
            cursor.execute('SELECT id FROM movies WHERE title=?', (selected_movie,))
            movie_id = cursor.fetchone()
            cursor.execute("DELETE FROM sessions WHERE movie_id=?", (movie_id[0],))
            cursor.execute("DELETE FROM movies WHERE title=?", (selected_movie,))
            conn.commit()
            messagebox.showinfo("Успех", "Фильм успешно удален.")

    # Создание главного фрейма для формы
    main_frame = tk.Frame(app, bg='black')
    main_frame.place(anchor='c', relx=0.5, rely=0.5)

    # Подгрузка списка фильмов из базы данных
    cursor.execute("SELECT title FROM movies")
    movie_titles = [row[0] for row in cursor.fetchall()]

    # Выпадающий список названий фильмов
    movie_choice = tk.StringVar()
    movie_choice.set("Выберите фильм")
    
    movie_option_menu = tk.OptionMenu(main_frame, movie_choice, *movie_titles)
    movie_option_menu.config(font=("futura", 12, "bold"), bg='red', fg='white')
    movie_option_menu.pack(pady=20)

    # Кнопка "Удалить"
    delete_button = tk.Button(main_frame, text="Удалить", command=delete_movie, bg='red', fg='white')
    delete_button.pack()

    # Кнопка для возвращения назад в интерфейс администратора
    back_button = tk.Button(app, text="Назад к интерфейсу администратора", bg='red', fg='white', font=("futura", 12, "bold"),
                            command=lambda: create_admin_interface(app))
    back_button.place(x=0, y=0)

    
def main():
    app = tk.Tk()
    # Установка фона окна черным
    app.configure(bg='black')

    # Установка размеров окна на 1000*1000
    app.geometry("1000x1000")
    app.title("Бронирование мест в кинотеатре")
    choose_interface(app)
    app.mainloop()
    conn.close()
    

#Подключение к базе данных
conn = sqlite3.connect('cinema_booking.db')
cursor = conn.cursor()

main()