import asyncio
import logging
import threading
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from database import cleanup_old_data, get_session, FinanceNews, get_database_info
from web.app import app
import config

# ============ 配置日志 ============
def setup_logging():
    """设置日志"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 确保日志目录存在
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    handlers = [
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

class FinanceBot:
    """主应用程序"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.web_thread = None
        self.bot_app = None
    
    def setup_scheduler(self):
        """设置定时任务"""
        # 每天凌晨3点清理过期数据
        self.scheduler.add_job(
            cleanup_old_data,
            'cron',
            hour=3,
            minute=0,
            id='cleanup_job',
            name='清理过期数据'
        )
        
        # 每小时更新一次统计
        self.scheduler.add_job(
            self.log_stats,
            'interval',
            hours=1,
            id='stats_job',
            name='输出统计信息'
        )
        
        self.scheduler.start()
        logger.info("✅ [调度器] 定时任务已启动")
    
    def log_stats(self):
        """输出统计信息"""
        try:
            info = get_database_info()
            logger.info(
                f"📊 [统计] 总数: {info['total']} | "
                f"数据库大小: {info['db_size_mb']:.2f}MB | "
                f"最新: {info['newest_news']}"
            )
        except Exception as e:
            logger.error(f"❌ [统计] 错误: {e}")
    
    def start_web_server(self):
        """启动Web服务"""
        self.web_thread = threading.Thread(
            target=lambda: app.run(
                host=config.FLASK_HOST,
                port=config.FLASK_PORT,
                debug=config.FLASK_DEBUG,
                use_reloader=False
            ),
            daemon=True
        )
        self.web_thread.start()
        logger.info(f"✅ [Web服务] 启动在 http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    
    def start_telegram_bot_sync(self):
        """在单独线程中启动Telegram机器人（同步包装）"""
        from telegram_bot import main as telegram_main
        
        bot_thread = threading.Thread(
            target=telegram_main,
            daemon=True
        )
        bot_thread.start()
        logger.info("✅ [Telegram] 机器人已启动")
    
    def run(self):
        """运行整个应用"""
        logger.info("=" * 60)
        logger.info("🚀 财经机器人启动")
        logger.info("=" * 60)
        logger.info(f"📂 数据目录: {config.APP_DATA_DIR}")
        logger.info(f"💾 数据库路径: {config.DB_PATH}")
        logger.info(f"🔗 数据库URL: {config.DATABASE_URL}")
        logger.info(f"📝 日志文件: {config.LOG_FILE}")
        logger.info("=" * 60)
        
        try:
            # 启动定时任务
            self.setup_scheduler()
            
            # 启动Web服务
            self.start_web_server()
            
            # 稍微延迟，确保Web服务启动
            import time
            time.sleep(2)
            
            # 启动Telegram机器人
            self.start_telegram_bot_sync()
            
            # 保持主线程运行
            logger.info("=" * 60)
            logger.info("✅ 所有服务已启动，按 Ctrl+C 停止")
            logger.info("=" * 60)
            
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\n⏹️ [关闭] 机器人正在关闭...")
            if self.scheduler.running:
                self.scheduler.shutdown()
            logger.info("✅ [关闭] 机器人已关闭")
        except Exception as e:
            logger.error(f"❌ [错误] 程序崩溃: {e}", exc_info=True)
        finally:
            if self.scheduler.running:
                self.scheduler.shutdown()

def main():
    """主入口"""
    finance_bot = FinanceBot()
    finance_bot.run()

if __name__ == '__main__':
    main()
