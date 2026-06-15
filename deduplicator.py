import hashlib
import difflib
from datetime import datetime, timedelta
from database import get_session, FinanceNews
import config

class Deduplicator:
    """智能去重模块"""
    
    @staticmethod
    def generate_hash(text):
        """生成文本哈希"""
        return hashlib.md5(text.encode()).hexdigest()
    
    @staticmethod
    def get_similarity(text1, text2):
        """计算两个文本的相似度"""
        ratio = difflib.SequenceMatcher(None, text1, text2).ratio()
        return ratio
    
    @staticmethod
    def is_duplicate(title, content, message_id=None):
        """
        判断是否重复
        1. 优先检查message_id（精确去重）
        2. 检查内容哈希
        3. 检查相似度
        """
        session = get_session()
        try:
            # 1. 消息ID精确去重
            if message_id:
                existing = session.query(FinanceNews).filter(
                    FinanceNews.message_id == message_id
                ).first()
                if existing:
                    return True, "消息ID重复"
            
            # 2. 内容哈希去重
            content_hash = Deduplicator.generate_hash(content)
            existing = session.query(FinanceNews).filter(
                FinanceNews.id == content_hash
            ).first()
            if existing:
                return True, "内容哈希重复"
            
            # 3. 24小时内相似度检查
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recent_news = session.query(FinanceNews).filter(
                FinanceNews.published_time >= cutoff_time
            ).all()
            
            # 只需对标题做相似度检查（更快）
            for news in recent_news:
                similarity = Deduplicator.get_similarity(title, news.title)
                if similarity > config.SIMILARITY_THRESHOLD:
                    return True, f"相似度{similarity:.2%}超过阈值"
            
            return False, None
        except Exception as e:
            print(f"[去重] 错误: {e}")
            return False, None
        finally:
            session.close()

deduplicator = Deduplicator()
