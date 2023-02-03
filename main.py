import time
import pytz
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

API_TOKEN = "6122198842:AAEnIcyxCUQk5bW_VVzZrfcsRBRzfVOuQT0"

bot = telebot.TeleBot(API_TOKEN)
reminders = {}
warsaw_timezone = pytz.timezone("Europe/Warsaw")


def send_reminders(bot, chat_id, reminder_texts):
    bot.send_message(chat_id, "It's 7 AM in Warsaw. Here are your reminders:")
    for reminder_text in reminder_texts:
        bot.send_message(chat_id, reminder_text)
    reminders[chat_id] = []


@bot.message_handler(commands=['start'])
def start_handler(message):
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item_set_reminder = telebot.types.KeyboardButton("Set Reminder")
    item_display_reminders = telebot.types.KeyboardButton("Display Reminders")
    item_help = telebot.types.KeyboardButton("Help")
    markup.add(item_set_reminder, item_display_reminders, item_help)
    bot.send_message(chat_id,
                     "Hello! I am your daily reminder bot. I will remind you to do your tasks every day at 7:00 AM in "
                     "Warsaw. Use the buttons below to set reminders, display reminders or delete reminders using the "
                     "/delete_reminder command. Type 'Help' for more information.",
                     reply_markup=markup)
    reminders[chat_id] = []
    scheduler.add_job(send_reminders,
                      args=[bot, chat_id, reminders[chat_id]],
                      trigger=CronTrigger(hour=7, minute=0, timezone=warsaw_timezone),
                      id=str(chat_id))


@bot.message_handler(func=lambda message: message.text == "Set Reminder")
def set_reminder(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "What would you like to be reminded about?")
    bot.register_next_step_handler(message, set_reminder_task)


def set_reminder_task(message):
    chat_id = message.chat.id
    if message.text == "Display Reminders":
        display_reminders(message)
    elif message.text == "Help":
        help_message(message)
    else:
        if chat_id not in reminders:
            reminders[chat_id] = []
        reminders[chat_id].append(message.text)
        bot.send_message(chat_id, "Reminder added.")


@bot.message_handler(func=lambda message: message.text == "Display Reminders")
def display_reminders(message):
    chat_id = message.chat.id
    if chat_id not in reminders or not reminders[chat_id]:
        bot.send_message(chat_id, "You don't have any reminders set.")
    else:
        reminder_text = "\n".join(reminders[chat_id])
        bot.send_message(chat_id, "Here are your reminders:\n" + reminder_text)


@bot.message_handler(commands=['delete_reminder'])
def delete_reminder_handler(message):
    chat_id = message.chat.id
    if chat_id not in reminders or not reminders[chat_id]:
        bot.send_message(chat_id, "You don't have any reminders to delete.")
    else:
        bot.send_message(chat_id, "Which reminder would you like to delete? Please enter the number of the reminder.")
        bot.register_next_step_handler(message, delete_reminder)


def delete_reminder(message):
    chat_id = message.chat.id
    if message.text == "Display Reminders":
        display_reminders(message)
    else:
        try:
            reminder_index = int(message.text) - 1
            if 0 <= reminder_index < len(reminders[chat_id]):
                del reminders[chat_id][reminder_index]
                bot.send_message(chat_id, "Reminder deleted.")
            else:
                bot.send_message(chat_id, "Invalid reminder number.")
        except ValueError:
            bot.send_message(chat_id, "Invalid input. Please enter a number.")


def help_message(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     "Use the buttons to set reminders or display reminders. You can also delete reminders by using "
                     "the /delete_reminder command. Reminders will be sent every day at 7:00 AM in Warsaw.")


@bot.message_handler(func=lambda message: message.text == "Help" or message.text == "help")
def help(message):
    help_message(message)


scheduler = BackgroundScheduler()
scheduler.start()

while True:
    try:
        bot.polling()
    except Exception as e:
        if "429" in str(e):
            time.sleep(60)
