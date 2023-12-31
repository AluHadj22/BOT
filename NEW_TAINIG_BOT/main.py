from aiogram import types
from create_bot import bot,dp
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from keybord_client import kb_client
from keybord_client import menu_kb
import json, string
from data_base import sqlite_db


ID = None
async def on_startup(_):
    print("BOT IS ONLINE")
    sqlite_db.sql_start()

from handlers import call
call.register_handlers_call(dp)


    
#MENU PANEL
class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    desctiption = State()
    callories = State()

#ПОЛУЧАЮ ID ТЕКУЩЕГО МОДЕРА
@dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Что вы хотите сделать?', reply_markup=menu_kb.button_case_admin)
    await message.delete()



@dp.message_handler(commands=['load_Menu'], state=None)
async def cm_start(message: types.Message):
    await FSMAdmin.photo.set()
    await message.reply('Загрузи фото')
#Выход из состояний
@dp.message_handler(state="*", commands=['cancel'])
@dp.message_handler(Text(equals='cancel', ignore_case=True),state='*')
async def cancel_handler(message: types.Message,  state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.finish()
    await message.reply('OK')

@dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await FSMAdmin.next()
    await message.reply('Теперь введи название')

@dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply('Введи описание')

@dp.message_handler(state=FSMAdmin.desctiption)
async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desctiption'] = message.text
    await FSMAdmin.next()
    await message.reply('Введи калории на 100 грамм продукта')

@dp.message_handler(state=FSMAdmin.callories)
async def load_callories(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['callories'] = message.text
    
    await sqlite_db.sql_add_command(state)
    await state.finish()




#CLIENT PANEL

@dp.message_handler(commands=["start"])
async def command_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, "Привет, я бот-ТРЕНЕР, котрого создал Алу. Для получения информации о возможностях, нажми кнопку help", reply_markup=kb_client)
        await message.delete()
    except:
        await message.reply("Общение с ботом только через лс, перейдите по ссылке: http://t.me/Training_Alu_bot_BOT")

@dp.message_handler(commands=["help"])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Вы можете высчитать калории через мой калькулятор, который использует формулу Миллера с учетом ваших данных.\n Для этого, нажми кнопку caloris. Есть возможность получить меню(план питания), его вы можете редактровать и сами. Для этого, добавьте бота в любую группу и дайте ему админку, а после, напишите в группе команду\n /moderator.\n',  reply_markup=kb_client)
    await message.delete()
#АДРЕС
@dp.message_handler(commands=["calories"])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id,"",  reply_markup=kb_client) # вычисление идет в другом файле, я передумал.
    await message.delete()



@dp.message_handler(commands=["Menu"])
async def command_start(message: types.Message):
    await sqlite_db.sql_read(message)


def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(command_start, commands=['help'])
    dp.register_message_handler(command_start, commands=['calories'])
    dp.register_message_handler(command_start, commands=['Menu'])
    dp.register_message_handler(cm_start, commands=['load_Menu'], state=None)
    dp.message_handler(state="*", commands=['cancel'])
    dp.message_handler(Text(equals='cancel', ignore_case=True),state='*')
    dp.register_message_handler(load_photo, content_types=['photo'], state=FSMAdmin.photo )



#ФИЛЬТР МАТЕРНОЙ ЛЕКСИКИ
@dp.message_handler()
async def echo_send(message : types.Message):
    for i in message.text.split(' '):
        if {i.lower().translate(str.maketrans("", "", string.punctuation))}.intersection(set(json.load(open('cenz.json')))) != set():
            await message.reply('Матерная лексика запрещена!')
            await message.delete()



def register_handlers_other(dp : Dispatcher):
    dp.register_message_handler(echo_send)
    




    




executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


