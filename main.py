from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import youtube_dl


def hello(update, context):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))
def ps(update, context):
    print(update)
    update.message.reply_text(update.message.text)

updater = Updater('token', use_context=True)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(MessageHandler(filters.Filters.text, ps))

updater.start_polling()
updater.idle()