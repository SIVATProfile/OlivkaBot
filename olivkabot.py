import telegram.ext
import os
import logging
import datetime
import requests
import bs4


def logger_setup(log_level: str = "INFO") -> logging.Logger:
    _logger = logging.getLogger()
    _logger.setLevel(log_level)
    _logger.propagate = False
    if not _logger.hasHandlers():
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt=f"[%(asctime)s][%(levelname)-7s][%(funcName)s] %(message)s")
        _logger.addHandler(stream_handler)
        stream_handler.setFormatter(formatter)
    return _logger


logger = logger_setup(log_level="DEBUG")


def get_weekday_menu(weekday: str):
    weekday_list = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    try:
        weekday = weekday_list.index(weekday)
    except ValueError:
        logger.error(f"Weekday name '{weekday}' is wrong!")
        raise
    response = requests.get('https://m.olivkafood.ru/produkciya/bizneslanch/')
    status = response.status_code
    if status != 200:
        logger.error(f"Request to 'https://m.olivkafood.ru/produkciya/bizneslanch/' failed!!!")
    soup = bs4.BeautifulSoup(response.text, features='html.parser')
    menu_html = soup.body.find('div',
                               attrs={'class': f'menu-item mix menu-category-filter c{weekday + 1}'}).find_all(
        'div', attrs={'class': 'extended-item'})
    del menu_html[0]
    menu_list = list()
    for position in menu_html:
        position_name = position.find('div', attrs={'class': 'item-name'})
        position_portion = position.find('div', attrs={'class': 'item-portion'})
        if position_portion:
            menu_list.append(f"{position_name.text.capitalize()} ({position_portion.text})")
        else:
            menu_list.append(f"{position_name.text.capitalize()}")
    return menu_list


def get_menu(weekday: str):
    menu_list = get_weekday_menu(weekday=weekday)
    menu_text = 'Ланч в кафе "Оливка" на сегодня:'
    for item in menu_list:
        menu_text = f"{menu_text}\n - {item}"
    menu_text = f"{menu_text}\nПриятного аппетита!"
    return menu_text


def get_token():
    token = os.environ.get("API_TOKEN", None)
    if not token:
        logger.error(f"Environment variable 'API_TOKEN' not found")
        raise ValueError
    logger.debug(f"API TOKEN is {token}")
    return token


def callback_notify(context: telegram.ext.CallbackContext):
    weekday_name = datetime.datetime.today().strftime("%A")
    message = get_menu(weekday=weekday_name)
    context.bot.send_message(chat_id=context.job.context, text=message)


def start_command(update: telegram.Update, context: telegram.ext.CallbackContext):
    jobs = context.job_queue.jobs()
    if len(jobs) > 0:
        logger.error(f"JOB ALREADY STARTED!!!")
        job = context.job_queue.jobs()[0]
        job.schedule_removal()
    notify_time = datetime.time(hour=3, minute=0, second=0)
    context.job_queue.run_daily(callback=callback_notify, days=tuple(range(5)), context=update.message.chat_id,
                                time=notify_time)
    context.bot.send_message(chat_id=update.message.chat_id, text='Для данного канала добавлена рассылка о составе '
                                                                  'ланча в кафе "Оливка. Рассылка проводится по будням'
                                                                  ' в 10:00')


def stop_command(update: telegram.Update, context: telegram.ext.CallbackContext):
    jobs = context.job_queue.jobs()
    if len(jobs) > 0:
        job = context.job_queue.jobs()[0]
        job.schedule_removal()
    else:
        pass
    context.bot.send_message(chat_id=update.message.chat_id, text='Рассылка информации о составе ланча в кафе "Оливка" '
                                                                  'отключена для данного канала')


def start_bot():
    token = get_token()
    updater = telegram.ext.Updater(token=token)
    dispatcher = updater.dispatcher

    start_command_handler = telegram.ext.CommandHandler('start', start_command)
    stop_message_handler = telegram.ext.CommandHandler('stop', stop_command)
    dispatcher.add_handler(start_command_handler)
    dispatcher.add_handler(stop_message_handler)

    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    start_bot()
