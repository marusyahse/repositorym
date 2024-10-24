from aiogram import executor
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

import sqlite3 as sq  # Импортируем SQL

BOT_TOKEN = '7945396651:AAG0UjvVC0holg2wZHvwc-9gvolMCylMSfY'

chat_id = -1002126320637

db = sq.connect("salon1.db")
cur = db.cursor()


async def db_start():  # Создаем таблицы баз данных

    cur.execute("CREATE TABLE IF NOT EXISTS UserInfo("
                "ID INTEGER,"
                "user_name,"
                "Name,"
                "Number)"
                )

    cur.execute("CREATE TABLE IF NOT EXISTS salon_info("
                "Name,"
                "Number,"
                "Adress)"
                )

    cur.execute("CREATE TABLE IF NOT EXISTS about_salon("
                "text,"
                "photo)"
                )

    cur.execute("CREATE TABLE IF NOT EXISTS record_users("
                "ID INTEGER,"
                "user_name,"
                "data,"
                "time,"
                "id_record,"
                "accept)"
                )

    db.commit()


###Add
#добавляем салон в базу данных
def add_name_salon(name, num, adres):
    cur.execute("INSERT INTO salon_info VALUES(?, ?, ?);", (name, num, adres))
    db.commit()

#вставляет инфо о пользвоателях в базу данных
async def Users_Info(tg_ID, firstname, number, username):
    account = cur.execute("SELECT ID FROM UserInfo WHERE ID=?;", [tg_ID]).fetchone()
    if not account:
        cur.execute("INSERT INTO UserInfo VALUES(?, ?, ?, ?);", (tg_ID, username, firstname, number))
        db.commit()

#добвляем текст о нас в базу данных
async def add_text_photo_AboutUs(txt, photo):
    cur.execute("INSERT INTO about_salon VALUES(?, ?);", (txt, photo))
    db.commit()


async def add_record_user(id, username, data, time, id_record):
    cur.execute("INSERT INTO record_users VALUES(?, ?, ?, ?, ?, ?);", (id, username, data, time, id_record, 0))
    db.commit()


###Get - возвращает собранные данные из базы
def get_name_salon():
    name = cur.execute('SELECT Name FROM salon_info').fetchall()
    return name[0][0]


def get_number_salon():
    num = cur.execute('SELECT Number FROM salon_info').fetchall()
    return num[0][0]


def get_adres_salon():
    adres = cur.execute('SELECT Adress FROM salon_info').fetchall()
    return adres[0][0]


def get_aboutus_text():
    txt = cur.execute('SELECT text FROM about_salon').fetchall()
    return txt[0][0]


def get_aboutus_photo():
    p = cur.execute('SELECT photo FROM about_salon').fetchall()
    return p[0][0]


async def get_user_info(id):
    inf = cur.execute('SELECT Name, Number FROM UserInfo WHERE ID = ?;', [id]).fetchall()
    return inf


async def get_user_info_record(rid):
    rinf = cur.execute('SELECT ID, data, time FROM record_users WHERE id_record = ?;', [rid]).fetchall()
    return rinf


async def get_username_ID(id):
    us = cur.execute('SELECT user_name FROM UserInfo WHERE ID = ?', [id]).fetchall()
    return us[0][0]


###обновление информации
async def update_info(why, new_info):
    cur.execute(f"UPDATE salon_info SET {why} = ?",
                [new_info])
    db.commit()


async def update_about_us(text, photo):
    cur.execute(f"UPDATE about_salon SET text = ?, photo = ?", (text, photo))
    db.commit()


async def edit_flag_record(f, id):
    cur.execute(f"UPDATE record_users SET accept = ? WHERE id_record = ?",
                (f, id))
    db.commit()


###Scans - проверяет, есть ли юзер в базе данных
async def scan(user):
    ac = cur.execute("SELECT ID FROM UserInfo WHERE ID=?;", [user]).fetchone()
    if not ac:
        return 0
    else:
        return 1


###Delete

async def delete_record_user(rec_id):
    cur.execute("DELETE FROM record_users WHERE id_record = ?;", [rec_id])
    db.commit()


logging.basicConfig(level=logging.INFO)  # Для запуска бота

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)  # Для запуска бота


async def on_startup(dispatcher):
    await db_start()
    print("База данных загружена")
    # await set_default_commands(dispatcher)
    # await on_startup_notify(dispatcher)


add_about = types.InlineKeyboardMarkup(row_width=2)
b1 = types.InlineKeyboardButton(text="Да", callback_data='addabout|salon|yes')
b2 = types.InlineKeyboardButton(text="Позже", callback_data='addabout|salon|no')  # Кнопочки Inline
add_about.add(b1, b2)

# возвращает клавиатуру для изменения информации о нас для админов
def why_refact_about():
    refact_about = types.InlineKeyboardMarkup(row_width=1)
    b11 = types.InlineKeyboardButton(text="Изменить", callback_data=f'refactorabout|info')  # Кнопочки Inline
    refact_about.add(b11)
    return refact_about


add_name = types.InlineKeyboardMarkup(row_width=2)
b1 = types.InlineKeyboardButton(text="Да", callback_data='addname|salon|yes')
b2 = types.InlineKeyboardButton(text="Позже", callback_data='addname|salon|no')
add_name.add(b1, b2)  # Кнопочки Inline


def why_refact(x):
    refact = types.InlineKeyboardMarkup(row_width=1)
    b11 = types.InlineKeyboardButton(text="Изменить", callback_data=f'refactor|info|{x}')
    refact.add(b11)
    return refact  # Кнопочки Inline


go = types.InlineKeyboardMarkup(row_width=1)
b1 = types.InlineKeyboardButton(text="Вперед!", callback_data="lets|go|record")  # Кнопочки Inline
go.add(b1)


def answer_user(username, id_record):
    ans = types.InlineKeyboardMarkup(row_width=2)
    ans.add(types.InlineKeyboardButton(text="Ответить", url=f'https://t.me/{username}'),
            types.InlineKeyboardButton(text='Отменить', callback_data=f'stop|rec|{id_record}')).add(
        types.InlineKeyboardButton(text='Принять', callback_data=f'accept|rec|{id_record}'))  # Кнопочки Inline

    answer = types.InlineKeyboardMarkup(row_width=1)
    a1 = types.InlineKeyboardButton(text="Ответить", url=f'https://t.me/{username}')
    answer.add(a1)  # Кнопочки Inline

    return [ans, answer]


admin_menu = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text="Информация о салоне")).add(types.KeyboardButton(text="Назад в меню"))

# Кнопочки reply

salon_menu = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text="Название"),
                                                                 types.KeyboardButton(text="Контактный номер"),
                                                                 types.KeyboardButton(text="Адрес")).add(
    types.KeyboardButton(text="О нас (edit)")).add(
    types.KeyboardButton(text="Назад в меню"))

# Кнопочки reply

menu_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Записаться', 'Примеры работ', 'О нас')

back = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Назад в меню')


# Кнопочки reply


@dp.message_handler(Text('О нас'))  # Вывод О НАС по требованию пользователя
async def info_salon(message: types.Message, state: FSMContext):
    try:
        text_about = get_aboutus_text()  # Достаем из базы текст
        photo_about = get_aboutus_photo()  # Достаем из базы фото
        try:
            await bot.send_photo(chat_id=message.chat.id, photo=photo_about, caption=f'{text_about}')
        except:
            pass
    except:
        await message.answer('Упс!\n'
                             'Нет данных.')


class Reg(StatesGroup):
    wait_contact = State()
    wait_name = State()
    wait_username = State()


async def add_user_a_db(ID, contact, name, username):
    await Users_Info(ID, name, contact, username)


@dp.message_handler(commands=['start'])  # Регистрация
async def start(message: types.Message, state: FSMContext):
    if not await scan(message.from_user.id):  # Если такого пользователя нет в базе
        km = types.ReplyKeyboardMarkup(resize_keyboard=True)
        km.add(types.KeyboardButton(text='Подтвердить номер', request_contact=True))  # Подтверждаем номер
        await message.answer(text=f"✂️ Добро пожаловать в {get_name_salon()}!\n"
                                  f"Подтвердите свой номер телефона для дальнейшего использования", reply_markup=km)
        await state.set_state(Reg.wait_contact)
    else:  # Если пользователь есть в базе
        await message.answer(text=f"✂️ Добро пожаловать в {get_name_salon()}! Чем могу помочь?",
                             reply_markup=menu_keyboard)


@dp.message_handler(state=Reg.wait_contact, content_types=['contact'])  # Подтверждаем номер
async def registration(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    username = message.from_user.username

    await state.update_data(phone=phone_number, username=username)
    await message.answer('Напишите ваше имя', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Reg.wait_name)


@dp.message_handler(state=Reg.wait_name)
async def add_name(message: types.Message, state: FSMContext):
    name = message.text
    user_data = await state.get_data()  # Добавляем данные о новом пользователе в базу
    phone_number = user_data.get('phone')
    username = user_data.get('username')

    await add_user_a_db(message.from_user.id, phone_number, name, username)
    await message.answer(text='Вы успешно зарегестрировались!', reply_markup=menu_keyboard)
    await state.finish()


class recordtime(StatesGroup):
    data = State()
    time = State()
    types_work = State()


def is_leap(year) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def check_date(year: int, month: int, day: int) -> bool:  # Функция проверки даты на корректность
    DAYS_MONTH = ('', 31, (28, 29), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    high_border_day = DAYS_MONTH[month] if month != 2 else DAYS_MONTH[2][is_leap(year)]
    return 0 < month < 13 and 0 < day <= high_border_day


def is_valid_time(time_str):  # Функция проверки времени на корректность
    try:
        hours, minutes = map(int, time_str.split(':'))

        if 0 <= hours < 24 and 0 <= minutes < 60:
            return True
        else:
            return False
    except ValueError:
        return False


@dp.message_handler(Text('Записаться'))  # Начать запись по нажатию
async def record(message: types.Message, state: FSMContext):
    await message.answer('Отлично! Я могу помочь вам с этой записью. Пожалуйста, укажите удобное для вас время и дату, '
                         'а также тип услуги. Мы с вами свяжемся', reply_markup=go)


@dp.callback_query_handler(Text(startswith='lets|go'))  # Просьба ввести число (Дату) по определенному формату
async def record_data(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text="На какое число вы хотели бы записаться? (DD.MM.YYYY)📅\n"
                                   "P.S Я очень чувствителен к формату⚙️",
                              reply_markup=back)
    await recordtime.next()


@dp.message_handler(state=recordtime.data)
async def record(message: types.Message, state: FSMContext):
    datatext = message.text
    if datatext == 'Назад в меню':
        await message.answer('Меню', reply_markup=menu_keyboard)
        await state.finish()
    if len(datatext) == 10:
        day_month = datatext[:2]
        month = datatext[3:5]
        year = datatext[6:]
        if check_date(int(year), int(month), int(day_month)):  # Проверка даты на корректность
            recordtime.data = datatext
            await message.answer(text=f"{day_month}:{month}:{year}📅\n"
                                      f"Теперь укажите время в формате HH:MM🕔")  # Дата корректна - идем дальше
            await recordtime.next()
        else:
            await message.answer(text="❌Введите корректную дату")
    else:
        await message.answer(
            text="❌Введите дату по формату. Например 10.03.2024")  # Дата некорректна - просим ввести еще раз


@dp.message_handler(state=recordtime.time)
async def record(message: types.Message, state: FSMContext):
    timetext = message.text

    if len(timetext) == 5:  # Проверка времени на корректность
        if is_valid_time(timetext):
            recordtime.time = timetext
            await message.answer("На какую услугу хотите записаться?")
            await recordtime.next()
        else:
            await message.answer(text="❌Введите корректное время")  # Если время не корректно
    else:
        await message.answer(text="❌Введите время по формату. Например 09:30, 10:05")


@dp.message_handler(state=recordtime.types_work)
async def types_w(message: types.Message, state: FSMContext):
    typ = message.text
    s = await get_user_info(message.from_user.id)
    msg = await message.answer(
        text=f'✅Запись на {recordtime.data} в {recordtime.time} принята\n'  # Время корректно, отправляем запись на рассмотрение
             f'Мы с вами свяжемся в ближайшее время📞\n'
             f'Тип услуги: {typ}',
        reply_markup=menu_keyboard)
    await add_record_user(message.from_user.id, message.from_user.username, recordtime.data,
                                      recordtime.time, msg.message_id)
    await bot.send_message(chat_id=chat_id, text=f"Запись на {recordtime.data} в {recordtime.time}\n"
                                                 f"От {s[0][0]}, контактный номер - {s[0][1]}\n"
                                                 f"Тип услуги: {typ}\n"  # Запись отправляем в группу для работников, где указана вся инфа
                                                 f"Клиент ожидает ответа", reply_markup=answer_user(
        message.from_user.username, msg.message_id)[0])
    await state.finish()


photos = [
    'work_photo/work1.jpg',
    'work_photo/work2.jpg',
    'work_photo/work3.jpg',
    'work_photo/work4.jpg',
]


#      'data/work_photo/work5.jpg',
#      'data/work_photo/work6.jpg',
#      'data/work_photo/work7.jpg',
#      'data/work_photo/work8.jpg',
#      'data/work_photo/work9.jpg',
#      'data/work_photo/work10.jpg'

# Для того что бы добавить еще фото (не больше 10, ограничение ТГ) !!ОБЯЗАТЕЛЬНО!! называть файлы work с цифрой от 1 до 10
# При необходимости, добавть нужный путь к файлу (Указаны выше) в список photos


@dp.message_handler(Text('Примеры работ'))  # Вывод примеров работ по требованию пользователя
async def info_salon(message: types.Message, state: FSMContext):
    try:
        await message.answer("Вдохновляйтесь! 💇‍♀️ Посмотрите фото наших работ и выберите подходящий образ.")
        media = [types.InputMediaPhoto(open(photo, 'rb')) for photo in photos]
        await bot.send_media_group(message.chat.id, media)
    except:
        print("ERROR: Maybe >10 photo")


class about_us_add(StatesGroup):  # Классы для работы с последовательными сообщениями
    text = State()
    photo = State()


class about_us_refact(StatesGroup):
    text = State()
    photo = State()


@dp.message_handler(Text('О нас (edit)'))  # Говорим если нет данных в базе
async def info_salon(message: types.Message, state: FSMContext):
    try:
        text_about = get_aboutus_text()
        photo_about = get_aboutus_photo()
        try:
            await bot.send_photo(chat_id=message.chat.id, photo=photo_about, caption=f'{text_about}',
                                 reply_markup=why_refact_about())
        except:
            pass
    except:
        await message.answer('Упс!\n'
                             'Нет данных. Хотите добавить?', reply_markup=add_about)


@dp.callback_query_handler(Text(startswith='addabout'))  # Меняем фото которое будет в О НАС
async def edit_about(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    cd = call.data.split("|")[-1]
    message_id = call.message.message_id
    if cd == "yes":
        await call.message.answer(f'Введите текст информации')
        await about_us_add().next()
    else:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@dp.message_handler(state=about_us_add.text)
async def edit_about(message: types.Message, state: FSMContext):
    about_us_add.text = message.text
    await message.answer(f'Добавьте фото')
    await about_us_add.next()


@dp.message_handler(state=about_us_add.photo, content_types=['any'])
async def edit_about(message: types.Message, state: FSMContext):
    if message.photo:
        about_us_add.photo = message.photo[0].file_id
        await add_text_photo_AboutUs(about_us_add.text, about_us_add.photo)
        await message.answer("Данные обновлены")
        await state.finish()
    else:
        await message.answer("Добавьте фото")


@dp.callback_query_handler(Text(startswith='refactorabout'))  # Меняем информацию о салоне
async def refact_about(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(f'Введите новый текст информации')
    await about_us_refact().next()


@dp.message_handler(state=about_us_refact.text)
async def edit_about(message: types.Message, state: FSMContext):
    about_us_add.text = message.text
    await message.answer(f'Добавьте новое фото')
    await about_us_refact.next()


@dp.message_handler(state=about_us_refact.photo, content_types=['any'])
async def edit_about(message: types.Message, state: FSMContext):
    if message.photo:
        about_us_add.photo = message.photo[0].file_id
        await update_about_us(about_us_add.text, about_us_add.photo)
        await message.answer("Данные обновлены")
        await state.finish()
    else:
        await message.answer("Добавьте фото")


@dp.message_handler(commands=['admin'])  # Проверка на Админа
async def admin(message: types.Message, state: FSMContext):
    with open('admins.txt', 'r') as f:
        admins = [int(i.replace('\n', '')) for i in f.readlines()]

    if message.from_user.id in admins:
        await message.answer('Админ-панель', reply_markup=admin_menu)


class add_salon(StatesGroup):
    name = State()
    number = State()
    adress = State()


class refact_info_s(StatesGroup):
    name = State()
    number = State()
    address = State()


async def add_name_salon(name, number, adres):
    add_name_salon(name, number, adres)


async def update_info_salon(w, inf):
    await update_info(w, inf)


@dp.message_handler(Text('Информация о салоне'))  # Выводим информацию по запросу
async def info_salon(message: types.Message, state: FSMContext):
    with open('admins.txt', 'r') as f:
        admins = [int(i.replace('\n', '')) for i in f.readlines()]

    if message.from_user.id in admins:
        await message.answer('Информация', reply_markup=salon_menu)


@dp.message_handler(Text('Название'))  # Выводим информацию по запросу
async def info_salon(message: types.Message, state: FSMContext):
    with open('admins.txt', 'r') as f:
        admins = [int(i.replace('\n', '')) for i in f.readlines()]

    if message.from_user.id in admins:
        try:
            await message.answer(f'Текущее название: {get_name_salon()}', reply_markup=why_refact("Name"))
        except:
            await message.answer(f'Упс, нет данных.\n'
                                 f'Хотите добавить?', reply_markup=add_name)


@dp.message_handler(Text('Контактный номер'))  # Выводим информацию по запросу
async def info_salon(message: types.Message, state: FSMContext):
    with open('admins.txt', 'r') as f:
        admins = [int(i.replace('\n', '')) for i in f.readlines()]

    if message.from_user.id in admins:
        try:
            await message.answer(f'Текущий номер: {get_number_salon()}', reply_markup=why_refact("Number"))
        except:
            await message.answer(f'Упс, нет данных.\n'
                                 f'Хотите добавить?', reply_markup=add_name)


@dp.message_handler(Text('Адрес'))  # Выводим информацию по запросу
async def info_salon(message: types.Message, state: FSMContext):
    with open('admins.txt', 'r') as f:
        admins = [int(i.replace('\n', '')) for i in f.readlines()]

    if message.from_user.id in admins:
        try:
            await message.answer(f'Адрес: {get_adres_salon()}', reply_markup=why_refact("Adress"))
        except:
            await message.answer(f'Упс, нет данных.\n'
                                 f'Хотите добавить?', reply_markup=add_name)


@dp.callback_query_handler(Text(startswith='addname'))  # Добавляем информацию (Название салона/Номер/Адрес)
async def edit_info(call: types.CallbackQuery, state: FSMContext):
    cd = call.data.split("|")[-1]
    message_id = call.message.message_id
    if cd == "yes":
        await call.message.answer(f'Введите название')
        await add_salon().next()
    else:
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@dp.message_handler(state=add_salon.name)
async def edit_info(message: types.Message, state: FSMContext):
    add_salon.name = message.text
    await message.answer(f'Введите контактный номер')
    await add_salon.next()


@dp.message_handler(state=add_salon.number)
async def edit_info(message: types.Message, state: FSMContext):
    add_salon.number = message.text
    await message.answer(f'Введите адрес')
    await add_salon.next()


@dp.message_handler(state=add_salon.adress)
async def edit_info(message: types.Message, state: FSMContext):
    add_salon.adress = message.text
    await add_name_salon(add_salon.name, add_salon.number, add_salon.adress)
    await message.answer(f"Информация добавлена")
    await state.finish()


@dp.callback_query_handler(Text(startswith='refactor|info'))  # Изменяем информацию (Название салона/Номер/Адрес)
async def edit_info(call: types.CallbackQuery, state: FSMContext):
    cb = call.data.split("|")[-1]
    if cb == "Name":
        await call.message.answer(f'Введите новое название')
        await state.set_state(refact_info_s.name.state)
    if cb == "Adress":
        await call.message.answer(f'Введите новый адрес')
        await state.set_state(refact_info_s.address.state)
    if cb == "Number":
        await call.message.answer(f'Введите новый номер телефона')
        await state.set_state(refact_info_s.number.state)


@dp.message_handler(state=refact_info_s.name)
async def edit_info(message: types.Message, state: FSMContext):
    await update_info_salon("Name", message.text)
    await message.answer(text="Данные обновлены", reply_markup=salon_menu)
    await state.finish()


@dp.message_handler(state=refact_info_s.number)
async def edit_info(message: types.Message, state: FSMContext):
    await update_info_salon("Number", message.text)
    await message.answer(text="Данные обновлены", reply_markup=salon_menu)
    await state.finish()


@dp.message_handler(state=refact_info_s.address)
async def edit_info(message: types.Message, state: FSMContext):
    await update_info_salon("Adress", message.text)
    await message.answer(text="Данные обновлены", reply_markup=salon_menu)
    await state.finish()


class stop_record(StatesGroup):
    text = State()
    data = State()
    time = State()
    id_us = State()


@dp.callback_query_handler(Text(startswith='accept|rec'))  # Обработка случая с одобрением записи
async def edit_info(call: types.CallbackQuery, state: FSMContext):
    cd = call.data.split('|')[-1]
    await edit_flag_record(1, int(cd))
    info_rec_user = await get_user_info_record(int(cd))
    await bot.send_message(info_rec_user[0][0], text=f"Ваша запись на {info_rec_user[0][1]} {info_rec_user[0][2]} "
                                                     f"одобрена✅\n"
                                                     f"Мы вас ждем по адресу: {get_adres_salon()}⏳\n"
                                                     f"Контактный номер: {get_number_salon()}")
    user_name = await get_username_ID(info_rec_user[0][0])
    await call.message.edit_reply_markup(reply_markup=answer_user(user_name, 0)[1])


@dp.callback_query_handler(
    Text(startswith='stop|rec'))  # Обработка случая с отклонением записи и требованиеем ввести причину
async def edit_info(call: types.CallbackQuery, state: FSMContext):
    cd = call.data.split('|')[-1]
    info_rec_user = await get_user_info_record(int(cd))
    stop_record.id_us = info_rec_user[0][0]
    stop_record.data = info_rec_user[0][1]
    stop_record.time = info_rec_user[0][2]
    await call.message.edit_text(text="Опишите причину отмены")
    await delete_record_user(int(cd))
    await stop_record.next()


@dp.message_handler(state=stop_record.text)  # Обработка случая с отклонением записи
async def add_name(message: types.Message, state: FSMContext):
    stop_record.text = message.text
    await bot.send_message(stop_record.id_us, text=f"Ваша запись на {stop_record.data} {stop_record.time} "
                                                   f"отклонена❌\n"
                                                   f"Причина: {stop_record.text}")
    await state.finish()


@dp.message_handler(Text('Назад в меню'), state='*')  # Для работы кнопки "Назад в меню"
async def menu(message: types.Message, state: FSMContext):
    await message.delete();
    await state.finish()
    await message.answer(text='Меню', reply_markup=menu_keyboard)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)





