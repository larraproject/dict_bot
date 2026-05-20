import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes, 
    MessageHandler, filters
)
from api_client import fetch_definition

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Привет! Я бот-словарь.\n"
        "Отправь команду /define <слово> на английском, чтобы получить определение.\n"
        "Пример: `/define serendipity`"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📚 **Доступные команды:**\n"
        "/start - Запустить бота\n"
        "/help - Показать справку\n"
        "/define <word> - Найти определение английского слова\n\n"
        "💡 Совет: Пиши слово латиницей без пробелов."
    )

async def define(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("🤔 Пожалуйста, укажи слово. Пример: `/define serendipity`")
        return

    word = " ".join(context.args).strip()
    await update.message.reply_text("⏳ Ищу определение...")
    
    success, result = await fetch_definition(word)
    if success:
        await update.message.reply_text(result)
    else:
        await update.message.reply_text(result)

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("❓ Неизвестная команда. Используйте /help для списка команд.")

def main() -> None:
    # Инициализация приложения
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("define", define))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Автоматическое определение режима: Webhook (для Render) или Polling (локально)
    webhook_url = os.getenv("WEBHOOK_URL")
    render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    
    if webhook_url or render_host:
        final_webhook = webhook_url or f"https://{render_host}/{BOT_TOKEN}"
        print(f"🌐 Запуск в режиме Webhook: {final_webhook}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=final_webhook
        )
    else:
        print("📡 Запуск в режиме Polling (локальная разработка)...")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()