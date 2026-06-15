import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DB_DIR = "/app/data"
LINKS_FILE = os.path.join(DB_DIR, "telegram_links.json")

os.makedirs(DB_DIR, exist_ok=True)

def save_link(url, text=""):
    """保存链接到 JSON 文件"""
    links = []
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            links = json.load(f)
    
    # 避免重复
    if not any(link.get('url') == url for link in links):
        links.append({
            'url': url,
            'text': text[:100],
            'date': datetime.now().isoformat(),
        })
        with open(LINKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ [Bot] 保存链接: {url}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """接收频道消息"""
    message = update.channel_post
    
    if message and message.text:
        text = message.text
        # 提取所有链接
        words = text.split()
        for word in words:
            if word.startswith(('http://', 'https://', 't.me')):
                if not word.startswith('http'):
                    word = 'https://' + word
                save_link(word, text)

async def run_bot():
    """异步运行 Bot"""
    if not BOT_TOKEN:
        logger.error("❌ [Bot] 缺少 TELEGRAM_BOT_TOKEN")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🤖 [Bot] 机器人启动，监听 Financial_Express 频道...")
    await app.run_polling()

def main():
    """主函数（供 main.py 调用）"""
    import asyncio
    try:
        asyncio.run(run_bot())
    except Exception as e:
        logger.error(f"❌ [Bot] 错误: {e}", exc_info=True)

if __name__ == '__main__':
    main()
