from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, CommandHandler, MessageHandler, \
    Filters, CallbackQueryHandler, InlineQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, \
    InlineQueryResultArticle, ParseMode, InputTextMessageContent
from uuid import uuid4

import logging

from .translate import translate
from .messages import MESSAGE
from . import config


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    keyboard = update_keyboard('start')
    update.message.reply_text(
        MESSAGE['BR']['start'], reply_markup=keyboard)


def help(bot, update):
    """Send a message when the command /help is issued."""
    keyboard = update_keyboard('help')
    update.message.reply_text(
        MESSAGE['BR']['help'], reply_markup=keyboard)


def about(bot, update):
    """Send a message when the command /about is issued."""
    keyboard = update_keyboard('about')
    update.message.reply_text(
        MESSAGE['BR']['about'], reply_markup=keyboard)


def translation(bot, update):
    """Translate the user message to 'dinosaurese'."""
    text_translated = translate(update.message.text)
    update.message.reply_text(text_translated)


def update_keyboard(message):
    lang_keyboard = [[InlineKeyboardButton("🇧🇷", callback_data=f'BR/{message}'),
                      InlineKeyboardButton("🇺🇸", callback_data=f'EN/{message}')]]
    reply_keyboard = InlineKeyboardMarkup(lang_keyboard)
    return reply_keyboard


def button(bot, update):
    query = update.callback_query
    language, message = query.data.split("/")
    bot.edit_message_text(text=MESSAGE[language][message],
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          reply_markup=update_keyboard(message))


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    one_f = translate(query, remove=True)
    more_f = translate(query, remove=False)
    if one_f == more_f:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="F",
                input_message_content=InputTextMessageContent(
                    one_f))]
    else:
        results = [
            InlineQueryResultArticle(
                id=uuid4(),
                title="1F",
                input_message_content=InputTextMessageContent(
                    one_f)),
            InlineQueryResultArticle(
                id=uuid4(),
                title=f"+F",
                input_message_content=InputTextMessageContent(
                    more_f))]

    update.inline_query.answer(results)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def run_bot():
    """Start the bot."""

    updater = Updater(config['TELEGRAM_TOKEN'])
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("translate", translation))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(InlineQueryHandler(inlinequery))

    dp.add_handler(MessageHandler(Filters.text, translation))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()