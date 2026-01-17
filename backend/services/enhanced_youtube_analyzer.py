"""
轻量级 YouTube 分析器 - 针对 512MB 内存优化
移除重量级依赖：spaCy, KeyBERT, sklearn
使用轻量级替代方案
"""

import re
from typing import List, Dict, Optional
from collections import Counter
import numpy as np

# 只保留必需的 NLTK 组件
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# Set NLTK data path
import os
nltk_data_path = os.getenv('NLTK_DATA', '/usr/local/share/nltk_data')
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

# 确保下载必要数据（使用 nltk_setup 模块）
try:
    from services.nltk_setup import download_nltk_data
    download_nltk_data()
except Exception as e:
    print(f"⚠️  NLTK setup module not available: {e}")
    # Fallback: 直接下载必要数据
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        try:
            nltk.download('punkt', quiet=True)
        except:
            pass
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        try:
            nltk.download('punkt_tab', quiet=True)
        except:
            pass
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        try:
            nltk.download('stopwords', quiet=True)
        except:
            pass
    try:
        nltk.data.find('taggers/averaged_perceptron_tagger_eng')
    except LookupError:
        try:
            nltk.download('averaged_perceptron_tagger_eng', quiet=True)
        except:
            pass


class LightweightContentAnalyzer:
    """
    轻量级内容分析器 - 不依赖 spaCy 和 KeyBERT
    """
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stop_words.update([
            'video', 'youtube', 'like', 'subscribe', 'comment', 
            'channel', 'watch', 'episode', 'part', 'new', 'best',
            'top', 'first', 'last', 'full', 'official'
        ])
    
    def extract_topics_from_titles(self, titles: List[str]) -> List[Dict]:
        """
        Extract meaningful topics from video titles using NLP
        
        Returns:
            List of topics with scores and related terms
        """
        # Combine all titles
        combined_text = ' '.join(titles)
        
        # Method 1: TF-IDF + Noun Extraction
        tfidf_topics = self._extract_tfidf_topics(titles)
        
        # Method 2: Proper Nouns (brands, products, etc.)
        proper_nouns = self._extract_proper_nouns(combined_text)
        
        # Merge and rank topics
        all_topics = self._merge_topics(tfidf_topics, proper_nouns)
        
        return all_topics[:15]  # Top 15 topics
    
    def _extract_tfidf_topics(self, titles: List[str]) -> List[Dict]:
        """
        Use TF-IDF to extract important terms, filtered by POS tags
        """
        # Preprocess: extract nouns and proper nouns only
        processed_titles = []
        for title in titles:
            try:
                # 分词
                words = word_tokenize(title.lower())
                # 词性标注
                pos_tags = pos_tag(words)
                # 只保留名词和专有名词
                tokens = [
                    word for word, pos in pos_tags
                    if pos.startswith(('NN', 'NNP'))  # NN=名词, NNP=专有名词
                    and word not in self.stop_words
                    and len(word) > 2
                    and word.isalnum()
                ]
                processed_titles.append(' '.join(tokens))
            except Exception as e:
                print(f"⚠️  Tokenization error for title '{title[:50]}...': {e}")
                continue
        
        if not any(processed_titles):
            return []
        
        # 简单的 TF-IDF 计算
        # 1. 计算词频 (TF)
        all_words = []
        for title in processed_titles:
            all_words.extend(title.split())
        
        word_freq = Counter(all_words)
        
        # 2. 计算文档频率 (DF)
        doc_freq = Counter()
        for title in processed_titles:
            unique_words = set(title.split())
            for word in unique_words:
                doc_freq[word] += 1
        
        # 3. 计算 TF-IDF
        num_docs = len(titles)
        tfidf_scores = {}
        
        for word, tf in word_freq.items():
            df = doc_freq[word]
            # TF-IDF = (TF / total_words) * log(N / DF)
            idf = np.log(num_docs / df) if df > 0 else 0
            tfidf_scores[word] = (tf / len(all_words)) * idf if all_words else 0
        
        # 4. 提取 bigrams (两词组合)
        bigrams = self._extract_bigrams(titles)
        for bigram, count in bigrams.items():
            # 给短语更高的权重
            tfidf_scores[bigram] = count * 1.5
        
        # 5. 归一化分数到 0-1 范围
        if tfidf_scores:
            max_score = max(tfidf_scores.values())
            min_score = min(tfidf_scores.values())
            score_range = max_score - min_score if max_score > min_score else 1.0
            
            # 归一化: (score - min) / range
            normalized_scores = {
                word: (score - min_score) / score_range if score_range > 0 else 0.5
                for word, score in tfidf_scores.items()
            }
        else:
            normalized_scores = {}
        
        # 6. 排序并返回
        topics = [
            {
                'topic': word,
                'score': float(normalized_scores.get(word, 0.0)),  # 使用归一化后的分数
                'type': 'tfidf',
                'frequency': word_freq.get(word, bigrams.get(word, 1))
            }
            for word, score in sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return topics[:20]
    
    def _extract_bigrams(self, titles: List[str]) -> Counter:
        """提取有意义的双词组合"""
        bigrams = []
        
        for title in titles:
            try:
                words = word_tokenize(title.lower())
                words = [w for w in words if w.isalnum() and w not in self.stop_words]
                
                # 生成 bigrams
                for i in range(len(words) - 1):
                    bigram = f"{words[i]} {words[i+1]}"
                    bigrams.append(bigram)
            except Exception as e:
                continue
        
        # 只保留出现 2 次以上的 bigrams
        bigram_counts = Counter(bigrams)
        return Counter({k: v for k, v in bigram_counts.items() if v >= 2})
    
    def _extract_proper_nouns(self, text: str) -> List[Dict]:
        """
        提取专有名词（品牌、产品、人名等）
        使用 NLTK 词性标注
        """
        try:
            # 分词和词性标注
            words = word_tokenize(text)
            pos_tags = pos_tag(words)
            
            # 提取专有名词 (NNP, NNPS)
            proper_nouns = []
            i = 0
            while i < len(pos_tags):
                word, pos = pos_tags[i]
                
                # 连续的专有名词组合在一起
                if pos in ['NNP', 'NNPS']:
                    noun_phrase = [word]
                    j = i + 1
                    
                    # 查找连续的专有名词
                    while j < len(pos_tags) and pos_tags[j][1] in ['NNP', 'NNPS']:
                        noun_phrase.append(pos_tags[j][0])
                        j += 1
                    
                    # 组合成短语
                    phrase = ' '.join(noun_phrase)
                    if len(phrase) > 2:  # 至少3个字符
                        proper_nouns.append(phrase.lower())
                    
                    i = j
                else:
                    i += 1
            
            # 统计频率
            noun_freq = Counter(proper_nouns)
            
            return [
                {
                    'topic': noun,
                    'score': count / len(proper_nouns) if proper_nouns else 0,
                    'type': 'entity',
                    'frequency': count
                }
                for noun, count in noun_freq.most_common(10)
            ]
        except Exception as e:
            print(f"⚠️  Proper noun extraction error: {e}")
            return []
    
    def _merge_topics(self, *topic_lists) -> List[Dict]:
        """
        Merge topics from different methods and rank by composite score
        """
        topic_map = {}
        
        for topics in topic_lists:
            for topic_data in topics:
                topic = topic_data['topic']
                score = topic_data['score']
                
                if topic in topic_map:
                    # 平均分数
                    topic_map[topic]['score'] = (topic_map[topic]['score'] + score) / 2
                    topic_map[topic]['methods'] = topic_map[topic].get('methods', 1) + 1
                else:
                    topic_map[topic] = {
                        'topic': topic,
                        'score': score,
                        'frequency': topic_data.get('frequency', 1),
                        'methods': 1
                    }
        
        # 多方法验证的主题加分
        for topic_data in topic_map.values():
            method_bonus = topic_data.get('methods', 1) * 0.2
            topic_data['score'] = topic_data['score'] * (1 + method_bonus)
        
        # 排序
        ranked_topics = sorted(
            topic_map.values(),
            key=lambda x: (x['score'], x['frequency']),
            reverse=True
        )
        
        return ranked_topics
    
    def analyze_high_performing_videos(self, videos: List[Dict]) -> Dict:
        """分析高表现视频"""
        if not videos:
            return {}
        
        # 按播放量排序
        sorted_videos = sorted(
            videos, 
            key=lambda x: x.get('viewCount', 0), 
            reverse=True
        )
        top_20_percent = sorted_videos[:max(1, len(sorted_videos) // 5)]
        
        # 提取主题
        top_titles = [v['title'] for v in top_20_percent]
        common_topics = self.extract_topics_from_titles(top_titles)
        
        # 分析模式
        avg_title_length = int(np.mean([len(v['title']) for v in top_20_percent]))
        
        # 计算平均和中位数播放量
        all_views = [v.get('viewCount', 0) for v in videos if v.get('viewCount', 0) > 0]
        avg_views = int(np.mean(all_views)) if all_views else 10000
        median_views = int(np.median(all_views)) if all_views else 10000
        
        return {
            'common_topics': common_topics[:5],
            'avg_title_length': avg_title_length,
            'avg_views': avg_views,
            'median_views': median_views,
            'total_videos': len(videos),
            'top_performer_count': len(top_20_percent)
        }
    
    def identify_content_style(self, videos: List[Dict]) -> Dict:
        """识别内容风格"""
        titles = [v['title'] for v in videos]
        combined = ' '.join(titles).lower()
        
        styles = {
            'tutorial': ['how to', 'tutorial', 'guide', 'tips', 'learn'],
            'review': ['review', 'unboxing', 'first look', 'hands on', 'vs'],
            'entertainment': ['funny', 'prank', 'challenge', 'compilation', 'fails'],
            'news': ['news', 'update', 'breaking', 'latest', 'today'],
            'educational': ['explained', 'science', 'history', 'documentary'],
            'gaming': ['gameplay', 'walkthrough', 'let\'s play', 'speedrun'],
            'tech': ['tech', 'gadget', 'phone', 'laptop', 'specs']
        }
        
        style_scores = {}
        for style, keywords in styles.items():
            score = sum(combined.count(kw) for kw in keywords)
            if score > 0:
                style_scores[style] = score
        
        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'primary_style': sorted_styles[0][0] if sorted_styles else 'general',
            'style_distribution': dict(sorted_styles[:3]),
            'is_multi_format': len(sorted_styles) > 3
        }


class LightweightAudienceAnalyzer:
    """轻量级受众分析器"""
    
    def analyze_target_audience(self, videos: List[Dict], channel_data: Dict) -> Dict:
        """分析目标受众"""
        titles_text = ' '.join([v['title'] for v in videos]).lower()
        
        # 年龄段分析
        age_indicators = {
            '18-24岁 (年轻人)': ['college', 'meme', 'viral', 'tiktok', 'trending'],
            '25-34岁 (职场)': ['career', 'productivity', 'business', 'startup'],
            '35-44岁 (成熟)': ['professional', 'investment', 'finance', 'management'],
            '全年龄': ['tutorial', 'guide', 'beginner', 'how to']
        }
        
        age_scores = {}
        for age_group, keywords in age_indicators.items():
            score = sum(1 for kw in keywords if kw in titles_text)
            if score > 0:
                age_scores[age_group] = score
        
        primary_age = max(age_scores.items(), key=lambda x: x[1])[0] if age_scores else '18-24岁 (年轻人)'
        
        # 互动水平
        if videos:
            avg_comment_rate = np.mean([
                v.get('commentCount', 0) / max(v.get('viewCount', 1), 1) * 100
                for v in videos
            ])
        else:
            avg_comment_rate = 0
        
        engagement_level = (
            '高 (活跃)' if avg_comment_rate > 0.5 else
            '中等' if avg_comment_rate > 0.2 else
            '低'
        )
        
        return {
            'primary_age_group': primary_age,
            'engagement_level': engagement_level,
            'engagement_rate': f"{avg_comment_rate:.3f}%",
            'subscriber_count': channel_data.get('subscriberCount', 0)
        }


# 为了兼容性，保留旧的类名作为别名
EnhancedContentAnalyzer = LightweightContentAnalyzer
EnhancedAudienceAnalyzer = LightweightAudienceAnalyzer

# 初始化轻量级分析器
content_analyzer = LightweightContentAnalyzer()
audience_analyzer = LightweightAudienceAnalyzer()


def analyze_channel_deeply(videos: List[Dict], channel_data: Dict) -> Dict:
    """
    轻量级频道深度分析
    """
    titles = [v['title'] for v in videos]
    
    # 提取主题
    topics = content_analyzer.extract_topics_from_titles(titles)
    
    # 分析高表现视频
    high_performers = content_analyzer.analyze_high_performing_videos(videos)
    
    # 识别内容风格
    content_style = content_analyzer.identify_content_style(videos)
    
    # 分析受众
    target_audience = audience_analyzer.analyze_target_audience(videos, channel_data)
    
    return {
        'topics': topics,
        'high_performers': high_performers,
        'content_style': content_style,
        'target_audience': target_audience,
        'video_analyses': [],  # 禁用字幕分析以节省内存
        'total_videos_analyzed': len(videos)
    }
