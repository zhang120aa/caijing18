import json
import jieba
import config

class Tagger:
    """标签模块 - 自动提取财经关键词"""
    
    @staticmethod
    def extract_tags(title, content):
        """
        提取标签
        1. 精确匹配关键词
        2. 分词匹配
        """
        tags = set()
        text = f"{title} {content}".lower()
        
        # 1. 精确关键词匹配
        for category, keywords in config.FINANCE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    tags.add(category)
                    break
        
        # 2. 分词匹配（可选，用于捕捉更多标签）
        words = jieba.cut(text)
        for word in words:
            if len(word) >= 2:  # 过滤单字
                for category, keywords in config.FINANCE_KEYWORDS.items():
                    if word.lower() in keywords:
                        tags.add(category)
                        break
        
        # 如果没有匹配到标签，添加默认标签
        if not tags:
            tags.add('其他')
        
        return json.dumps(list(tags), ensure_ascii=False)
    
    @staticmethod
    def parse_tags(tags_json):
        """解析标签JSON"""
        try:
            return json.loads(tags_json)
        except:
            return []

tagger = Tagger()
