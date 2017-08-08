from telegram.ext import Updater, CommandHandler
from re import match
from time import time
import sqlite3

DATABASE = "t.db"
master = 117543374
timeout = 5  # timeout for wrong killing code


def log(bot, msg):
    if type(msg) != str:
        msg = str(msg)
    bot.send_message(chat_id=master, text=msg)


def start(_, update):
    update.message.reply_text('Добро пожаловать в игру Киллер™ ЛШ 2017 в Дубне!'
                              '\nНапишите /login <code> чтобы зайти в игру (p.s <code>: r\'[A-Z0-9]{9}\')')


def login(_, update, args):
    user_id = str(update.message.chat_id)
    if len(args) != 1:
        update.message.reply_text("Используйте: /login <code>")
        return

    with sqlite3.connect(DATABASE) as con:
        args = args[0]
        fio = con.execute("SELECT fio FROM names WHERE pass=?", (args, )).fetchone()
        if match(r'[A-Z0-9]{9}', args) is None or fio is None:
            update.message.reply_text("Похоже ты ошибся с вводом кода")
            return

        if con.execute("SELECT count(*) FROM info WHERE pass=?", (args, )).fetchone()[0] > 0:
            update.message.reply_text("Этот аккаунт уже используется")
            return

        con.execute("INSERT INTO info VALUES (?, ?, 0)", (user_id, args))
        con.commit()
        update.message.reply_text('Добро пожаловать, {}'.format(fio[0]))


def target(bot, update):
    user_id = str(update.message.chat_id)
    with sqlite3.connect(DATABASE) as con:
        killer = con.execute("SELECT pass FROM info WHERE tg_id=?", (user_id,)).fetchone()[0]
        if con.execute("SELECT count(*) FROM kills WHERE killed_pass=?", (killer,)).fetchone()[0] > 0:
            update.message.reply_text("Увы, мертвые не могут убивать")
            return

        aim = con.execute("SELECT fio FROM names where pass="
                          "(SELECT aim FROM aims WHERE user_pass=?)", (killer, )).fetchone()

        if aim is None:
            update.message.reply_text("Что-то пошло не так, но мы уже вкурсе и скоро починим!")
            log(bot, user_id)
            return
        update.message.reply_text("Твоя цель: {}".format(aim[0]))


def kill(bot, update, args):
    user_id = str(update.message.chat_id)

    if len(args) != 1 or match(r'[A-Z0-9]{9}', args[0]) is None:
        update.message.reply_text("Используйте: /kill [A-Z0-9]{9}")
        return

    args = args[0]
    with sqlite3.connect(DATABASE) as con:
        t, killer = con.execute("SELECT last_try, pass FROM info WHERE tg_id=?", (user_id,)).fetchone()
        if time() - t < timeout:
            update.message.reply_text("Зря брутил, за тобой уже выехали")
            log(bot, "bf attempt: {}".format(killer))
            return

        if con.execute("SELECT count(*) FROM kills WHERE killed_pass=?", (killer,)).fetchone()[0] > 0:
            update.message.reply_text("Увы, мертвые не могут убивать")
            return

        aim = con.execute("SELECT aim FROM aims WHERE user_pass=? and aim=?", (killer, args)).fetchone()

        if aim is None:
            update.message.reply_text("Неверный код.")
            con.execute("UPDATE info SET last_try=? WHERE pass=?", (time(), killer))
            return

        aim = aim[0]

        aim_of_aim = con.execute("SELECT aim FROM aims WHERE user_pass=?", (aim, )).fetchone()[0]
        con.execute("UPDATE aims SET aim=? WHERE user_pass=?", (aim_of_aim, killer))
        con.execute("INSERT INTO kills VALUES (?,?,?)", (killer, aim, int(time() * 1000)))
        con.commit()

        tg = con.execute("SELECT tg_id FROM info WHERE pass=?", (aim,)).fetchone()
        if tg is None:
            return
        name = con.execute("SELECT fio FROM names WHERE pass=?", (killer,)).fetchone()[0]
        bot.send_message(chat_id=tg[0],
                         text="Тебя убил {}!".format(name))


def stat(_, update):
    user_id = str(update.message.chat_id)
    with sqlite3.connect(DATABASE) as con:
        kills = con.execute("SELECT count(*) from kills where pass="
                            "(SELECT pass FROM info where tg_id=?)", (user_id, )).fetchone()[0]

        msg = "Уже убито тобой: {}\n"
        if kills == 0:
            msg += "Не отчаивайся, у тебя все получится!"
        elif kills > 1:
            msg += "Хорошее начало для успешной карьеры ассасина!"
        elif kills > 5:
            msg += "Продолжай в том же духе и сможешь победить"
        elif kills > 9:
            msg += "Да с тобой опасно иметь дело! Такими темпами вокруг тебя будут одни трупы"
        elif kills > 14:
            msg += "Можешь определенно считать себя героем этой игры"
        elif kills > 21:
            msg += "В общем ты очень и очень крут и мне лень придумывать дальше сообщеньки :("

        update.message.reply_text(msg.format(kills))


def top(_, update):
    with sqlite3.connect(DATABASE) as con:
        cur = con.execute("SELECT "
                          "  (SELECT fio FROM names WHERE names.pass=kills.pass),"
                          "  count(killed_pass) "
                          "FROM kills GROUP BY pass ORDER BY count(killed_pass) DESC;")
        s = "Текущий топ5 киллеров:\n\n"
        for c in cur:
            try:
                s += '\t' + c[0] + " " + str(c[1]) + '\n'
            except:
                break
        update.message.reply_text(s)


def contact(_, update):
    update.message.reply_text("Если что-то пошло не так можно обратиться к @kitsu")


def help(_, update):
    update.message.reply_text("Игровые команды: target, kill, stat, top\n"
                              "При возникновении проблем смотрите в /contact")


updater = Updater('406219111:AAEpkp-IK1IJI1ZrMKS7uisY_2RUMBDs0d8')


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('login', login, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('target', target))
updater.dispatcher.add_handler(CommandHandler('kill', kill, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('stat', stat))
updater.dispatcher.add_handler(CommandHandler('top', top))
updater.dispatcher.add_handler(CommandHandler('contact', contact))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('h', help))

updater.start_polling()
updater.idle()

