from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import config

Base = declarative_base()

class FinanceNews(Base):
    __tablename__ = 'finance_news'
    
    id = Column(String, primary_key=True, unique=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(100), default='Financial_Express')
    published_time = Column(DateTime, nullable=False)
    created_time = Column(DateTime, default=datetime.utcnow)
    tags = Column(String(200))  # JSON格式标签
    url = Column(String(500))
    message_id = Column(String(100))
    
    __table_args__ = (
        Index('idx_published_time', 'published_time'),
        Index('idx_created_time', 'created_time'),
        Index('idx_tags', 'tags'),
    )

# ============ 数据库初始化 ============
def init_database():
    """初始化数据库连接"""
    try:
        # 确保数据目录存在
        db_dir = config.APP_DATA_DIR
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # 创建引擎
        engine = create_engine(
            config.DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
        
        # 创建所有表
        Base.metadata.create_all(engine)
        
        print(f"✅ [数据库] 初始化成功: {config.DB_PATH}")
        return engine
    
    except Exception as e:
        print(f"❌ [数据库] 初始化失败: {e}")
        raise

# 初始化引擎和Session工厂
engine = init_database()
SessionLocal = sessionmaker(bind=engine)

def get_session():
    """获取数据库会话"""
    return SessionLocal()

def cleanup_old_data():
    """删除7天前的数据"""
    session = get_session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=config.DATA_RETENTION_DAYS)
        deleted = session.query(FinanceNews).filter(
            FinanceNews.created_time < cutoff_date
        ).delete()
        session.commit()
        print(f"✅ [数据清理] 删除了 {deleted} 条过期数据 (7天前)")
        return deleted
    except Exception as e:
        print(f"❌ [数据清理] 错误: {e}")
        session.rollback()
        return 0
    finally:
        session.close()

def save_news(news_id, title, content, tags, url=None, message_id=None):
    """保存新闻"""
    session = get_session()
    try:
        news = FinanceNews(
            id=news_id,
            title=title,
            content=content,
            tags=tags,
            url=url,
            message_id=message_id,
            published_time=datetime.utcnow()
        )
        session.add(news)
        session.commit()
        print(f"✅ [数据库] 保存新闻: {news_id}")
        return True
    except Exception as e:
        print(f"❌ [数据库] 保存失败: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def get_all_news(limit=100, offset=0):
    """获取所有新闻"""
    session = get_session()
    try:
        news = session.query(FinanceNews).order_by(
            FinanceNews.published_time.desc()
        ).limit(limit).offset(offset).all()
        return news
    except Exception as e:
        print(f"❌ [数据库] 查询失败: {e}")
        return []
    finally:
        session.close()

def search_news(keyword, limit=50):
    """搜索新闻"""
    session = get_session()
    try:
        results = session.query(FinanceNews).filter(
            (FinanceNews.title.like(f'%{keyword}%')) |
            (FinanceNews.content.like(f'%{keyword}%')) |
            (FinanceNews.tags.like(f'%{keyword}%'))
        ).order_by(FinanceNews.published_time.desc()).limit(limit).all()
        return results
    except Exception as e:
        print(f"❌ [数据库] 搜索失败: {e}")
        return []
    finally:
        session.close()

def get_news_by_tag(tag, limit=50):
    """按标签获取新闻"""
    session = get_session()
    try:
        results = session.query(FinanceNews).filter(
            FinanceNews.tags.like(f'%{tag}%')
        ).order_by(FinanceNews.published_time.desc()).limit(limit).all()
        return results
    except Exception as e:
        print(f"❌ [数据库] 按标签查询失败: {e}")
        return []
    finally:
        session.close()

def get_stats():
    """获取统计信息"""
    session = get_session()
    try:
        total = session.query(FinanceNews).count()
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today = session.query(FinanceNews).filter(
            FinanceNews.created_time >= today_start
        ).count()
        return {'total': total, 'today': today}
    except Exception as e:
        print(f"❌ [数据库] 统计失败: {e}")
        return {'total': 0, 'today': 0}
    finally:
        session.close()

def get_database_info():
    """获取数据库信息"""
    session = get_session()
    try:
        total = session.query(FinanceNews).count()
        oldest = session.query(FinanceNews).order_by(
            FinanceNews.created_time.asc()
        ).first()
        newest = session.query(FinanceNews).order_by(
            FinanceNews.created_time.desc()
        ).first()
        
        return {
            'total': total,
            'db_path': config.DB_PATH,
            'data_dir': config.APP_DATA_DIR,
            'oldest_news': oldest.created_time.isoformat() if oldest else None,
            'newest_news': newest.created_time.isoformat() if newest else None,
            'db_size_mb': os.path.getsize(config.DB_PATH) / (1024 * 1024) if os.path.exists(config.DB_PATH) else 0
        }
    except Exception as e:
        print(f"❌ [数据库] 获取信息失败: {e}")
        return {}
    finally:
        session.close()
