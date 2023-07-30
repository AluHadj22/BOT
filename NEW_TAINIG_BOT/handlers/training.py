from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import dp,bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db_training
from keybord_client import menu_kb




class FSMAdmin(StatesGroup):
    link = State()
    name = State()
    desctiption = State()

#ПОЛУЧАЮ ID ТЕКУЩЕГО МОДЕРА
@dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Что вы хотите сделать?', reply_markup=menu_kb.button_case_admin)
    await message.delete()



@dp.message_handler(commands=['load_training'], state=None)
async def cm_start(message: types.Message):
    await FSMAdmin.link.set()
    await message.reply('напиши ссылку на видео')


@dp.message_handler(content_types=['link'], state=FSMAdmin.link)
async def load_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['link'] = message.link[0].file_id
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
    
    await sqlite_db_training.sql_add_command(state)
    await state.finish()


def register_handlers_training(dp : Dispatcher):
    dp.register_message_handler(cm_start, commands=['load_training'], state=None)
    dp.message_handler(state="*", commands=['cancel'])
    dp.message_handler(Text(equals='cancel', ignore_case=True),state='*')
    dp.register_message_handler(load_link, content_types=['link'], state=FSMAdmin.link )
    dp.register_message_handler(load_name, state=FSMAdmin.name )
    dp.register_message_handler(load_description, state=FSMAdmin.desctiption )