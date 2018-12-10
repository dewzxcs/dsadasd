from pylibgen import Library
from emoji import emojize
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
Library.mirror = "http://gen.lib.rus.ec"
l = Library()

updater = Updater(token='685085857:AAEclwC7ZKr_OY6f2F8DQIpalToXb_uszTU') # Токен API к Telegram
dispatcher = updater.dispatcher


# Обработка команд
def startCommand(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Привет, я бот для поиска научных книг. Напиши мне ее название.')


def textMessage(bot, update):
    bot.sendChatAction(update.message.chat_id, 'typing')
    mes = update.message.text
    global ids
    if mes.isdigit():
        if len(ids) >= int(mes) > 0:
            download_mes = 'Книга #' + mes + ':'
            s = "http://gen.lib.rus.ec/json.php?ids=&fields=Title,MD5"
            index = s.find('ids=')
            output_line = s[:index + 4] + ids[int(mes) - 1] + "&fields=MD5,Title"
            response = requests.get(output_line)
            o = response.text
            md5 = o.split('"')[3]
            title = o.split('"')[7]
            down_linc = 'http://gen.lib.rus.ec/get.php?md5=' + md5
            download_mes += '\n' + title
            bot.send_message(chat_id=update.message.chat_id, text = download_mes + '\n' + down_linc)
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Вы ввели неправильный номер. Попробуйте еще раз.')

    else:
        ids = l.search(mes)
        if len(ids) == 0:
            bot.send_message(chat_id=update.message.chat_id, text='Я не нашел ни одной книги по вашему запросу. ')
        else:
            if len(ids) > 50:
                bot.send_message(chat_id=update.message.chat_id,
                                 text='Я нашел слишком много книг по вашему запросу, '
                                      'поэтому выведу первые 50. Попробуйте уточнить ваш запрос.')
                ids = ids[:50]
            firstlane = 'По вашему запросу найдено: ' + str(len(ids)) + emojize(" :books:", use_aliases=True)
            blist = ''
            k = 0
            for i in ids:
                k += 1
                s = "http://gen.lib.rus.ec/json.php?ids=&fields=Title,MD5"
                index = s.find('ids=')
                output_line = s[:index + 4] + i + "&fields=MD5,Title"
                response = requests.get(output_line)
                o = response.text
                title = o.split('"')[7]
                blist += str(k)
                blist += ') '
                blist += title
                blist += "\n"
            blist += "\n"
            blist += "Введите номер книги, которую хотите скачать."
            firstlane += '\n' + '\n' + blist
            bot.send_message(chat_id=update.message.chat_id, text=str(firstlane))


def bookMessage(bot, update):
    response = 'Вот что мне удалось найти по вашему запросу: '
    bot.send_message(chat_id=update.message.chat_id, text=response)
    ids = l.search(update.message.text)
    for i in ids:
        s = "http://gen.lib.rus.ec/json.php?ids=&fields=Title,MD5"
        index = s.find('ids=')
        output_line = s[:index + 4] + i + "&fields=MD5,Title"
        response = requests.get(output_line)
        o = response.text
        md5 = o.split('"')[3]
        title = o.split('"')[7]
        down_linc = 'http://gen.lib.rus.ec/get.php?md5=' + md5
        bot.send_message(chat_id=update.message.chat_id, text=title + ' | ' + down_linc)


# Хендлеры
start_command_handler = CommandHandler('start', startCommand)
text_message_handler = MessageHandler(Filters.text, textMessage)
# Добавляем хендлеры в диспетчер
dispatcher.add_handler(start_command_handler)
dispatcher.add_handler(text_message_handler)

# Начинаем поиск обновлений
updater.start_polling(clean=True)
# Останавливаем бота, если были нажаты Ctrl + C
updater.idle()
