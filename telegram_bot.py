import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters, CommandHandler
from telegram.error import TelegramError
import config
from database import save_news
from deduplicator import deduplicator
from tagger import tagger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram 爬虫机器人"""
    
    def __init__(self):
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """设置处理器"""
        # 处理频道消息
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        # 处理启动命令
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help_command))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """启动命令"""
        await update.message.reply_text(
            "🤖 财经机器人已启动！\n"
            "正在监听 Financial_Express 频道...\n"
            "使用 /help 查看帮助"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """帮助命令"""
        await update.message.reply_text(
            "📚 帮助信息\n\n"
            "机器人自动监听 @Financial_Express 频道\n"
            "去除重复内容，并分类标签\n\n"
            "前端访问: http://localhost:5000"
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理消息"""
        try:
            message = update.channel_post or update.message
            if not message or not message.text:
                return
            
            # 提取信息
            title = message.text[:100]  # 前100字作为标题
            content = message.text
            message_id = str(message.message_id)
            
            # 去重检查
            is_dup, reason = deduplicator.is_duplicate(title, content, message_id)
            if is_dup:
                logger.info(f"[去重] {reason}: {title[:50]}")
                return
            
            # 生成唯一ID
            news_id = deduplicator.generate_hash(content)
            
            # 提取标签
            tags = tagger.extract_tags(title, content)
            
            # 保存数据库
            success = save_news(
                news_id=news_id,
                title=title,
                content=content,
                tags=tags,
                message_id=message_id
            )
            
            if success:
                logger.info(f"[新闻] 已保存: {title[:50]}")
        
        except Exception as e:
            logger.error(f"[错误] 处理消息失败: {e}")
    
    async def run(self):
        """运行机器人"""
        logger.info("[启动] Telegram 机器人启动中...")
        try:
            await self.app.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"[错误] 机器人运行失败: {e}")
            # 自动重连
            await asyncio.sleep(5)
            await self.run()

def get_bot():
    return TelegramBot()
