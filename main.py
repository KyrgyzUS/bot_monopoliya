import random
from aiogram.types.web_app_info import WebAppInfo
def generate_unique_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

import json
import string
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

# Инициализация бота
bot = Bot(token='7220960522:AAEwBksKJJCUm1vSPwJOcxI-KDOBlPaw__w')
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Создаем состояние для ожидания ввода суммы
class TransferState(StatesGroup):
    waiting_for_money_amount = State()

class TransferState2(StatesGroup):
    waiting_for_money_amount2 = State()

class TransferState3(StatesGroup):
     waiting_for_money_amount3 = State()


class TransferState4(StatesGroup):
    waiting_for_money_amount4 = State()

# Состояния для машины состояний
class Form(StatesGroup):
    name = State()
    enter_room = State()
    throwing_bones = State()
# Создаем соединение с базой данных и таблицу, если ее нет
conn = sqlite3.connect('game_database.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS game_data (
    chat_id INTEGER PRIMARY KEY,
    name TEXT,
    money INTEGER,
    turn INTEGER,
    apartments TEXT,
    round INTEGER,
    room TEXT,
    pole TEXT,
    role TEXT,
    game_turn INTEGER
)
''')
conn.commit()

# Обработчик команды /start
@dp.message(Command(commands=["start"]))
async def start(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ваше имя:")
    await state.set_state(Form.name)
    # Создание кнопки с WebApp
    button = types.KeyboardButton(text='kosti', web_app=WebAppInfo(url="https://kyrgyzus.github.io/web_cubick/"))
    button1 = types.KeyboardButton(text='/menu')
    # Создание клавиатуры и добавление кнопки
    markup = types.ReplyKeyboardMarkup(keyboard=[[button], [button1]], resize_keyboard=True)
    await message.answer("knopki dlya kubikov i menu vnizu", reply_markup=markup)

# Обработчик ввода имени
@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    chat_id = message.chat.id
    name = message.text

    cursor.execute('INSERT OR IGNORE INTO game_data (chat_id, name, money, turn, apartments, round, room, pole, role, game_turn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (chat_id, name, 0, 0, -1, 0, 'None', 'None', 'None', 0))
    cursor.execute('UPDATE game_data SET name = ? WHERE chat_id = ?', (name, chat_id))
    conn.commit()

    button1 = types.InlineKeyboardButton(text='Start game', callback_data='start_game')
    button2 = types.InlineKeyboardButton(text='Enter to game', callback_data='enter_game')
    markup_start = types.InlineKeyboardMarkup(inline_keyboard=[[button1], [button2]])

    await message.answer(f"Привет, {name}! Что вы хотите сделать?", reply_markup=markup_start)
    await state.clear()


# Обработчик callback-запроса для начала игры
@dp.callback_query(F.data == 'start_game')
async def process_start_game(callback_query: CallbackQuery):
    chat_id = callback_query.from_user.id
    unique_code = generate_unique_code()

    cursor.execute('UPDATE game_data SET room = ?, role = ?, apartments = ? WHERE chat_id = ?',
                   (unique_code, 'owner', -1, chat_id))
    conn.commit()

    await callback_query.answer(f"Ваш номер комнаты: {unique_code}. Используйте этот код, чтобы пригласить друзей!")

    button = types.InlineKeyboardButton(text="Let's play", callback_data='lets_play')
    markup = types.InlineKeyboardMarkup(inline_keyboard=[[button]])

    await bot.send_message(chat_id, f"Ваш номер комнаты: {unique_code}. Используйте этот код, чтобы пригласить друзей!",
                           reply_markup=markup)


# Обработчик callback-запроса для кнопки "Let's play"
@dp.callback_query(lambda c: c.data == 'lets_play')
async def process_lets_play(callback_query: CallbackQuery):
    chat_id = callback_query.from_user.id

    # Получаем код комнаты пользователя
    cursor.execute('SELECT room FROM game_data WHERE chat_id = ?', (chat_id,))
    room_code = cursor.fetchone()

    if not room_code:
        await callback_query.answer("Вы не в комнате.")
        return

    room_code = room_code[0]

    # Получаем список всех участников комнаты
    cursor.execute('SELECT chat_id FROM game_data WHERE room = ?', (room_code,))
    players_in_room = cursor.fetchall()

    # Устанавливаем apartments = 2 для всех игроков в комнате
    cursor.execute('UPDATE game_data SET apartments = 2 WHERE room = ?', (room_code,))
    conn.commit()

    # Генерируем уникальные номера для игроков
    player_ids = [player[0] for player in players_in_room]
    random.shuffle(player_ids)  # Перемешиваем список chat_id для случайного назначения номеров


    # Отправляем сообщение о начале игры и меню с кнопками
    button1 = types.InlineKeyboardButton(text='Send money', callback_data='send_money')
    button2 = types.InlineKeyboardButton(text='Pay to bank', callback_data='pay_to_bank')
    button3 = types.InlineKeyboardButton(text='Take from bank', callback_data='take_from_bank')
    button4 = types.InlineKeyboardButton(text='pay to exit from prison', callback_data='let_me_out')
    button6 = types.InlineKeyboardButton(text='Баланс', callback_data='balance')
    button5 = types.InlineKeyboardButton(text= 'Cancel the game', callback_data='cancel_the_game')
    markup_start = types.InlineKeyboardMarkup(inline_keyboard=[[button1], [button2], [button3], [button4], [button6]])
    markup_end = types.InlineKeyboardMarkup(inline_keyboard = [[button5]])
    # Отправляем сообщение каждому игроку с уникальным номером
    for idx, player_chat_id in enumerate(player_ids, start=1):
        try:
            if idx == 1:
                await bot.send_message(player_chat_id, f"Ваш номер в игре: {idx}. Бросайте кости!", reply_markup=markup_start)

                cursor.execute('UPDATE game_data SET turn = ? WHERE chat_id = ?', (idx ,player_chat_id,))
                conn.commit()
            else:
                await bot.send_message(player_chat_id, f"Ваш номер в игре: {idx}. Wait 1st will trow his cubes", reply_markup=markup_start)

                cursor.execute('UPDATE game_data SET turn = ? WHERE chat_id = ?', (idx, player_chat_id,))
                conn.commit()
        except Exception as e:
            print(f"Не удалось отправить сообщение игроку {player_chat_id}: {e}")

    # Обновляем сообщение для удаления кнопки "Let's play"
    try:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Игра начинается! Выберите действие:",
            reply_markup = markup_end
        )
    except Exception as e:
        print(f"Не удалось обновить сообщение: {e}")

    # Обновляем значения полей для всех игроков в комнате
    cursor.execute('UPDATE game_data SET pole = 0, game_turn = 1, round = 0, money = 0 WHERE room = ?', (room_code,))
    conn.commit()

    await callback_query.answer("Игра начинается. Проверьте свои сообщения.")


# Обработчик callback-запроса для кнопки "Enter to game"
@dp.callback_query(F.data == 'enter_game')
async def enter_game(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите код комнаты:")
    await state.set_state(Form.enter_room)


@dp.message(Form.enter_room)
async def process_enter_room(message: Message, state: FSMContext):
    chat_id = message.chat.id

    room_code = (message.text.strip()).upper()

    # Проверяем, находится ли пользователь уже в комнате
    cursor.execute('SELECT room FROM game_data WHERE chat_id = ?', (chat_id,))
    current_room = cursor.fetchone()

    if current_room:
        if current_room[0] == room_code:
            await message.answer("Вы уже находитесь в этой комнате.")
            await state.clear()
            return

    # Проверяем, существует ли комната с таким кодом
    cursor.execute('SELECT chat_id FROM game_data WHERE room = ?', (room_code,))
    room_owner = cursor.fetchone()

    if room_owner:
        # Получаем все значения поля apartments для игроков в комнате
        cursor.execute('SELECT apartments FROM game_data WHERE room = ?', (room_code,))
        apartments_list = cursor.fetchall()

        # Проверяем условие: все значения apartments должны быть больше чем -1
        if all(int(apartment[0]) < 0 for apartment in apartments_list):
            # Обновляем запись пользователя, чтобы присоединить его к этой комнате
            cursor.execute('UPDATE game_data SET room = ?, role = ?, apartments = ? WHERE chat_id = ?',
                           (room_code, 'player', -1, chat_id))
            conn.commit()
            await message.answer(f"Вы присоединились к комнате {room_code}.")

            # Получаем имя текущего пользователя
            cursor.execute('SELECT name FROM game_data WHERE chat_id = ?', (chat_id,))
            player_name = cursor.fetchone()[0]

            # Получаем список всех участников комнаты
            cursor.execute('SELECT chat_id FROM game_data WHERE room = ?', (room_code,))
            players_in_room = cursor.fetchall()

            # Отправляем сообщение всем участникам комнаты
            for player in players_in_room:
                if player[0] != chat_id:  # Не отправляем сообщение текущему пользователю
                    try:
                        await bot.send_message(player[0], f"Игрок {player_name} присоединился к комнате {room_code}.")
                    except Exception as e:
                        print(f"Не удалось отправить сообщение игроку {player[0]}: {e}")
        else:
            await message.answer("В этой комнате слишком много игроков или условия не выполнены. Попробуйте снова.")

    else:
        await message.answer("Комнаты с таким кодом не существует, попробуйте снова.")

    await state.clear()

# Обработчик сообщений с типом 'web_app_data'
@dp.message(lambda message: message.web_app_data is not None)
async def web_app(message: Message):
    try:
        data = message.web_app_data.data
        chat_id = message.chat.id
        chat_id_sp = chat_id

        cursor.execute('SELECT turn FROM game_data WHERE chat_id = ?', (chat_id,))
        player_turn = cursor.fetchone()[0]

        cursor.execute('SELECT name FROM game_data WHERE chat_id = ?', (chat_id,))
        name = cursor.fetchone()[0]

        # Получаем код комнаты пользователя
        cursor.execute('SELECT room FROM game_data WHERE chat_id = ?', (chat_id,))
        room_code = cursor.fetchone()[0]

        cursor.execute('SELECT game_turn FROM game_data WHERE room = ?', (room_code,))
        turn = cursor.fetchone()[0]

        cursor.execute('SELECT chat_id FROM game_data WHERE room = ?', (room_code,))
        players_in_room = cursor.fetchall()

        res = json.loads(data)
        response_text = res.get('n1','n2')
        result = int(res['n1']) + int(res['n2'])

        cursor.execute('SELECT apartments FROM game_data WHERE chat_id = ?', (chat_id_sp,))
        stat = int(cursor.fetchone()[0])

        cursor.execute('SELECT pole FROM game_data WHERE chat_id = ?', (chat_id_sp,))
        pole = int(cursor.fetchone()[0])

        refresh_turn = len(players_in_room)
        cursor.execute('SELECT round FROM game_data WHERE chat_id = ?', (chat_id_sp,))
        new_round = int(cursor.fetchone()[0])

        if player_turn == turn:
            for player in players_in_room:
                chat_id = player[0]
                await bot.send_message(chat_id, f"{name} has {result}. Turn: {turn}")
            if res['n1'] == res['n2']:
                if stat == 3:
                    for player in players_in_room:
                        chat_id = player[0]
                        await bot.send_message(chat_id, f"Dude! {name}, you are lucky today, go out from prison!")
                        cursor.execute('UPDATE game_data SET apartments = ? WHERE chat_id = ?',(2, chat_id_sp,))
                        conn.commit()
                pole += result
                if pole >= 40:
                    new_round += 1
                    pole -= 40
                    cursor.execute('UPDATE game_data SET round = ?, pole = ? WHERE chat_id = ?', (new_round, pole, chat_id_sp,))
                    conn.commit()
                    for player in players_in_room:
                        chat_id = player[0]
                        await bot.send_message(chat_id, f"{name} take your money from bank!")
                if pole == 10 or pole == 30:
                    for player in players_in_room:
                        chat_id = player[0]
                        await bot.send_message(chat_id, f"OH, look's like Prison")
                        cursor.execute('UPDATE game_data SET apartments = ? WHERE chat_id = ?', (3, chat_id_sp,))
                        conn.commit()
                cursor.execute('UPDATE game_data SET pole = ? WHERE chat_id = ?', (pole, chat_id_sp,))
                conn.commit()
                for player in players_in_room:
                    chat_id = player[0]
                    await bot.send_message(chat_id, f"Double! {name} can throw again.")
            else:
                if refresh_turn == turn:
                    turn = 1
                else:
                    turn += 1
                cursor.execute('UPDATE game_data SET game_turn = ? WHERE room = ?', (turn, room_code,))
                conn.commit()
                if stat == 3:
                    for player in players_in_room:
                        chat_id = player[0]
                        await bot.send_message(chat_id, f"Dude! {name}, you are not lucky today, but our prison is great!")
                        cursor.execute('UPDATE game_data SET apartments = ? WHERE chat_id = ?',(2, chat_id_sp,))
                        conn.commit()
                else:
                    pole += result
                    cursor.execute('UPDATE game_data SET pole = ? WHERE chat_id = ?', (pole, chat_id_sp,))
                    conn.commit()
                    if pole >= 40:
                        new_round += 1
                        pole -= 40
                        cursor.execute('UPDATE game_data SET round = ?, pole = ? WHERE chat_id = ?', (new_round, pole, chat_id_sp,))
                        conn.commit()
                        for player in players_in_room:
                            chat_id = player[0]
                            await bot.send_message(chat_id, f"{name} take your money from bank!")
                    if pole == 10 or pole == 30:
                        for player in players_in_room:
                            chat_id = player[0]
                            await bot.send_message(chat_id, f"OH, look's like Prison")
                            cursor.execute('UPDATE game_data SET apartments = ? WHERE chat_id = ?', (3, chat_id_sp,))
                            conn.commit()
                    for player in players_in_room:
                        chat_id = player[0]
                        await bot.send_message(chat_id, f"Now turn: {turn}")
        else:
            for player in players_in_room:
                chat_id = player[0]
                await bot.send_message(chat_id, f"{name} is chort, cheater, tried to throw not in their turn.")
    except Exception as e:
        await message.answer(f"An error occurred: {e}")
        print(f"An error occurred: {e}")



# Обработчик callback-запроса для кнопки "send money"
@dp.callback_query(lambda c: c.data == 'send_money')
async def send_money(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id

    # Получаем код комнаты пользователя
    cursor.execute('SELECT room FROM game_data WHERE chat_id = ?', (chat_id,))
    room_code = cursor.fetchone()[0]

    # Получаем список игроков в комнате
    cursor.execute('SELECT chat_id, name FROM game_data WHERE room = ?', (room_code,))
    players_in_room = cursor.fetchall()

    # Генерируем кнопки с именами игроков
    builder = InlineKeyboardBuilder()
    for player in players_in_room:
        if player[0] != chat_id:
            builder.button(text=player[1], callback_data=f"send_money_to_{player[0]}")

    await callback_query.message.answer("Выберите, кому перевести деньги:", reply_markup=builder.as_markup())

# Обработчик выбора игрока для перевода денег
@dp.callback_query(lambda c: c.data.startswith("send_money_to_"))
async def process_send_money(callback_query: CallbackQuery, state: FSMContext):
    sender_id = callback_query.from_user.id
    receiver_id = int(callback_query.data.split("_")[-1])

    # Сохраняем ID получателя в состоянии
    await state.update_data(receiver_id=receiver_id)
    await state.set_state(TransferState.waiting_for_money_amount)

    await bot.send_message(sender_id, text="Введите сумму для перевода:")

# Обработчик ввода суммы
@dp.message(TransferState.waiting_for_money_amount)
async def process_money_amount(message: types.Message, state: FSMContext):
    sender_id = message.from_user.id
    amount = int(message.text.strip())

    # Получаем баланс отправителя
    cursor.execute('SELECT money FROM game_data WHERE chat_id = ?', (sender_id,))
    sender_balance = cursor.fetchone()[0]

    # Проверяем, хватает ли средств для перевода
    if sender_balance < amount:
        await message.answer(f"У вас недостаточно средств для перевода. Пожалуйста, введите другую сумму under {sender_balance}.")
        return

    data = await state.get_data()
    receiver_id = data['receiver_id']

    # Обновляем баланс отправителя
    cursor.execute('UPDATE game_data SET money = money - ? WHERE chat_id = ?', (amount, sender_id))
    # Обновляем баланс получателя
    cursor.execute('UPDATE game_data SET money = money + ? WHERE chat_id = ?', (amount, receiver_id))
    conn.commit()

    # Получаем имена отправителя и получателя для уведомления
    cursor.execute('SELECT name FROM game_data WHERE chat_id = ?', (sender_id,))
    sender_name = cursor.fetchone()[0]
    cursor.execute('SELECT name FROM game_data WHERE chat_id = ?', (receiver_id,))
    receiver_name = cursor.fetchone()[0]

    await message.answer(f"Вы успешно перевели {amount} единиц игроку {receiver_name}.")
    await bot.send_message(receiver_id, f"Игрок {sender_name} перевел вам {amount} единиц.")

    # Очищаем состояние
    await state.clear()


# Обработчик callback-запроса для кнопки "Take from bank"
@dp.callback_query(lambda c: c.data == 'take_from_bank')
async def take_from_bank(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id

    # Сохраняем состояние ожидания суммы
    await state.set_state(TransferState2.waiting_for_money_amount2)

    await callback_query.message.answer("Введите сумму, которую хотите взять из банка:")


# Обработчик ввода суммы
@dp.message(TransferState2.waiting_for_money_amount2)
async def process_take_from_bank(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    amount = int(message.text.strip())

    # Обновляем баланс игрока
    cursor.execute('UPDATE game_data SET money = money + ? WHERE chat_id = ?', (amount, chat_id))
    conn.commit()

    # Получаем имя игрока для уведомления
    cursor.execute('SELECT name FROM game_data WHERE chat_id = ?', (chat_id,))
    player_name = cursor.fetchone()[0]

    # Получаем код комнаты пользователя
    cursor.execute('SELECT room FROM game_data WHERE chat_id = ?', (chat_id,))
    room_code = cursor.fetchone()[0]

    # Получаем список всех участников комнаты
    cursor.execute('SELECT chat_id FROM game_data WHERE room = ?', (room_code,))
    players_in_room = cursor.fetchall()

    # Отправляем сообщение всем участникам комнаты
    for player in players_in_room:
        await bot.send_message(player[0], f"Игрок {player_name} взял из банка {amount} единиц.")

    # Очищаем состояние
    await state.clear()

# Обработчик callback-запроса для кнопки "Take from bank"
@dp.callback_query(lambda c: c.data == 'pay_to_bank')
async def pay_to_bank(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id

    # Сохраняем состояние ожидания суммы
    await state.set_state(TransferState3.waiting_for_money_amount3)

    await callback_query.message.answer("Введите сумму, которую хотите отдать банку:")


# Обработчик ввода суммы
@dp.message(TransferState3.waiting_for_money_amount3)
async def process_pay_to_bank(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    amount = int(message.text.strip())

    # Получаем баланс отправителя
    cursor.execute('SELECT money FROM game_data WHERE chat_id = ?', (chat_id,))
    sender_balance = cursor.fetchone()[0]

    # Проверяем, хватает ли средств для перевода
    if sender_balance < amount:
        await message.answer(f"У вас недостаточно средств для перевода. Пожалуйста, введите другую сумму under {sender_balance}.")
        return

    # Обновляем баланс игрока
    cursor.execute('UPDATE game_data SET money = money - ? WHERE chat_id = ?', (amount, chat_id))
    conn.commit()

    # Получаем имя игрока для уведомления
    cursor.execute('SELECT name FROM game_data WHERE chat_id = ?', (chat_id,))
    player_name = cursor.fetchone()[0]

    # Получаем код комнаты пользователя
    cursor.execute('SELECT room FROM game_data WHERE chat_id = ?', (chat_id,))
    room_code = cursor.fetchone()[0]

    # Получаем список всех участников комнаты
    cursor.execute('SELECT chat_id FROM game_data WHERE room = ?', (room_code,))
    players_in_room = cursor.fetchall()

    # Отправляем сообщение всем участникам комнаты
    for player in players_in_room:
        await bot.send_message(player[0], f"Игрок {player_name} отдал банку {amount} единиц.")

    # Очищаем состояние
    await state.clear()

@dp.callback_query(lambda c: c.data == 'let_me_out')
async def pay_to_bank(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id

    # Сохраняем состояние ожидания суммы
    await state.set_state(TransferState4.waiting_for_money_amount4)

    await callback_query.message.answer("Введите сумму, для взятки:")


# Обработчик ввода суммы
@dp.message(TransferState4.waiting_for_money_amount4)
async def process_let_me_out(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    amount = int(message.text.strip())

    # Получаем баланс отправителя
    cursor.execute('SELECT money FROM game_data WHERE chat_id = ?', (chat_id,))
    sender_balance = cursor.fetchone()[0]

    # Проверяем, хватает ли средств для перевода
    if sender_balance < amount:
        await message.answer(f"У вас недостаточно средств для оплаты. Balance: {sender_balance}.")
        return

    # Обновляем баланс игрока
    cursor.execute('UPDATE game_data SET money = money - ? WHERE chat_id = ?', (amount, chat_id))
    conn.commit()

    # Обновляем баланс игрока
    cursor.execute('UPDATE game_data SET apartments = ? WHERE chat_id = ?', (2, chat_id))
    conn.commit()

    # Получаем имя игрока для уведомления
    cursor.execute('SELECT name FROM game_data WHERE chat_id = ?', (chat_id,))
    player_name = cursor.fetchone()[0]

    # Получаем код комнаты пользователя
    cursor.execute('SELECT room FROM game_data WHERE chat_id = ?', (chat_id,))
    room_code = cursor.fetchone()[0]

    # Получаем список всех участников комнаты
    cursor.execute('SELECT chat_id FROM game_data WHERE room = ?', (room_code,))
    players_in_room = cursor.fetchall()

    # Отправляем сообщение всем участникам комнаты
    for player in players_in_room:
        await bot.send_message(player[0], f"Игрок {player_name} отдал тюрьме {amount} единиц взятку.")

    # Очищаем состояние
    await state.clear()

@dp.callback_query(lambda c: c.data == 'balance')
async def view_balance(callback_query: CallbackQuery, state: FSMContext):
    chat_id = callback_query.from_user.id

    cursor.execute('SELECT money FROM game_data WHERE chat_id = ?', (chat_id,))
    balance = cursor.fetchone()[0]
    await callback_query.message.answer(f"Your balance:{balance}")


@dp.message(Command(commands=["menu"]))
async def menu(message: Message, state: FSMContext):
    button1 = types.InlineKeyboardButton(text='Send money', callback_data='send_money')
    button2 = types.InlineKeyboardButton(text='Pay to bank', callback_data='pay_to_bank')
    button3 = types.InlineKeyboardButton(text='Take from bank', callback_data='take_from_bank')
    button4 = types.InlineKeyboardButton(text='pay to exit from prison', callback_data='let_me_out')
    button6 = types.InlineKeyboardButton(text='Баланс', callback_data='balance')
    markup_menu = types.InlineKeyboardMarkup(inline_keyboard=[[button1], [button2], [button3], [button4], [button6]])
    await message.answer("menu", reply_markup=markup_menu)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

import atexit
atexit.register(lambda: conn.close())