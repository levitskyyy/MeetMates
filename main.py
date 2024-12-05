import logging
import asyncio
import random
import pymysql
from pymysql.cursors import DictCursor
import string
import emoji
import time
# aiogram и всё утилиты для коректной работы с Telegram API
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.utils.emoji import emojize
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentType
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, callback_query
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.exceptions
from aiogram.types.message import ContentTypes
# конфиг с настройками
import config
import markups as lev
from database import Dbworker, UserInfo
from aiocryptopay import AioCryptoPay, Networks

# инициализируем базу данных
db = Dbworker()
profiledb = UserInfo()

# инициализируем бота
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# логирование
logging.basicConfig(filename="all_log.log", level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s')
warning_log = logging.getLogger("warning_log")
warning_log.setLevel(logging.WARNING)

fh = logging.FileHandler("warning_log.log")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

warning_log.addHandler(fh)

crypto = AioCryptoPay(token=config.DONATE, network='https://pay.crypt.bot')
gamelist = dict()


# Антифлуд
async def anti_flood(*args, **kwargs):
    pass


class Chating(StatesGroup):  # Машина состояний для переписки
    msg = State()
    donate = State()
    usernick = State()
    userlike = State()
    steamconnector = State()
    gamechooser = State()


# хендлер команды /start

@dp.message_handler(commands=['start'], state='*')
async def start(message: types.Message, state: FSMContext):
    start_text = [
        '<b>Привет, волчонок! 🐺 </b>\n\n<i>MeetMates - именно тот бот, который сможет помочь тебе в поиске тиммейта для твоей любимой игры!</i>\n\nЧтобы преступить к поиску волчонка, просто воспользуйся кнопками. 😉',
        '<b>Привет, волчонок! 🐺 </b>\n\n<i>MeetMates - это именно тот чат-бот, который сможет помочь тебе найти напарника для игры, которую ты любишь!</i>\n\nЧтобы преступить к поиску волчонка, просто воспользуйся кнопками. 😉',
        '<b>Привет, волчонок! 🐺 </b>\n\n<i>MeetMates - это именно тот чат-бот, который сможет помочь тебе найти волчонка для совместной игры!</i>\n\nЧтобы преступить к поиску волчонка, просто воспользуйся кнопками. 😉']
    hi_sticker = ['CAACAgIAAxkBAAEIGJdkDNP28kxsutxggNlK25dxUEsVXwACLiMAAmabGEuBY7fvxgPQky8E',
                  'CAACAgIAAxkBAAEIJfhkEeIs2CLNH73xOrynCxvCTvaN6AACtiUAAvh3GEtre9Hh2p7XKy8E',
                  'CAACAgIAAxkBAAEIJfpkEeI9nkpvypq2zqZj8NgB0unxwQACXCQAAvaEGUu8NmNITYHkSy8E',
                  'CAACAgIAAxkBAAEIVRhkIGyLCIIXW75dj1JiuODHQu-VWgACjyQAAmxaGUtQ--rb3igI8y8E']
    gamelist[message.from_user.id] = set()
    if not db.user_exists(message.from_user.id):  # если пользователя с таким telegram id не найдено
        ref_id = int(message.get_args()) if message.get_args() and message.get_args().isdigit() else 0
        if ref_id != message.from_user.id:
            db.add_user(message.from_user.username, message.from_user.id)
            db.setting_referal_id(ref_id, message.from_user.id)
            try:
                await bot.send_message(ref_id,
                                       f"По вашей ссылке зарегистрировался(-лась) @{message.from_user.username}\n"
                                       f"Вам начислено 25 🔹")
                db.add_count_refs(ref_id)
                db.add_count_msg_ref(ref_id)
            except:
                pass
        else:
            db.add_user(message.from_user.username, message.from_user.id)
            await bot.send_message(message.from_user.id,
                                   "Реферальная система не работает на вас, если это ваша ссылка.")

    await state.finish()
    db.update_connect_with(None, db.select_connect_with(message.from_user.id))
    db.update_connect_with(None, message.from_user.id)
    if int(message.from_user.id) in profiledb.get_all_id_in_description():
        profiledb.user_id(message.from_user.id, yet_in_base=True)
    else:
        profiledb.user_id(message.from_user.id, yet_in_base=False)

    await bot.send_sticker(chat_id=message.chat.id,
                           sticker=random.choice(hi_sticker))
    await bot.send_message(message.chat.id,
                           f'{random.choice(start_text)}',
                           parse_mode='html', reply_markup=lev.mainMenu)
    if db.queue_exists(message.from_user.id):
        db.delete_from_queue(message.from_user.id)
        await bot.send_message(message.from_user.id, 'Вы были удалены из очереди.')


@dp.throttled(anti_flood, rate=1.5)
@dp.callback_query_handler(text="other", state='*')
async def other(message: types.Message):
    other_sticker = ['CAACAgIAAxkBAAEIVRRkIGxt4jJeDlig8I37gdGY5Y4PdAACVCYAAj-tGUtWODpA5fbkbi8E',
                     'CAACAgIAAxkBAAEIVRZkIGxzaHjjW69yl5YJDuptPITO9AACMCIAAiQqGEvksMEgNC_-9C8E']
    await bot.send_sticker(chat_id=message.from_user.id,
                           sticker=random.choice(other_sticker))
    await bot.send_message(message.from_user.id,
                           f'Выберите нужный для себя пункт в меню.', reply_markup=lev.otherMenu)


@dp.throttled(anti_flood, rate=1)
@dp.callback_query_handler(text="donate", state="*")
async def passer(callback_query: types.CallbackQuery, state=FSMContext):
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id,
                           f'Напишите сколько TON вы хотите нам пожертвовать! 😉 \n\n Отправьте число 0, чтобы отменить действие.',
                           reply_markup=lev.backMenu)
    await Chating.donate.set()


@dp.throttled(anti_flood, rate=0.7)
@dp.message_handler(content_types=ContentTypes.TEXT, state=Chating.donate)
async def donate1(message: types.message, state: FSMContext):
    invoice = await crypto.create_invoice(asset='TON', amount=message.text)
    await bot.send_message(message.from_user.id,
                           f'Ваша ссылка на оплату счёта в {message.text} TON.\n\n' + invoice.pay_url,
                           reply_markup=lev.backMenu)
    if callback_query.data == "back":
        await state.finish()
        await start(callback_query.message, state)
        await callback_query.answer("Действие отменено.")


@dp.callback_query_handler(text="back", state=Chating.donate)
@dp.callback_query_handler(text="back", state="*")
async def donate_back(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await state.finish()
    await start(callback_query.message, state)
    if db.queue_exists(user_id):
        db.delete_from_queue(user_id)
        await bot.send_message(user_id, 'Вы были удалены из очереди.')
    await callback_query.answer("Действие отменено.")


@dp.throttled(anti_flood, rate=1)
@dp.callback_query_handler(text="settings", state="*")
async def settings(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, 'Выбери нужный для себя пункт в меню!',
                           reply_markup=lev.settingsMenu)


@dp.message_handler(commands=['sendall'])
async def sendall(message: types.Message):
    if message.from_user.id == 1181380861 or message.from_user.id == 630334547:
        text = message.text[9:]
        users = db.get_users()
        for row in users:
            try:
                await bot.send_message(row[0], text)
                print(f"Успешное уведомление {row}")
                if int(row[1]) != 1:
                    db.set_active(row[0], 1)
                    print("Удалось отправить сообщение, пользователь помечен как активный!")
            except:
                db.set_active(row[0], 0)
                print(f"Пользователь {row[0]} помечен как неактивный.")

        await bot.send_message(message.from_user.id, "Рассылка окончена.")


@dp.throttled(anti_flood, rate=1)
@dp.callback_query_handler(text="search")
async def search(message: types.Message):
    try:
        if (not db.user_exists(message.from_user.id)):  # если пользователя с таким telegram id не найдено
            db.add_user(message.from_user.username, message.from_user.id)  # добавляем юзера в табличку дб

        await Chating.gamechooser.set()
        await bot.send_message(message.from_user.id,
                               'Выбери игру, по которой мы будем искать тиммейта. Как закончишь, дай нам знать, нажав "Готово"🐺',
                               reply_markup=lev.searchMenu)
    except Exception as e:
        warning_log.warning(e)


@dp.callback_query_handler(text="rating")
@dp.throttled(anti_flood, rate=2)
async def ranked(message: types.Message, state: FSMContext):
    ''' Функция для вывода рейтинга '''
    try:
        one = ['\nЗадрот, топ 1 выфармил!\n', '\nОго! Вот так да, первое место?\n', '\nПобедааа\n',
               '\nМощный волчонок\n']
        two = ['\nНеплохо, второе место!\n', '\nНеплохая активность, как для волчонка..\n',
               '\nОго-ого, кто-то у нас не вылазит с телефона!\n', '\nДа ну, второе место? Неплохо!\n']
        three = ['\nТретее место.. Это конечно не первое, но пойдёт!\n', '\n#Говорила\n', '\nАктивничает...\n']
        four = ['\n4 место, ууу, можно было и лучше...\n', '\nМожет больше актива? Ну ладно, хоть что-то...\n',
                '\nНеплохо, неплохо...\n']
        five = ['\nЗато в топе!\n', '\nНу.. 5 место...\n', '\nПойдёт!\n', '\nУхты! Это 5 место???\n']
        final_top = ''
        top_count = 0
        for i in db.top_rating():
            top_count += 1
            if db.get_name_user(i) == None:
                rofl_list = [random.choice(one), random.choice(two), random.choice(three), random.choice(four),
                             random.choice(five)]
                final_top = final_top + str(top_count) + '. *нету ника*' + ' - ' + str(
                    db.get_count_all_msg(i)) + ' 💠' + rofl_list[top_count - 1] + '\n'
            else:
                rofl_list = [random.choice(one), random.choice(two), random.choice(three), random.choice(four),
                             random.choice(five)]
                final_top = final_top + str(top_count) + '. @' + str(db.get_name_user(i)) + ' - ' + str(
                    db.get_count_all_msg(i)) + ' 💠' + rofl_list[top_count - 1] + '\n'
        await bot.send_message(message.from_user.id,
                               f'Рейтинг самых активных волчонков! 🐺\n\n{final_top}', reply_markup=lev.backMenu)
    except Exception as e:
        warning_log.warning(e)


back_message = ["Во время редактирования профиля нельзя вернуться в главное меню.",
                "Доделай профиль, а потом выходи!",
                "Нельзя выходить, сначала доделай профиль!",
                "Доделай, а потом выходи."]


@dp.throttled(anti_flood, rate=2)
@dp.callback_query_handler(text="eprofile", state="*")
async def nicknamesetter(query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.send_message(query.from_user.id, 'Начнём! Укажите никнейм, который желаете носить в нашей системе👻',
                           reply_markup=lev.backMenu)
    if query.data == '-':
        await Chating.usernick.set()
    else:
        await Chating.usernick.set()


@dp.throttled(anti_flood, rate=2)
@dp.callback_query_handler(text="refka", state="*")
async def refkainfo(query: types.CallbackQuery, state: FSMContext):
    result = profiledb.user_selector_refs(query.from_user.id)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.send_message(query.from_user.id,
                           f'💠 Реферальная система даёт возможность пригласить своего друга, получив за это доп. бонусы!\n\n'
                           f'Ваша реф. ссылка: https://t.me/MeetMates_bot?start={query.from_user.id}\n'
                           f'Ваше кол-во рефералов: {result["refs"]}', reply_markup=lev.backMenu)


@dp.throttled(anti_flood, rate=0.7)
@dp.message_handler(content_types=ContentTypes.TEXT, state=Chating.usernick)
async def nicknamesetter(message: types.message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(message.from_user.id,
                           'Теперь напиши твои увлечения. Если ты не хочешь их писать, просто поставь прочерк: "-"',
                           reply_markup=lev.backMenu)
    if message.text == '-':
        await Chating.userlike.set()
    else:
        await Chating.userlike.set()
        await profiledb.user_nick(message.from_user.id, message.text)


@dp.throttled(anti_flood, rate=0.7)
@dp.message_handler(content_types=ContentTypes.TEXT, state=Chating.userlike)
async def likessetter(message: types.message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(message.from_user.id,
                           'Класс! А сейчас можешь привязать свой стим профиль к профилю в нашей системе',
                           reply_markup=lev.backMenu)
    if message.text == '-':
        await Chating.userlike.set()
    else:
        await Chating.steamconnector.set()
        await profiledb.user_likes(message.from_user.id, message.text)


@dp.throttled(anti_flood, rate=0.7)
@dp.message_handler(content_types=ContentTypes.TEXT, state=Chating.steamconnector)
async def steamsetter(message: types.message, state: FSMContext):
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.send_message(message.from_user.id, 'Замечательно! Твой профиль готов!', reply_markup=lev.backMenu)
    await state.finish()
    await profiledb.steam_link(message.text, message.from_user.id)


@dp.throttled(anti_flood, rate=1)
@dp.callback_query_handler(text="profile", state="*")
async def view_profile(message: types.Message):
    result = profiledb.user_selector(message.from_user.id)
    result1 = profiledb.user_selector_refs(message.from_user.id)
    await bot.send_message(message.from_user.id, f'— Профиль —\n'
                                                 f'🔹 Никнейм: {result["user_nick"] if result["user_nick"] != "" else "-"}\n'
                                                 f'🔹 Увлечения: {result["user_like"] if result["user_like"] != "" else "-"}\n'
                                                 f'🔹 Кол-во рефералов: {result1["refs"]}\n'
                                                 f'🔹 Статус в системе: {result["user_status"] if result["user_status"] != "" else "-"}\n'
                                                 f'🔹 Steam: {result["steamlink"] if result["steamlink"] != "" else "-"}\n'
                                                 f'— 1/1 —', reply_markup=lev.backMenu)


@dp.throttled(anti_flood, rate=2)
@dp.callback_query_handler(text="info", state="*")
async def passer(message: types.Message):
    await bot.send_message(message.from_user.id, f'🔹 <b>Общая информация</b> 🔹\n\n'
                                                 f'Кол-во волчат: {int(db.count_user())}\n'
                                                 f'Кол-во неактивных волчат: {int(db.count_deactive())}\n'
                                                 f'По поводу вопросов/багов: @ew2df\n', parse_mode='html')


@dp.throttled(anti_flood, rate=0.7)
@dp.callback_query_handler(
    lambda callback_query: callback_query.data in ['minecraft', 'csgo', 'dota', 'wot', 'rust', 'valorant', 'pubg'],
    state=Chating.gamechooser)
async def game_insert(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    chosen_game = callback_query.data

    async with state.proxy() as data:
        if "gamelist" not in data:
            data["gamelist"] = {chosen_game}
        else:
            result = {i for i in data["gamelist"]}
            result.add(chosen_game)
            data["gamelist"] = result

    await bot.answer_callback_query(callback_query.id, text=f"Вы выбрали игру {chosen_game.capitalize()}")


@dp.throttled(anti_flood, rate=2)
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'done', state=Chating.gamechooser)
async def choose_game(callback_query: types.CallbackQuery, state: FSMContext):
    ''' Выбор игры для поиска '''
    try:
        user_id = callback_query.from_user.id

        if db.queue_exists(user_id):
            db.delete_from_queue(user_id)

        selected_games = set()

        async with state.proxy() as data:
            if "gamelist" in data:
                selected_games = list(data.get("gamelist", set()))

        if not selected_games:
            current_state = await state.get_state()
            if current_state is not None and current_state == Chating.gamechooser:
                await bot.send_message(user_id, 'Выбери хотя бы одну игру!', reply_markup=lev.searchMenu)
            return await state.reset_state()

        db.add_to_queue(user_id, list(selected_games))

        await bot.send_message(user_id, 'Ищем для вас волчат по вашим интересам..', reply_markup=lev.backMenu)

        while True:
            await asyncio.sleep(1)
            found_user = db.search(db.get_game_user(user_id), user_id)
            if found_user is not None:  # если был найден подходящий юзер в очереди
                try:
                    db.update_connect_with(found_user, user_id)  # обновляем с кем общается юзер
                    db.update_connect_with(user_id, found_user)
                    break
                except Exception as e:
                    print(e)

        while True:
            await asyncio.sleep(1)
            connected_user = db.select_connect_with(user_id)
            if connected_user is not None:  # если пользователь законектился
                await Chating.msg.set()
                break

        try:
            db.delete_from_queue(user_id)  # удаляем из очереди
            db.delete_from_queue(connected_user)
        except:
            pass

        result1 = profiledb.user_selector(user_id)
        result2 = profiledb.user_selector(connected_user)
        result3 = profiledb.user_selector_refs(user_id)
        result4 = profiledb.user_selector_refs(connected_user)

        # отправляем профиль собеседника
        await bot.send_message(connected_user, f'— Профиль собеседника —\n'
                                               f'🔹 Никнейм: {result1["user_nick"] if result1["user_nick"] != "" else "-"}\n'
                                               f'🔹 Увлечения: {result1["user_like"] if result1["user_like"] != "" else "-"}\n'
                                               f'🔹 Кол-во рефералов: {result3["refs"]}\n'
                                               f'🔹 Статус в системе: {result1["user_status"] if result1["user_status"] != "" else "-"}\n'
                                               f'🔹 Steam: {result1["steamlink"] if result1["steamlink"] != "" else "-"}\n'
                                               f'— 1/1 —')

        # отправляем сообщение о начале диалога
        await bot.send_message(connected_user, 'Диалог начался!\nЧтобы закончить нажмите кнопки под этим сообщением.',
                               reply_markup=lev.messageMenu)

        return None

    except Exception as e:
        warning_log.warning(e)


@dp.throttled(anti_flood, rate=0.7)
@dp.callback_query_handler(state='*')
async def chating(callback_query: types.CallbackQuery, state: FSMContext):
    ''' Подготовка к месседжингу, проверка всех условий'''
    try:
        if callback_query.data == 'share':
            if callback_query.from_user.username == None:
                await bot.send_message(db.select_connect_with_self(callback_query.from_user.id),
                                       'Пользователь не заполнил никнейм в настройках телеграма!')
            else:
                await bot.send_message(db.select_connect_with_self(callback_query.from_user.id),
                                       '@' + callback_query.from_user.username)
                await bot.send_message(callback_query.id, '@' + callback_query.from_user.username)

        elif callback_query.data == 'stop':
            await bot.send_message(callback_query.from_user.id, 'Диалог закончился!',
                                   reply_markup=lev.endMenu)
            await bot.send_message(db.select_connect_with(callback_query.from_user.id), 'Диалог закончился!',
                                   reply_markup=lev.endMenu)
            db.update_connect_with(None, db.select_connect_with(callback_query.from_user.id))
            db.update_connect_with(None, callback_query.from_user.id)

        elif callback_query.data == 'next':
            await choose_game(callback_query, state)

        elif callback_query.data == 'back':
            await start(callback_query, state)
            await state.finish()
            if db.queue_exists(callback_query.from_user.id):
                db.delete_from_queue(callback_query.from_user.id)
                await bot.send_message(callback_query.from_user.id, 'Вы были удалены из очереди.')

    except aiogram.utils.exceptions.ChatIdIsEmpty:
        await state.finish()
        await start(callback_query, state)
    except aiogram.utils.exceptions.BotBlocked:
        await bot.send_message(callback_query.id, 'Пользователь вышел из чат бота!')
        await state.finish()
        await start(callback_query, state)
    except Exception as e:
        warning_log.warning(e)


@dp.throttled(anti_flood, rate=0.5)
@dp.message_handler(content_types=ContentTypes.TEXT, state=Chating.msg)
async def chating_text(message: types.Message, state: FSMContext):
    '''Function with messaging'''
    await state.update_data(msg=message.text)
    user_data = await state.get_data()
    try:
        await bot.send_message(db.select_connect_with(message.from_user.id), user_data['msg'])
        # отправляем сообщения пользователя
        db.log_msg(message.from_user.id, user_data['msg'])  # логирование
        if random.randint(0, 100) < 10:
            db.add_count_msg(message.from_user.id)
        else:
            pass
    except Exception as a:
        warning_log.warning(a)


@dp.throttled(anti_flood, rate=0.5)
@dp.message_handler(content_types=ContentTypes.PHOTO, state=Chating.msg)
async def chating_photo(message: types.Message, state: FSMContext):
    ''' Функция где и происходить общения и обмен ФОТОГРАФИЯМИ '''
    try:
        await message.photo[-1].download('photo_user/' + str(message.from_user.id) + '.jpg')
        with open('photo_user/' + str(message.from_user.id) + '.jpg', 'rb') as photo:
            await bot.send_photo(db.select_connect_with(message.from_user.id), photo, caption=message.text)
    except Exception as e:
        warning_log.warning(e)


@dp.throttled(anti_flood, rate=2)
@dp.message_handler(content_types=ContentTypes.ANIMATION, state=Chating.msg)
async def chating_gif(message: types.Message, state: FSMContext):
    ''' Функция для обмена GIF '''
    try:
        await message.animation.download('gif_user/' + str(message.from_user.id) + '.gif')
        with open('gif_user/' + str(message.from_user.id) + '.gif', 'rb') as gif:
            await bot.send_animation(db.select_connect_with(message.from_user.id), gif, caption=message.caption)
    except Exception as e:
        warning_log.warning(e)


@dp.throttled(anti_flood, rate=2)
@dp.message_handler(content_types=ContentTypes.STICKER, state=Chating.msg)
async def chating_sticker(message: types.Message, state: FSMContext):
    ''' Функция где и происходить общения и обмен CТИКЕРАМИ '''
    try:
        await bot.send_sticker(db.select_connect_with(message.from_user.id), message.sticker.file_id)
    except Exception as e:
        warning_log.warning(e)


@dp.message_handler(content_types=ContentTypes.VOICE, state=Chating.msg)
async def chating_voice(message: types.Message, state: FSMContext):
    try:
        await bot.send_voice(db.select_connect_with(message.from_user.id), message.voice.file_id)
    except Exception as e:
        warning_log.warning(e)


@dp.throttled(anti_flood, rate=0.5)
@dp.callback_query_handler(lambda callback_query: callback_query.data == 'back')
async def back(message: types.Message, state: FSMContext):
    ''' Функция для команды back '''
    user_id = callback_query.from_user.id
    await state.finish()
    if db.queue_exists(user_id):
        db.delete_from_queue(user_id)
        await bot.send_message(user_id, 'Вы были удалены из очереди.')
    await start(message, state)


# хендлер который срабатывает при непредсказуемом запросе юзера

@dp.throttled(anti_flood, rate=1)
@dp.message_handler()
async def end(message: types.Message):
    '''Функция непредсказумогого ответа'''
    await message.answer('Я не знаю, что с этим делать 😲\nЯ просто напомню, что есть команда /start')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, )
