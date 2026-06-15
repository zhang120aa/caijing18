import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import logging
import asyncio

load_dotenv()
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ============ 多频道配置 ============
CHANNEL_IDS_STR = os.getenv("TELEGRAM_CHANNEL_ID", "-1001234567890")
CHANNEL_IDS = [int(ch.strip()) for ch in CHANNEL_IDS_STR.split(",") if ch.strip()]

CHANNEL_NAMES = {
    -1001234567890: "Financial_Express",
}

DB_DIR = "/app/data"
LINKS_FILE = os.path.join(DB_DIR, "telegram_links.json")

os.makedirs(DB_DIR, exist_ok=True)

def save_link(url, text="", channel_id=None, channel_name="Unknown"):
    """保存链接到 JSON 文件"""
    links = []
    if os.path.exists(LINKS_FILE):
        try:
            with open(LINKS_FILE, 'r', encoding='utf-8') as f:
                links = json.load(f)
        except json.JSONDecodeError:
            links = []
    
    if not any(link.get('url') == url for link in links):
        links.append({
            'url': url,
            'text': text[:100],
            'channel_id': channel_id,
            'channel_name': channel_name,
            'date': datetime.now().isoformat(),
        })
        
        links = sorted(links, key=lambda x: x['date'], reverse=True)
        
        with open(LINKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(links, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ [Bot] [{channel_name}] 保存链接: {url}")
        return True
    else:
        logger.debug(f"⏭️ [Bot] 链接已存在，跳过: {url}")
        return False

def get_channel_name(channel_id):
    """获取频道名称"""
    return CHANNEL_NAMES.get(channel_id, f"Channel_{channel_id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """接收频道消息"""
    message = update.channel_post
    
    if not message or not message.text:
        return
    
    if message.chat_id not in CHANNEL_IDS:
        return
    
    text = message.text
    channel_name = get_channel_name(message.chat_id)
    
    words = text.split()
    links_found = 0
    
    for word in words:
        if word.startswith(('http://', 'https://', 't.me')):
            if word.startswith('t.me'):
                url = 'https://' + word
            elif word.startswith('http'):
                url = word
            else:
                url = 'https://' + word
            
            url = url.rstrip('.,;:!?）)】')
            
            if save_link(url, text, message.chat_id, channel_name):
                links_found += 1
    
    if links_found > 0:
        logger.info(f"📨 [Bot] [{channel_name}] 消息处理完成，发现 {links_found} 个链接")

async def run_bot():
    """异步运行 Bot - 返回 coroutine，不使用 asyncio.run()"""
    if not BOT_TOKEN:
        logger.error("❌ [Bot] 缺少 TELEGRAM_BOT_TOKEN")
        return
    
    if not CHANNEL_IDS:
        logger.error("❌ [Bot] 缺少 TELEGRAM_CHANNEL_ID")
        return
    
    logger.info("=" * 60)
    logger.info("🤖 [Bot] Telegram 机器人启动")
    logger.info("=" * 60)
    logger.info(f"📡 监听的频道数: {len(CHANNEL_IDS)}")
    for ch_id in CHANNEL_IDS:
        logger.info(f"   - {get_channel_name(ch_id)} (ID: {ch_id})")
    logger.info(f"💾 链接保存位置: {LINKS_FILE}")
    logger.info("=" * 60)
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ [Bot] 等待新消息...\n")
    
    await app.run_polling()

def get_bot_coroutine():
    """供外部调用：返回 Bot 的 coroutine"""
    return run_bot()

if __name__ == '__main__':
    asyncio.run(run_bot())
