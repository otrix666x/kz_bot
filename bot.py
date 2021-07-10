from sqlite3.dbapi2 import connect
import telebot
from telebot import types
import time
import keyboard, config
import sqlite3
import random
tovar = {}
ves = {}
price = {}
bot = telebot.TeleBot(config.token)
@bot.message_handler(commands=['start'])
def start_bot(message):
    userid = message.chat.id
    connect = sqlite3.connect('bot.db')
    q = connect.cursor()
    q.execute("""CREATE TABLE IF NOT EXISTS users(
        id TEXT, discount INTEGER
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS promo(
        promo TEXT, discount INTEGER
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS adm(
        id TEXT
    )""")
    connect.commit()
    res = q.execute(f"SELECT * FROM users where id = {userid}").fetchone()
    if res is None:
        q.execute("INSERT INTO users(id) VALUES ('%s')"%(userid))
        connect.commit()
    bot.send_message(message.chat.id, config.start_text, parse_mode="html", reply_markup=keyboard.menu)

@bot.message_handler(commands=['admin', 'adm', 'админ'])
def adm(message):
    
    connect = sqlite3.connect('bot.db')
    q = connect.cursor()
    res = q.execute(f"SELECT id from adm where id = {message.chat.id}").fetchone()
    if res is None and message.chat.id not in config.admins:
        bot.send_message(message.chat.id, "Для вас эта команда недоступна👀")
    else:
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAECfL1g2F23u2MLMzpNIeVbfc9wb-7hoAACzAADe04qEF9nkGXzCRxAIAQ", reply_markup=keyboard.adm)
    

@bot.message_handler(content_types=['text'])
def text(message):
    user_id = message.chat.id
    message_id = message.message_id
    if message.text == "🌆Выбрать город":
        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot.send_message(user_id, "🌆Выбирите город", reply_markup=keyboard.city)
    if message.text == "👨‍💻Оператор":
        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot.send_message(user_id, f"Возникли какие-то вопросы?\nОператор шопа {config.support}", reply_markup=keyboard.cancel)
    if message.text == "🎫Промокод":
        bot.delete_message(chat_id=user_id, message_id=message_id)
        send = bot.send_message(user_id, "🎫Введите промокод🎫")
        bot.clear_step_handler_by_chat_id(user_id)
        bot.register_next_step_handler(send, promo)
    if message.text == "Добавить промокод🎟":
        bot.delete_message(chat_id=user_id, message_id=message_id)
        send = bot.send_message(user_id, "Введите промокод и % скидку")
        bot.clear_step_handler_by_chat_id(user_id)
        bot.register_next_step_handler(send, add_promo)
    if message.text == "Удалить промокод🎟":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        res = q.execute("SELECT * FROM promo").fetchall()
        proms = "Введите промокод который хотите удалить\n\n"
        if len(res) == 0:
            bot.send_message(message.chat.id, "На данный момент нет промокодов")
        else:
            for i in res:
                proms = proms + str(i[0]) + " " + str(i[1]) + "%" + "\n"
            bot.delete_message(chat_id=user_id, message_id=message_id)
            send = bot.send_message(user_id, proms, parse_mode='html', reply_markup=keyboard.cancel)
            bot.clear_step_handler_by_chat_id(user_id)
            bot.register_next_step_handler(send, del_promo)
    
    if message.text == "Меню🧞‍♀️":
        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAECcq9gzchf2Pfr0o-wfDSxlXRcxK3f1QACUl0AAp7OCwAB4FYiijZu4iwfBA", reply_markup=keyboard.menu)
    
    if message.text == "Добавить админа👨‍💻":
        bot.delete_message(chat_id=user_id, message_id=message_id)
        send = bot.send_message(user_id, "Введите id пользователя")
        bot.clear_step_handler_by_chat_id(user_id)
        bot.register_next_step_handler(send, add_adm)
    if message.text == "Запустить рассылку🔈":
        bot.delete_message(chat_id=user_id, message_id=message_id)
        bot.send_message(user_id, "Тип рассылки?🧐", reply_markup=keyboard.spam)
    
    if message.text == "Я оплатил✅":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute(f"update users set discount = 0 where id = {user_id}")
        connect.commit()
        bot.delete_message(chat_id=user_id, message_id=message_id)
        time.sleep(1.5)
        bot.send_message(user_id, "<b>Оплата не найдена, попробуйте через несколько секунд❌</b>", parse_mode="html")


            

@bot.callback_query_handler(func=lambda call: True)
def call_answ(call):
    userid = call.message.chat.id
    message_id = call.message.message_id
    if call.data == "delete":
        bot.delete_message(chat_id=userid, message_id=message_id)
    
    if call.data == "cancel_order":
        bot.delete_message(chat_id=userid, message_id=message_id)
        bot.delete_message(chat_id=userid, message_id=message_id-1)
        bot.send_message(userid, "Заказ успешно отменен🧞‍♀️", reply_markup=keyboard.menu)



    if call.data == "text":
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="📩Введите текст для рассылки📩")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, conf_text)
    
    if call.data == "pics":
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🌌Введите ссылку на фото с бота @imgurbot_bot🌌")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, caption)
    
    if call.data == "back_city":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🌆Выбирите город", reply_markup=keyboard.city)
    
    if call.data == "back_tovar":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="📦Выбирите товар", reply_markup=keyboard.staff)


######################################################################################################################################################    
    if call.data == "ast":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)
    
    if call.data == "kul":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "akt":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "aktb":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "alm":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "atr":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "kap":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "kar":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "kask":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "koksh":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "kuz":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "pavl":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "petr":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "saran":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "sem":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "tald":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "taraz":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)
    
    if call.data == "tem":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)
    
    if call.data == "tyrk":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)
    
    if call.data == "uralsk":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)
    
    if call.data == "ustkam":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "shaht":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "shum":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)

    if call.data == "ekuba":
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="🧞‍♀️Выбирите товар🧞‍♀️", reply_markup=keyboard.staff)
#######################################################################################################################################################
    if call.data == "Гаш 🍫":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.gash)
    
    if call.data == "Ск синий 🔵":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.sk_bl)
    
    if call.data == "Ск красный 🔴":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.sk_rd)
    
    if call.data == "Бошки White Widow 🌳":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.ww)
    
    if call.data == "Бошки АК-47 🌿":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.ak)
    
    if call.data == "Бошки Critical Kush 🌲":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.kush)
    
    if call.data == "Амф ⚡️":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.amf)
    
    if call.data == "Героин🍚":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.ger)
    
    if call.data == "План/Трим 🍃":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.plan)
    
    if call.data == "Лирика 300 💊":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.lira)
    
    if call.data == "Меф ❄️":
        tovar[userid] = call.data
        bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text=f"{tovar[userid]}", reply_markup=keyboard.mef)
######################################################################################################################################################
    
    if call.data == "1г – 13500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "2г – 24500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
        
    if call.data == "3г – 34500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "1г – 13000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "2г – 22000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "3г – 33000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "1г – 14000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "2г – 23000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "3г – 34000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "2г – 24000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "3г – 35000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################

    if call.data == "1г – 12000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "2г - 21000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "3г – 30000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "1г – 13500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "2г – 24500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "3г – 34500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "1г – 13000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "2г – 22000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "3г – 33000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################

    if call.data == "1г – 11500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)

    if call.data == "2г – 20500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)

    if call.data == "3г – 31500 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "1г – 15000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "2г – 26000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)

    if call.data == "3г – 39000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "2г – 12000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "4г – 21000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "5шт – 10000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "7шт – 12000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)

    if call.data == "14шт – 20000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
######################################################################################################################################################
    if call.data == "1г – 13000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)
    
    if call.data == "2г – 22000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)

    if call.data == "3г – 33000 ₸":
        arr = call.data.split('–')
        ves[userid] = arr[0]
        price[userid] = arr[1]
        send = bot.edit_message_text(chat_id=userid, message_id=call.message.message_id, text="Напишите(РАЙОН,УЛИЦУ, станцию метро) По этим данным БОТ найдет ближайший, актуальный JPS адрес с фото и его описанием. Например. г Москва, метро ВДНХ, ул Ленина. Или г Екатеринбург, посёлок Просторный, ул Снежная.")
        bot.clear_step_handler_by_chat_id(userid)
        bot.register_next_step_handler(send, pay)









######################################################################################################################################################
def pay(message):
    if message.text == "🌆Выбрать город" or message.text == "🎫Промокод" or message.text == "👨‍💻Оператор":
        bot.send_message(message.chat.id, "Отмена❌", reply_markup=keyboard.menu)
    else:
        comment = random.randint(1000000, 9999999)
        userid = message.chat.id
        arr = price[userid].split("₸")
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
        connect = sqlite3.connect("bot.db")
        q = connect.cursor()
        res = q.execute(f"SELECT discount from users where id = '{userid}'").fetchone()[0]
        if res is None or res == 0:
            bot.send_sticker(userid, "CAACAgIAAxkBAAECiRlg4xNYtwHIxHmH2FwcYbUCtPNwiQACvQADe04qEHG9Y2Kprec8IAQ", reply_markup=keyboard.pay_menu)
            bot.send_message(userid, "Готовый клад✅\n"\
                "➖➖➖➖➖➖➖➖➖➖\n"\
                    f"Товар: {tovar[userid]}\n"\
                        f"Количество: {ves[userid]}\n"\
                            f"Цена: {price[userid]}\n"\
                                "➖➖➖➖➖➖➖➖➖➖\n"\
                                    "Вы зарезервировали товар на 45⌛\n"\
                                        "Чтобы получить координаты + фото товара\n"\
                                            "Совершите платёж на QIWI / BTC / Карту.\n"\
                                                "➖➖➖➖➖➖➖➖➖➖\n"\
                                                    f"🏷QIWI кошелек: <code>{config.qiwi}</code>\n"\
                                                        f"💰Сумма к оплате: {arr[0]}₸\n"\
                                                            f"Комментарий к платежу: <code>{comment}</code>\n"\
                                                                "➖➖➖➖➖➖➖➖➖➖ \n"\
                                                                    f"🏷️КАРТА: <code>{config.card}</code>\n"\
                                                                        f"👤Держатель карты: {config.card_holder}\n"\
                                                                            f"💰Сумма к оплате: {arr[0]}₸\n"\
                                                                                "➖➖➖➖➖➖➖➖➖➖\n"\
                                                                                    f"Если вы хотите оплатить с Помощью BITCOIN, то переведите сумму эквивалентную {arr[0]}₸ рублям на зарезервированный для вас BITCOIN адрес:\n"\
                                                                                        f"<code>{config.btc}</code>\n"\
                                                                                            "➖➖➖➖➖➖➖➖➖➖\n"\
                                                                                                "‼️<b>Сумма платежа должна быть равна указаной или выше.</b>\n"\
                                                                                                    "‼️<b>Платежи обрабатываются в автоматическом режиме.</b>", parse_mode="html", reply_markup=keyboard.cancel_order)
        else:
            dsc = int(res) / 100
            new_price = int(arr[0]) - int(arr[0]) * dsc
            summ = str(new_price).split(".")
            bot.send_sticker(userid, "CAACAgIAAxkBAAECiRlg4xNYtwHIxHmH2FwcYbUCtPNwiQACvQADe04qEHG9Y2Kprec8IAQ", reply_markup=keyboard.pay_menu)
            bot.send_message(userid, "Готовый клад✅\n"\
                "➖➖➖➖➖➖➖➖➖➖\n"\
                    f"Товар: {tovar[userid]}\n"\
                        f"Количество: {ves[userid]}\n"\
                            f"Цена: {price[userid]}\n"\
                                f"Скидка {res}%\n"\
                                    "➖➖➖➖➖➖➖➖➖➖\n"\
                                        "Вы зарезервировали товар на 45⌛\n"\
                                            "Чтобы получить координаты + фото товара\n"\
                                                "Совершите платёж на QIWI / BTC / Карту.\n"\
                                                    "➖➖➖➖➖➖➖➖➖➖\n"\
                                                        f"🏷QIWI кошелек: <code>{config.qiwi}</code>\n"\
                                                            f"💰Сумма к оплате: {summ[0]} ₸\n"\
                                                                f"Комментарий к платежу: <code>{comment}</code>\n"\
                                                                    "➖➖➖➖➖➖➖➖➖➖ \n"\
                                                                        f"🏷️КАРТА: <code>{config.card}</code>\n"\
                                                                            f"👤Держатель карты: {config.card_holder}"
                                                                                f"💰Сумма к оплате: {summ[0]} ₸\n"\
                                                                                    "➖➖➖➖➖➖➖➖➖➖\n"\
                                                                                        f"Если вы хотите оплатить с Помощью BITCOIN, то переведите сумму эквивалентную {summ[0]} ₸ рублям на зарезервированный для вас BITCOIN адрес:\n"\
                                                                                            f"<code>{config.btc}</code>\n"\
                                                                                                "➖➖➖➖➖➖➖➖➖➖\n"\
                                                                                                    f"<i>Действует скидка {res}%</i>\n\n"\
                                                                                                        "‼️<b>Сумма платежа должна быть равна указаной или выше.</b>\n"\
                                                                                                            "‼️<b>Платежи обрабатываются в автоматическом режиме.</b>", parse_mode="html",reply_markup=keyboard.cancel_order)

    


    






def caption(message):
    photo = message.text
    text = bot.send_message(message.chat.id, "Введите текст под фото")
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(text, conf_photo, photo)

def conf_photo(message, photo):
    text = message.text
    send = bot.send_photo(message.chat.id, photo, caption=f"{text}\n\n"\
        "Отправлять? ДА/НЕТ")
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(send, send_photo,text, photo)

def send_photo(message,text, photo):
    if message.text.lower() == "да":
        try:
            caption = message.text
            connect = sqlite3.connect('bot.db')
            q = connect.cursor()
            res = q.execute("SELECT id FROM users").fetchall()
            bot.send_message(message.chat.id, "<b>Рассылка начнеться через 3 сукунды!</b>", parse_mode="html")
            time.sleep(3)
            bot.send_message(message.chat.id, "<b>Рассылка пошла!</b>", parse_mode="html")
            k = 0
            for i in res:
                try:
                    bot.send_photo(i[0], photo,caption=text, parse_mode="html", reply_markup=keyboard.cancel)
                    time.sleep(0.3)
                except:
                    pass
                k += 1
            bot.send_message(message.chat.id, f"Рассылку получило {k} чел.")
            
        except:
            bot.send_message(message.chat.id, "Ошибка")
    else:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.send_message(message.chat.id, "Рассылка отменена!")

def conf_text(message):
    text = message.text
    send = bot.send_message(message.chat.id, f"{text}\n\n"\
        "Отправлять? ДА/НЕТ")
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(send, send_all, text)


def send_all(message, text):
    if message.text.lower() == "да":
        try:
            connect = sqlite3.connect('bot.db')
            q = connect.cursor()
            res = q.execute("SELECT id FROM users").fetchall()
            bot.send_message(message.chat.id, "<b>Рассылка начнеться через 3 сукунды!</b>", parse_mode="html")
            time.sleep(3)
            bot.send_message(message.chat.id, "<b>Рассылка пошла!</b>", parse_mode="html")
            k = 0
            for i in res:
                try:
                    bot.send_message(i[0], text,disable_web_page_preview=True, parse_mode="html", reply_markup=keyboard.cancel)
                    time.sleep(0.3)
                except:
                    pass
                k += 1
            bot.send_message(message.chat.id, f"Рассылку получило {k} чел.")
            
        except:
            bot.send_message(message.chat.id, "Ошибка")
    else:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.send_message(message.chat.id, "Рассылка отменена!")


def promo(message):
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        promo = message.text
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        res = q.execute("SELECT * FROM promo").fetchall()
        for i in res:
            if i[0] == promo:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                res = q.execute(f"SELECT discount FROM promo where promo = '{i[0]}'").fetchone()[0]
                bot.send_message(message.chat.id, f"Промокод на скидку {res}% был успешно активирован")
                q.execute(f"update users set discount = {res} where id = '{message.chat.id}'")
                connect.commit()

    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка попробуйте позже")
        print(e)

def add_promo(message):
    try:
        arr = message.text.split(" ")
        promo = arr[0]
        disount = arr[1]
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("INSERT INTO promo(promo, discount) VALUES ('%s', '%s')"%(promo, disount))
        connect.commit()
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(message.chat.id, f"Промокод <code>{arr[0]}</code> на {arr[1]}% успешно добавлен", parse_mode="html")
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    except:
        bot.send_message(message.chat.id, "Ошибка")


def del_promo(message):
    promo = message.text
    try:
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute(f"DELETE FROM promo where promo = '{promo}'")
        connect.commit()
        bot.send_message(message.chat.id, f"Промокод {promo} успешно удален")
    except:
        bot.send_message(message.chat.id, "Ошибка")

def add_adm(message):
    try:
        adm_id = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        res = q.execute(f"SELECT * FROM adm where id = {adm_id}").fetchone()
        if res is None:
            q.execute("INSERT INTO adm(id) VALUES ('%s')"%(adm_id))
            connect.commit()
            bot.send_message(message.chat.id, "Админ добавлен успешно✅")
        else:
            bot.send_message(message.chat.id, "Амин уже есть в списке👀")

    except:
        bot.send_message(message.chat.id, "❌Произошла ошибка")
        time.sleep(1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        





while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        time.sleep(5)
        try:
            bot.polling(none_stop=True, interval=0)
        except:
            pass
