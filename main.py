import random

from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
import time
from random import randint
from telegram import Update
from telegram import ReplyKeyboardMarkup

print('Starting up bot...')

TOKEN = '5717663577:AAH07J2eUJ6e6_gM-WOvuOOFNYK_Evk2i8Q'
BOT_USERNAME = '@kimchi_gangbot'
reply_keyboard = [['/timer', '/dicer']]
markup1 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
dice_keyboard = [['/dice 6', '/dice 6 2'], ['/dice 20', '/back']]
markup2 = ReplyKeyboardMarkup(dice_keyboard, one_time_keyboard=False)
timer_keyboard = [['/time 30', '/time 60'], ['/time 120', '/back']]
markup3 = ReplyKeyboardMarkup(timer_keyboard, one_time_keyboard=False)
anekdots = ['Программист звонит в библиотеку.— Здравствуйте, Катю можно?\n— Она в архиве.\n— Разархивируйте ее пожалуйста. Она мне срочно нужна!',
            'Работа программиста и шамана имеет много общего — оба бормочут непонятные слова, совершают непонятные действия и не могут объяснить, как оно работает.',
            'Приходит программист к другу—пианисту — посмотреть на новый рояль. Долго ходит вокруг, хмыкает, потом заявляет:\n— Клава неудобная — всего 84 клавиши, половина функциональных, ни одна не подписана; хотя... шифт нажимать ногой — оригинально...',
            'Программисты на работе общаются двумя фразами: «непонятно» и «вроде работает».',
            'После напряженного трудового дня, программист открывает холодильник, берет пачку масла, читает на обертке: "Масло сливочное. 72%". Вголовусразуприходитмысль: "О! Скоро загрузится!" Возвращает масло назад в холодильник и закрывает дверцу.'
            ]


def start(update, context):
    update.message.reply_text(
        "Привет! Я бот, который умеет кидать кости и запускать таймер!", reply_markup=markup1)


async def help_command(update: Update, context):
    await update.message.reply_text('Это бот всячины Кимчи')


async def custom_command(update: Update, context):
    await update.message.reply_text('soon /. /. /.')


def dicer(update, context):
    update.message.reply_text('Выберети кубик', reply_markup=markup2)


def dice(update, context):
    try:
        n = 1 if len(context.args) < 2 else int(context.args[1])
        s = ', '.join([str(randint(1, int(context.args[0]))) for i in range(n)])
        update.message.reply_text(f'Результат бросков: {s}')
    except Exception as exe:
        update.message.reply_text('Использование: /dice <кол. граней> <кол. бросков>\n'
                                  'Количество бросков ро умолчанию 1')


def echo(update, context):
    message_type = str(update.message.chat.type)
    text = str(update.message.text)

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = str(text.replace(BOT_USERNAME, '').strip())
            response = str(handle_response(new_text))
        else:
            return
    else:
        response = str(handle_response(text))

    print(f'Bot:', response)
    update.message.reply_text(response)


def task(context):
    job = context.job
    context.bot.send_message(job.context, text='Время истекло!')


def timer(update, context):
    update.message.reply_text('Выберети время', reply_markup=markup3)


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def time(update, context):
    chat_id = update.message.chat_id
    try:
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Извините, не умеем возвращаться в прошлое')
            return
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(task, due, context=chat_id, name=str(chat_id))
        text = f'Засёк!'
        if job_removed:
            text += ' Старый таймер удален.'
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /timer <секунд>')


def back(update, context):
    return start(update, context)


def handle_response(text):
    processed = str(text.lower())

    if 'привет' in processed or 'здравствуй' in processed:
        return random.choice(['Привет!', 'Здравствуй!', 'Добрый день!'])

    if 'как дела' in processed or 'как твои дела' in processed:
        return 'Все отлично!'

    if 'анекдот' in processed:
        return random.choice(anekdots)

    return 'Я не понимаю'


async def error(update: Update, context):
    print(f'Update {update} caused error {context.error}')


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    text_handler = MessageHandler(Filters.text & ~Filters.command, echo)

    dp.add_handler(text_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("timer", timer))
    dp.add_handler(CommandHandler("time", time, pass_args=True,
                                  pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("dicer", dicer))
    dp.add_handler(CommandHandler("dice", dice, pass_args=True))
    dp.add_handler(CommandHandler("back", back))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
