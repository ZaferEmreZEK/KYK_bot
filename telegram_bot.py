import os
import telebot
import pandas as pd
from datetime import datetime, timedelta
import locale
from telegram.ext import Updater

# Turkce tarih formatini kullanmak icin locale ayarini yapin
locale.setlocale(locale.LC_TIME, 'tr_TR.UTF-8')

# API_KEY'yi cevre degiskenlerinden alin
API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(API_KEY)


# Komutları ayarla
commands = [
    telebot.types.BotCommand("/ben_gulnarliyim", "Sana bir mesaj verir"),
    telebot.types.BotCommand("/bugunkukahvalti", "Bugunku kahvalti menusunu gosterir"),
    telebot.types.BotCommand("/yarinkikahvalti", "Yarinki kahvalti menusunu gosterir"),
    telebot.types.BotCommand("/sonrakigun", "Sonraki gunun kahvalti menusunu gosterir"),
    telebot.types.BotCommand("/oncekigun", "Onceki gunun kahvalti menusunu gosterir"),
    telebot.types.BotCommand("/bugunkuaksamyemegi", "Bugunku aksam yemegi menusunu gosterir"),
    telebot.types.BotCommand("/sonrakigunaksamyemegi", "Sonraki gunun aksam yemegi menusunu gosterir"),
    telebot.types.BotCommand("/oncekigunaksamyemegi", "Onceki gunun aksam yemegi menusunu gosterir"),
    telebot.types.BotCommand("/komutlar", "Bu mesaji tekrar gosterir"),
    telebot.types.BotCommand("/gelistirici", "citirin linkedln")
]

bot.set_my_commands(commands)

# Kahvaltı menüsünü oku
breakfast_menu_df = pd.read_csv('breakfast_menu_cleaned.csv')

# Akşam yemeği menüsünü oku
dinner_menu_df = pd.read_csv('aksam.csv')

# Kahvaltı menülerini bir sözlükte sakla
breakfast_menu_dict = {}
date_formats = ["%d %B %Y"]

for index, row in breakfast_menu_df.iterrows():
    date_str = row['Date']
    parsed = False
    for date_format in date_formats:
        try:
            date = datetime.strptime(date_str, date_format)
            breakfast_menu_dict[date.strftime("%d %B %Y")] = row
            parsed = True
            break
        except ValueError as e:
            continue
    if not parsed:
        print(f"Tarih formati hatasi: {date_str}")

# Akşam yemeği menülerini bir sözlükte sakla
dinner_menu_dict = {}

for index, row in dinner_menu_df.iterrows():
    date_str = row['Tarih']
    parsed = False
    for date_format in date_formats:
        try:
            date = datetime.strptime(date_str, date_format)
            dinner_menu_dict[date.strftime("%d %B %Y")] = row
            parsed = True
            break
        except ValueError as e:
            continue
    if not parsed:
        print(f"Tarih formati hatasi: {date_str}")

# Bugünkü tarihi al
today = datetime.today().strftime("%d %B %Y")
day = datetime.today()
dinner_day = datetime.today()

def get_dinner_menu_for_date(menu_dict, date_str):
    menu = menu_dict.get(date_str)
    if menu is not None:
        return f"""
        {menu['Tarih']} Aksam Yemegi Menusu:
        Corba: {menu['Corba']}
        Yemek: {menu['Yemek']}
        Pilav: {menu['Pilav']}
        Tatli: {menu['Tatli']}
        Su: {menu['Su']}
        Ekmek: {menu['Ekmek']}
        Kalori: {menu['Kalori']}
        """
    else:
        return "Bu tarih için aksam yemeği menüsü bulunamadı."


def get_menu_for_date(menu_dict, date_str):
    menu = menu_dict.get(date_str)
    if menu is not None:
        return f"""
        {menu['Date']} Menusu:
        Ana Yemek: {menu['Main Dish']}
        Peynir Cesidi: {menu['Cheese Type']}
        Zeytin: {menu['Olives']}
        Surulebilir: {menu['Spreads']}
        Ekstra: {menu['Extra Item']}
        Su: {menu['Water']}
        Ekmek: {menu['Bread']}
        Kalori: {menu['Calories']}
        """
    else:
        return "Bu tarih için menü bulunamadı."

@bot.message_handler(commands=['ben_gulnarliyim'])
def hello(message):
    bot.send_message(message.chat.id, "gardasim benim adamin dibisin")

@bot.message_handler(commands=['gelistirici'])
def gelistirici(message):
    bot.send_message(message.chat.id, "https://www.linkedin.com/in/zaferemrekilinc/")


@bot.message_handler(commands=['yarinkikahvalti'])
def tomorrow_breakfast(message):
    global day
    day = datetime.today() + timedelta(days=1)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Kahvaltı', callback_data='oncekigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Kahvaltı', callback_data='sonrakigun'))
    tomorrow = (datetime.today() + timedelta(days=1)).strftime("%d %B %Y")
    breakfast = get_menu_for_date(breakfast_menu_dict, tomorrow)
    bot.send_message(message.chat.id, breakfast, reply_markup=markup)


# Kahvaltı Menüsü Komutları
@bot.message_handler(commands=['bugunkukahvalti'])
def today_breakfast(message):
    global day
    day = datetime.today()
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Kahvaltı', callback_data='oncekigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Kahvaltı', callback_data='sonrakigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Akşam Yemeği', callback_data='bugunkuaksamyemegi'))
    breakfast = get_menu_for_date(breakfast_menu_dict, day.strftime("%d %B %Y"))
    bot.send_message(message.chat.id, breakfast, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'sonrakigun')
def callback_next_day(call):
    global day
    day += timedelta(days=1)
    next_day = day.strftime("%d %B %Y")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Kahvaltı', callback_data='oncekigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Kahvaltı', callback_data='sonrakigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Akşam Yemeği', callback_data='bugunkuaksamyemegi'))
    breakfast = get_menu_for_date(breakfast_menu_dict, next_day)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=breakfast, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'oncekigun')
def callback_previous_day(call):
    global day
    day -= timedelta(days=1)
    previous_day = day.strftime("%d %B %Y")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Kahvaltı', callback_data='oncekigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Kahvaltı', callback_data='sonrakigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Akşam Yemeği', callback_data='bugunkuaksamyemegi'))
    breakfast = get_menu_for_date(breakfast_menu_dict, previous_day)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=breakfast, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'bugunkuaksamyemegi')
def callback_today_dinner(call):
    global dinner_day
    dinner_day = day
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Akşam Yemeği', callback_data='oncekigunaksamyemegi'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Akşam Yemeği', callback_data='sonrakigunaksamyemegi'))
    markup.add(telebot.types.InlineKeyboardButton(text='Kahvaltı', callback_data='bugunkukahvalti'))
    dinner = get_dinner_menu_for_date(dinner_menu_dict, dinner_day.strftime("%d %B %Y"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dinner, reply_markup=markup)

# Akşam Yemeği Menüsü Komutları
@bot.message_handler(commands=['bugunkuaksamyemegi'])
def today_dinner(message):
    global dinner_day
    dinner_day = datetime.today()
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Akşam Yemeği', callback_data='oncekigunaksamyemegi'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Akşam Yemeği', callback_data='sonrakigunaksamyemegi'))
    markup.add(telebot.types.InlineKeyboardButton(text='Kahvaltı', callback_data='bugunkukahvalti'))
    dinner = get_dinner_menu_for_date(dinner_menu_dict, dinner_day.strftime("%d %B %Y"))
    bot.send_message(message.chat.id, dinner, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'sonrakigunaksamyemegi')
def callback_next_day_dinner(call):
    global dinner_day
    dinner_day += timedelta(days=1)
    next_day = dinner_day.strftime("%d %B %Y")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Akşam Yemeği', callback_data='oncekigunaksamyemegi'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Akşam Yemeği', callback_data='sonrakigunaksamyemegi'))
    markup.add(telebot.types.InlineKeyboardButton(text='Kahvaltı', callback_data='bugunkukahvalti'))
    dinner = get_dinner_menu_for_date(dinner_menu_dict, next_day)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dinner, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'oncekigunaksamyemegi')
def callback_previous_day_dinner(call):
    global dinner_day
    dinner_day -= timedelta(days=1)
    previous_day = dinner_day.strftime("%d %B %Y")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Akşam Yemeği', callback_data='oncekigunaksamyemegi'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Akşam Yemeği', callback_data='sonrakigunaksamyemegi'))
    markup.add(telebot.types.InlineKeyboardButton(text='Kahvaltı', callback_data='bugunkukahvalti'))
    dinner = get_dinner_menu_for_date(dinner_menu_dict, previous_day)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=dinner, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'bugunkukahvalti')
def callback_today_breakfast(call):
    global day
    day = dinner_day
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(telebot.types.InlineKeyboardButton(text='Önceki Kahvaltı', callback_data='oncekigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Sonraki Kahvaltı', callback_data='sonrakigun'))
    markup.add(telebot.types.InlineKeyboardButton(text='Akşam Yemeği', callback_data='bugunkuaksamyemegi'))
    breakfast = get_menu_for_date(breakfast_menu_dict, day.strftime("%d %B %Y"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=breakfast, reply_markup=markup)

# Komutları göster
@bot.message_handler(commands=['komutlar'])
def komutlari_goster(message):
    """Kullanıcıya kullanabilecekleri komutları gösteren bir mesaj gönderir."""
    kullanilabilir_komutlar = """
    *Kullanılabilir Komutlar:*

    /ben\_gulnarliyim \- Sana bir mesaj verir
    /bugunkukahvalti \- Bugünkü kahvaltı menüsünü gösterir
    /yarinkukahvalti \- Yarınki kahvaltı menüsünü gösterir
    /sonrakigun \- Sonraki günün kahvaltı menüsünü gösterir
    /oncekigun \- Önceki günün kahvaltı menüsünü gösterir
    /bugunkuaksamyemegi \- Bugünkü akşam yemeği menüsünü gösterir
    /sonrakigunaksamyemegi \- Sonraki günün akşam yemeği menüsünü gösterir
    /oncekigunaksamyemegi \- Önceki günün akşam yemeği menüsünü gösterir
    /gelistirici \- citirin linkedln
    /komutlar \- Bu mesajı tekrar gösterir
    """
    bot.send_message(message.chat.id, kullanilabilir_komutlar, parse_mode='MarkdownV2')


bot.polling()

