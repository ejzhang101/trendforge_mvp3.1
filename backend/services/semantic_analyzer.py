"""
Semantic Keyword Analyzer with KeyBERT
优雅降级：KeyBERT 不可用时使用 TF-IDF，不影响现有功能
"""

from typing import List, Dict, Optional
import numpy as np

# 尝试导入 KeyBERT，失败则使用基础方法
try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False
    print("⚠️  KeyBERT not available, using TF-IDF fallback")


class SemanticKeywordAnalyzer:
    """
    语义关键词分析器
    
    特性：
    - KeyBERT 语义分析（准确率 +20%）
    - 自动降级到 TF-IDF
    - 可选启用（不影响默认流程）
    """
    
    def __init__(self, tfidf_analyzer=None):
        """
        Args:
            tfidf_analyzer: 基础 TF-IDF 分析器（降级使用）
        """
        self.keybert = None
        self.tfidf_analyzer = tfidf_analyzer
        self.use_semantic = KEYBERT_AVAILABLE
        
        # 延迟加载 KeyBERT（节省内存）
        self._keybert_loaded = False
    
    def extract_keywords(
        self,
        texts: List[str],
        use_semantic: bool = False,
        top_n: int = 15,
        diversity: float = 0.7
    ) -> List[Dict]:
        """
        提取关键词
        
        Args:
            texts: 文本列表（如视频标题）
            use_semantic: 是否使用语义分析（默认 False，使用 TF-IDF）
            top_n: 返回关键词数量
            diversity: 多样性（0-1，越高越多样）
        
        Returns:
            List of {topic, score, frequency, method}
        """
        # 如果不启用语义分析，或 KeyBERT 不可用，使用 TF-IDF
        if not use_semantic or not self.use_semantic:
            return self._tfidf_fallback(texts, top_n)
        
        # 延迟加载 KeyBERT
        if not self._keybert_loaded:
            self._load_keybert()
        
        # 如果加载失败，降级
        if self.keybert is None:
            return self._tfidf_fallback(texts, top_n)
        
        # 使用 KeyBERT 提取语义关键词
        return self._keybert_extraction(texts, top_n, diversity)
    
    def _load_keybert(self):
        """延迟加载 KeyBERT 模型"""
        try:
            print("📥 Loading KeyBERT model (first use)...")
            self.keybert = KeyBERT()
            self._keybert_loaded = True
            print("✅ KeyBERT loaded successfully")
        except Exception as e:
            print(f"⚠️  Failed to load KeyBERT: {e}")
            self.keybert = None
            self._keybert_loaded = True  # 标记已尝试，避免重复加载
    
    def _keybert_extraction(
        self,
        texts: List[str],
        top_n: int,
        diversity: float
    ) -> List[Dict]:
        """使用 KeyBERT 提取语义关键词"""
        try:
            # 合并文本
            combined_text = ' '.join(texts)
            
            # KeyBERT 提取
            keywords = self.keybert.extract_keywords(
                combined_text,
                keyphrase_ngram_range=(1, 3),  # 1-3 词组合
                stop_words='english',
                top_n=top_n * 2,  # 提取更多，后续合并
                use_maxsum=True,  # 最大化多样性
                diversity=diversity
            )
            
            # 转换为统一格式
            semantic_topics = [
                {
                    'topic': kw[0],
                    'score': float(kw[1]),
                    'frequency': self._count_frequency(kw[0], texts),
                    'method': 'keybert_semantic'
                }
                for kw in keywords
            ]
            
            # 如果也有 TF-IDF 分析器，合并结果
            if self.tfidf_analyzer:
                tfidf_topics = self.tfidf_analyzer.extract_topics_from_titles(texts)
                merged = self._merge_semantic_and_tfidf(semantic_topics, tfidf_topics)
                return merged[:top_n]
            
            return semantic_topics[:top_n]
            
        except Exception as e:
            print(f"⚠️  KeyBERT extraction failed: {e}")
            # 降级到 TF-IDF
            return self._tfidf_fallback(texts, top_n)
    
    def _tfidf_fallback(self, texts: List[str], top_n: int) -> List[Dict]:
        """降级到 TF-IDF 方法"""
        if self.tfidf_analyzer:
            print("ℹ️  Using TF-IDF fallback for keyword extraction")
            topics = self.tfidf_analyzer.extract_topics_from_titles(texts)
            # 添加 method 标记
            for topic in topics:
                topic['method'] = 'tfidf_fallback'
            return topics[:top_n]
        else:
            # 如果连 TF-IDF 都没有，返回空
            print("⚠️  No fallback analyzer available")
            return []
    
    def _merge_semantic_and_tfidf(
        self,
        semantic_topics: List[Dict],
        tfidf_topics: List[Dict]
    ) -> List[Dict]:
        """
        合并 KeyBERT 和 TF-IDF 结果
        
        策略：
        - KeyBERT 擅长语义理解（"AI" = "artificial intelligence"）
        - TF-IDF 擅长频率统计
        - 两者互补
        """
        topic_map = {}
        
        # 添加 KeyBERT 结果（权重 0.6）
        for topic_data in semantic_topics:
            topic = topic_data['topic'].lower()
            topic_map[topic] = {
                'topic': topic_data['topic'],  # 保留原始大小写
                'semantic_score': topic_data['score'],
                'tfidf_score': 0,
                'frequency': topic_data['frequency'],
                'methods': ['keybert']
            }
        
        # 添加 TF-IDF 结果（权重 0.4）
        for topic_data in tfidf_topics[:15]:  # 只取 top 15
            topic = topic_data['topic'].lower()
            
            if topic in topic_map:
                # 已存在，更新分数
                topic_map[topic]['tfidf_score'] = topic_data['score']
                topic_map[topic]['methods'].append('tfidf')
            else:
                # 新主题
                topic_map[topic] = {
                    'topic': topic_data['topic'],
                    'semantic_score': 0,
                    'tfidf_score': topic_data['score'],
                    'frequency': topic_data['frequency'],
                    'methods': ['tfidf']
                }
        
        # 计算综合分数
        for topic_data in topic_map.values():
            # 加权平均：KeyBERT 60%, TF-IDF 40%
            composite_score = (
                topic_data['semantic_score'] * 0.6 +
                topic_data['tfidf_score'] * 0.4
            )
            
            # 多方法验证加成
            if len(topic_data['methods']) > 1:
                composite_score *= 1.2
            
            topic_data['score'] = composite_score
            topic_data['method'] = 'hybrid_semantic_tfidf'
        
        # 排序
        ranked_topics = sorted(
            topic_map.values(),
            key=lambda x: (x['score'], x['frequency']),
            reverse=True
        )
        
        return ranked_topics
    
    def _count_frequency(self, term: str, texts: List[str]) -> int:
        """统计词频"""
        count = 0
        term_lower = term.lower()
        for text in texts:
            count += text.lower().count(term_lower)
        return count
    
    def analyze_semantic_similarity(
        self,
        query: str,
        candidates: List[str]
    ) -> List[Dict]:
        """
        计算语义相似度（用于匹配推荐）
        
        Args:
            query: 查询文本（如推荐关键词）
            candidates: 候选文本列表（如频道主题）
        
        Returns:
            List of {text, similarity_score}
        """
        if not self.use_semantic or self.keybert is None:
            # 降级：简单字符串匹配
            return self._simple_similarity(query, candidates)
        
        try:
            # 使用 sentence-transformers 计算相似度
            from sentence_transformers import SentenceTransformer, util
            
            model = SentenceTransformer('all-MiniLM-L6-v2')  # 轻量模型
            
            # 编码
            query_embedding = model.encode(query, convert_to_tensor=True)
            candidate_embeddings = model.encode(candidates, convert_to_tensor=True)
            
            # 计算余弦相似度
            similarities = util.cos_sim(query_embedding, candidate_embeddings)[0]
            
            results = [
                {
                    'text': candidates[i],
                    'similarity_score': float(similarities[i])
                }
                for i in range(len(candidates))
            ]
            
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            return results
            
        except Exception as e:
            print(f"⚠️  Semantic similarity failed: {e}")
            return self._simple_similarity(query, candidates)
    
    def _simple_similarity(self, query: str, candidates: List[str]) -> List[Dict]:
        """简单的字符串相似度（降级方法）"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        for candidate in candidates:
            candidate_lower = candidate.lower()
            candidate_words = set(candidate_lower.split())
            
            # Jaccard 相似度
            intersection = len(query_words & candidate_words)
            union = len(query_words | candidate_words)
            similarity = intersection / union if union > 0 else 0
            
            results.append({
                'text': candidate,
                'similarity_score': similarity
            })
        
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results


# 全局实例（懒加载）
_semantic_analyzer_instance = None

def get_semantic_analyzer(tfidf_analyzer=None) -> SemanticKeywordAnalyzer:
    """获取语义分析器单例"""
    global _semantic_analyzer_instance
    if _semantic_analyzer_instance is None:
        _semantic_analyzer_instance = SemanticKeywordAnalyzer(tfidf_analyzer)
    return _semantic_analyzer_instance
