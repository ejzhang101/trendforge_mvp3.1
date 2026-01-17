"""
Enhanced YouTube Channel Analyzer with Deep Content Analysis
MVP 2.0 - Intelligent Topic Extraction & Video Content Analysis
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import Counter
import numpy as np

# NLP Libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag

# Try to import spaCy (optional for lightweight deployment)
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None
    nlp = None
    print("⚠️  spaCy not available. Using NLTK-only mode. Install: pip install spacy")

# Machine Learning (optional for lightweight deployment)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None
    KMeans = None
    print("⚠️  scikit-learn not available. Using NLTK-only mode. Install: pip install scikit-learn")

# YouTube Transcript (optional)
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_TRANSCRIPT_AVAILABLE = True
except ImportError:
    YOUTUBE_TRANSCRIPT_AVAILABLE = False
    YouTubeTranscriptApi = None
    print("⚠️  youtube-transcript-api not available. Transcript analysis disabled.")

# Semantic Keywords (optional)
try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False
    KeyBERT = None
    print("⚠️  KeyBERT not available. Install: pip install keybert")

# Download required NLTK data
# NLTK 3.8.1+ uses punkt_tab instead of punkt
import os

# Set NLTK data path
nltk_data_path = os.getenv('NLTK_DATA', '/usr/local/share/nltk_data')
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

# Check and download NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        # Download both for compatibility
        print("📦 Downloading NLTK punkt resources...")
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            print(f"⚠️ punkt download failed: {e}")
        try:
            nltk.download('punkt_tab', quiet=True)
        except Exception as e:
            print(f"⚠️ punkt_tab download failed: {e}")
        try:
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('wordnet', quiet=True)
        except Exception as e:
            print(f"⚠️ Other NLTK data download failed: {e}")

# Load spaCy model (if available)
if SPACY_AVAILABLE:
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        try:
            print("⚠️  Downloading spaCy model...")
            import subprocess
            subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'], check=False)
            nlp = spacy.load('en_core_web_sm')
        except:
            nlp = None
            print("⚠️  Failed to load spaCy model. Using NLTK-only mode.")
else:
    nlp = None


class EnhancedContentAnalyzer:
    """
    Advanced content analyzer with NLP capabilities
    """
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Add custom stop words
        self.stop_words.update([
            'video', 'youtube', 'like', 'subscribe', 'comment', 
            'channel', 'watch', 'episode', 'part', 'new', 'best',
            'top', 'first', 'last', 'full', 'official'
        ])
        
        if KEYBERT_AVAILABLE:
            self.keybert = KeyBERT()
        else:
            self.keybert = None
    
    def extract_topics_from_titles(self, titles: List[str]) -> List[Dict]:
        """
        Extract meaningful topics from video titles using NLP
        
        Returns:
            List of topics with scores and related terms
        """
        # Combine all titles
        combined_text = ' '.join(titles)
        
        # Method 1: TF-IDF + Noun Extraction (or NLTK-only fallback)
        tfidf_topics = self._extract_tfidf_topics(titles)
        
        # Method 2: Named Entity Recognition (spaCy or NLTK fallback)
        ner_topics = self._extract_named_entities(combined_text)
        
        # Method 3: KeyBERT semantic keywords (if available)
        if self.keybert:
            semantic_topics = self._extract_semantic_keywords(combined_text)
        else:
            semantic_topics = []
        
        # Merge and rank topics
        all_topics = self._merge_topics(tfidf_topics, ner_topics, semantic_topics)
        
        return all_topics[:15]  # Top 15 topics
    
    def _extract_nltk_topics(self, titles: List[str]) -> List[Dict]:
        """
        Extract topics using NLTK only (lightweight mode)
        """
        # Combine all titles
        combined_text = ' '.join(titles).lower()
        
        # Tokenize and filter
        tokens = word_tokenize(combined_text)
        tokens = [t for t in tokens if t.isalnum() and t not in self.stop_words and len(t) > 2]
        
        # POS tagging
        pos_tags = pos_tag(tokens)
        nouns = [word for word, pos in pos_tags if pos.startswith('NN')]
        
        # Count frequency
        topic_counter = Counter(nouns)
        
        topics = []
        for topic, count in topic_counter.most_common(15):
            topics.append({
                'topic': topic,
                'score': count / len(nouns) if nouns else 0,
                'type': 'nltk',
                'frequency': count
            })
        
        return topics
    
    def _extract_tfidf_topics(self, titles: List[str]) -> List[Dict]:
        """
        Use TF-IDF to extract important terms, filtered by POS tags
        Falls back to NLTK-only mode if spaCy or sklearn unavailable
        """
        # Check if required libraries are available
        if not SKLEARN_AVAILABLE:
            return self._extract_nltk_topics(titles)
        
        # Preprocess: extract nouns and proper nouns only
        processed_titles = []
        for title in titles:
            if SPACY_AVAILABLE and nlp:
                # Use spaCy if available
                try:
                    doc = nlp(title.lower())
                    tokens = [
                        token.lemma_ for token in doc 
                        if token.pos_ in ['NOUN', 'PROPN'] 
                        and token.text not in self.stop_words
                        and len(token.text) > 2
                        and not token.is_punct
                    ]
                    processed_titles.append(' '.join(tokens))
                except:
                    # Fallback to NLTK if spaCy fails
                    tokens = word_tokenize(title.lower())
                    pos_tags = pos_tag(tokens)
                    nouns = [word for word, pos in pos_tags 
                            if pos.startswith('NN') 
                            and word not in self.stop_words 
                            and len(word) > 2]
                    processed_titles.append(' '.join(nouns))
            else:
                # Fallback to NLTK
                tokens = word_tokenize(title.lower())
                pos_tags = pos_tag(tokens)
                nouns = [word for word, pos in pos_tags 
                        if pos.startswith('NN') 
                        and word not in self.stop_words 
                        and len(word) > 2]
                processed_titles.append(' '.join(nouns))
        
        if not any(processed_titles):
            return self._extract_nltk_topics(titles)
        
        # TF-IDF
        try:
            vectorizer = TfidfVectorizer(
                max_features=30,
                ngram_range=(1, 3),  # Include bigrams and trigrams
                min_df=1,
                max_df=0.8
            )
            
            tfidf_matrix = vectorizer.fit_transform(processed_titles)
            feature_names = vectorizer.get_feature_names_out()
            
            # Calculate average TF-IDF scores
            avg_scores = tfidf_matrix.mean(axis=0).A1
            topics = [
                {
                    'topic': feature_names[i],
                    'score': float(avg_scores[i]),
                    'type': 'tfidf',
                    'frequency': self._count_occurrences(feature_names[i], titles)
                }
                for i in avg_scores.argsort()[-15:][::-1]
            ]
            
            return topics
        except Exception as e:
            print(f"⚠️  TF-IDF extraction error: {e}, falling back to NLTK")
            return self._extract_nltk_topics(titles)
    
    def _extract_proper_nouns_nltk(self, text: str) -> List[Dict]:
        """
        Extract proper nouns using NLTK (fallback when spaCy unavailable)
        """
        try:
            # Tokenize and POS tag
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # Extract proper nouns (NNP, NNPS)
            proper_nouns = [
                word.lower() 
                for word, pos in pos_tags 
                if pos in ['NNP', 'NNPS'] 
                and word.isalnum() 
                and len(word) > 2
                and word.lower() not in self.stop_words
            ]
            
            # Count frequency
            entity_counter = Counter(proper_nouns)
            
            entities = []
            for entity, count in entity_counter.most_common(10):
                entities.append({
                    'topic': entity,
                    'score': count / len(proper_nouns) if proper_nouns else 0,
                    'type': 'entity',
                    'frequency': count
                })
            
            return entities
        except Exception as e:
            print(f"⚠️  NLTK proper noun extraction error: {e}")
            return []
    
    def _extract_named_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities (brands, products, technologies, etc.)
        Uses spaCy if available, falls back to NLTK proper noun extraction
        """
        if not SPACY_AVAILABLE or not nlp:
            return self._extract_proper_nouns_nltk(text)
        
        try:
            doc = nlp(text)
            entities = []
            
            entity_counter = Counter()
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'GPE', 'PERSON', 'WORK_OF_ART', 'EVENT']:
                    entity_counter[ent.text.lower()] += 1
            
            for entity, count in entity_counter.most_common(10):
                entities.append({
                    'topic': entity,
                    'score': count / len(doc.ents) if doc.ents else 0,
                    'type': 'entity',
                    'frequency': count
                })
            
            return entities
        except Exception as e:
            print(f"⚠️  spaCy NER error: {e}, falling back to NLTK")
            return self._extract_proper_nouns_nltk(text)
    
    def _extract_semantic_keywords(self, text: str) -> List[Dict]:
        """
        Use KeyBERT for semantic keyword extraction
        """
        if not self.keybert or not text.strip():
            return []
        
        try:
            keywords = self.keybert.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 3),
                stop_words='english',
                top_n=10,
                use_maxsum=True,
                diversity=0.7
            )
            
            return [
                {
                    'topic': kw[0],
                    'score': float(kw[1]),
                    'type': 'semantic',
                    'frequency': self._count_occurrences(kw[0], text)
                }
                for kw in keywords
            ]
        except:
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
                    # Average scores from different methods
                    topic_map[topic]['score'] = (topic_map[topic]['score'] + score) / 2
                    topic_map[topic]['methods'].append(topic_data['type'])
                else:
                    topic_map[topic] = {
                        'topic': topic,
                        'score': score,
                        'frequency': topic_data.get('frequency', 1),
                        'methods': [topic_data['type']]
                    }
        
        # Boost score for topics found by multiple methods
        for topic_data in topic_map.values():
            method_bonus = len(topic_data['methods']) * 0.2
            topic_data['score'] = topic_data['score'] * (1 + method_bonus)
        
        # Sort by composite score
        ranked_topics = sorted(
            topic_map.values(),
            key=lambda x: (x['score'], x['frequency']),
            reverse=True
        )
        
        return ranked_topics
    
    def _count_occurrences(self, term: str, texts) -> int:
        """Count how many times a term appears across texts"""
        if isinstance(texts, str):
            texts = [texts]
        
        count = 0
        term_lower = term.lower()
        for text in texts:
            count += text.lower().count(term_lower)
        return count
    
    def analyze_video_content(self, video_id: str) -> Optional[Dict]:
        """
        Analyze video content from transcript
        
        Returns:
            {
                'main_topics': [...],
                'summary': '...',
                'sentiment': 'positive/neutral/negative',
                'key_points': [...]
            }
        """
        if not YOUTUBE_TRANSCRIPT_AVAILABLE:
            return None
        
        try:
            # Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = ' '.join([entry['text'] for entry in transcript_list])
            
            # Extract topics
            topics = self.extract_topics_from_titles([transcript_text])[:5]
            
            # Generate summary (first 500 chars)
            summary = transcript_text[:500] + '...' if len(transcript_text) > 500 else transcript_text
            
            # Basic sentiment (can be enhanced with proper sentiment analysis)
            sentiment = self._analyze_sentiment(transcript_text)
            
            return {
                'main_topics': [t['topic'] for t in topics],
                'summary': summary,
                'sentiment': sentiment,
                'transcript_length': len(transcript_text),
                'has_transcript': True
            }
        
        except Exception as e:
            print(f"Could not get transcript for {video_id}: {e}")
            return {
                'has_transcript': False,
                'error': str(e)
            }
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Basic sentiment analysis
        (Can be enhanced with proper sentiment models)
        """
        positive_words = {'great', 'amazing', 'awesome', 'excellent', 'best', 'love', 'perfect'}
        negative_words = {'bad', 'worst', 'terrible', 'awful', 'hate', 'horrible', 'disappointing'}
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count * 1.5:
            return 'positive'
        elif neg_count > pos_count * 1.5:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_high_performing_videos(self, videos: List[Dict]) -> Dict:
        """
        Analyze what makes high-performing videos successful
        
        Args:
            videos: List of video dicts with viewCount, title, etc.
        
        Returns:
            {
                'common_topics': [...],
                'avg_title_length': int,
                'best_posting_time': str,
                'engagement_patterns': {...}
            }
        """
        if not videos:
            return {}
        
        # Sort by view count
        sorted_videos = sorted(videos, key=lambda x: x.get('viewCount', 0), reverse=True)
        top_20_percent = sorted_videos[:max(1, len(sorted_videos) // 5)]
        
        # Extract topics from top performers
        top_titles = [v['title'] for v in top_20_percent]
        common_topics = self.extract_topics_from_titles(top_titles)
        
        # Analyze patterns
        avg_title_length = np.mean([len(v['title']) for v in top_20_percent])
        
        # Posting time analysis (hour of day)
        posting_hours = [v.get('publishedAt', '').split('T')[1].split(':')[0] 
                        for v in top_20_percent if 'publishedAt' in v]
        best_hour = Counter(posting_hours).most_common(1)[0][0] if posting_hours else 'N/A'
        
        # Engagement rate
        avg_engagement = np.mean([
            (v.get('likeCount', 0) + v.get('commentCount', 0)) / max(v.get('viewCount', 1), 1)
            for v in top_20_percent
        ])
        
        # Calculate average views from all videos (not just top performers)
        # This is the benchmark for prediction
        all_views = [v.get('viewCount', 0) for v in videos if v.get('viewCount', 0) > 0]
        avg_views = int(np.mean(all_views)) if all_views else 10000
        
        # Also calculate median for more robust estimate
        median_views = int(np.median(all_views)) if all_views else 10000
        
        return {
            'common_topics': common_topics[:5],
            'avg_title_length': int(avg_title_length),
            'best_posting_hour': best_hour,
            'avg_engagement_rate': float(avg_engagement),
            'top_performer_count': len(top_20_percent),
            'avg_views': avg_views,  # 频道平均播放量（用于预测基准）
            'median_views': median_views,  # 中位数播放量（更稳健）
            'total_videos': len(videos)
        }
    
    def identify_content_style(self, videos: List[Dict]) -> Dict:
        """
        Identify the channel's content style and format
        """
        titles = [v['title'] for v in videos]
        combined = ' '.join(titles).lower()
        
        # Identify style indicators
        styles = {
            'tutorial': ['how to', 'tutorial', 'guide', 'tips', 'learn'],
            'review': ['review', 'unboxing', 'first look', 'hands on', 'vs'],
            'entertainment': ['funny', 'prank', 'challenge', 'compilation', 'fails'],
            'news': ['news', 'update', 'breaking', 'latest', 'today'],
            'vlog': ['vlog', 'daily', 'day in', 'life', 'routine'],
            'educational': ['explained', 'science', 'history', 'documentary', 'facts'],
            'gaming': ['gameplay', 'walkthrough', 'let\'s play', 'speedrun'],
            'tech': ['tech', 'gadget', 'phone', 'laptop', 'specs']
        }
        
        style_scores = {}
        for style, keywords in styles.items():
            score = sum(combined.count(kw) for kw in keywords)
            if score > 0:
                style_scores[style] = score
        
        # Get dominant styles
        sorted_styles = sorted(style_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'primary_style': sorted_styles[0][0] if sorted_styles else 'general',
            'style_distribution': dict(sorted_styles[:3]),
            'is_multi_format': len(sorted_styles) > 3
        }


class EnhancedAudienceAnalyzer:
    """
    优化的受众分析器 - 更精细的年龄和兴趣标签
    """
    
    def analyze_target_audience(self, videos: List[Dict], channel_data: Dict) -> Dict:
        """
        细粒度受众分析
        """
        titles_text = ' '.join([v['title'] for v in videos]).lower()
        descriptions = ' '.join([v.get('description', '')[:200] for v in videos]).lower()
        combined_text = titles_text + ' ' + descriptions
        
        # 更细化的年龄段指标
        age_indicators = {
            '6-12岁 (儿童)': {
                'keywords': ['kids', 'children', 'cartoon', 'toy', 'fun', 'animation', 'disney'],
                'score': 0
            },
            '13-17岁 (青少年)': {
                'keywords': ['teen', 'school', 'student', 'fortnite', 'tiktok', 'roblox'],
                'score': 0
            },
            '18-24岁 (大学生/年轻人)': {
                'keywords': ['college', 'university', 'study', 'dorm', 'dating', 'meme', 'viral'],
                'score': 0
            },
            '25-34岁 (职场新人)': {
                'keywords': ['career', 'startup', 'side hustle', 'productivity', 'freelance', 'crypto'],
                'score': 0
            },
            '35-44岁 (成熟职场)': {
                'keywords': ['professional', 'business', 'management', 'investment', 'finance', 'real estate'],
                'score': 0
            },
            '45+ (资深/退休)': {
                'keywords': ['retirement', 'classic', 'history', 'documentary', 'gardening', 'travel'],
                'score': 0
            },
            '全年龄': {
                'keywords': ['family', 'everyone', 'beginner', 'basic', 'guide', 'tutorial'],
                'score': 0
            }
        }
        
        # 计算每个年龄段的匹配分数
        for age_group, data in age_indicators.items():
            for keyword in data['keywords']:
                if keyword in combined_text:
                    data['score'] += 1
        
        # 排序并获取前2个最可能的年龄段
        sorted_ages = sorted(
            age_indicators.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        primary_age = sorted_ages[0][0] if sorted_ages[0][1]['score'] > 0 else '18-24岁 (大学生/年轻人)'
        secondary_age = sorted_ages[1][0] if len(sorted_ages) > 1 and sorted_ages[1][1]['score'] > 0 else None
        
        # 兴趣标签识别
        interest_indicators = {
            '科技爱好者': ['tech', 'gadget', 'phone', 'computer', 'software', 'app', 'ai'],
            '游戏玩家': ['game', 'gaming', 'gameplay', 'esports', 'console', 'pc'],
            '创业者': ['startup', 'business', 'entrepreneur', 'side hustle', 'passive income'],
            '学生/学习者': ['learn', 'study', 'education', 'tutorial', 'course', 'exam'],
            '时尚/美妆': ['fashion', 'makeup', 'beauty', 'style', 'outfit'],
            '健身/健康': ['fitness', 'workout', 'health', 'diet', 'gym', 'nutrition'],
            '投资/理财': ['invest', 'stock', 'crypto', 'finance', 'money', 'wealth'],
            '娱乐爱好者': ['entertainment', 'movie', 'music', 'celebrity', 'comedy'],
            '专业人士': ['professional', 'expert', 'advanced', 'industry', 'career']
        }
        
        interest_scores = {}
        for interest, keywords in interest_indicators.items():
            score = sum(1 for kw in keywords if kw in combined_text)
            if score > 0:
                interest_scores[interest] = score
        
        top_interests = sorted(
            interest_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        # 互动水平分析
        avg_comment_rate = np.mean([
            v.get('commentCount', 0) / max(v.get('viewCount', 1), 1) * 100
            for v in videos
        ])
        
        engagement_level = (
            '极高 (活跃社区)' if avg_comment_rate > 1.0 else
            '高 (积极互动)' if avg_comment_rate > 0.5 else
            '中等 (正常水平)' if avg_comment_rate > 0.2 else
            '低 (观看为主)'
        )
        
        # 消费能力推测（基于内容类型）
        purchasing_power_indicators = {
            '高消费': ['luxury', 'premium', 'expensive', 'high-end', 'professional'],
            '中等消费': ['affordable', 'budget', 'value', 'best', 'review'],
            '价格敏感': ['cheap', 'free', 'budget', 'affordable', 'deal']
        }
        
        purchasing_scores = {}
        for level, keywords in purchasing_power_indicators.items():
            score = sum(1 for kw in keywords if kw in combined_text)
            purchasing_scores[level] = score
        
        purchasing_power = max(purchasing_scores.items(), key=lambda x: x[1])[0] if any(purchasing_scores.values()) else '中等消费'
        
        return {
            'primary_age_group': primary_age,
            'secondary_age_group': secondary_age,
            'age_confidence': f"{sorted_ages[0][1]['score']}个匹配指标",
            'top_interests': [interest for interest, _ in top_interests],
            'engagement_level': engagement_level,
            'engagement_rate': f"{avg_comment_rate:.3f}%",
            'purchasing_power': purchasing_power,
            'subscriber_count': channel_data.get('subscriberCount', 0),
            'audience_size_tier': (
                '大型频道 (10万+)' if channel_data.get('subscriberCount', 0) > 100000 else
                '中型频道 (1万-10万)' if channel_data.get('subscriberCount', 0) > 10000 else
                '小型频道 (1千-1万)' if channel_data.get('subscriberCount', 0) > 1000 else
                '新频道 (<1千)'
            ),
            'audience_insights': self._generate_insights(
                primary_age, 
                [i for i, _ in top_interests],
                engagement_level
            )
        }
    
    def _generate_insights(self, age_group: str, interests: List[str], engagement: str) -> str:
        """生成受众洞察文本"""
        insights = []
        
        # 年龄段洞察
        if '18-24' in age_group:
            insights.append("年轻观众群体，喜欢新潮、病毒式内容")
        elif '25-34' in age_group:
            insights.append("职场新人为主，关注实用技能和职业发展")
        elif '35-44' in age_group:
            insights.append("成熟观众，偏好深度内容和专业知识")
        
        # 兴趣洞察
        if interests:
            insights.append(f"核心兴趣：{', '.join(interests[:2])}")
        
        # 互动洞察
        if '极高' in engagement or '高' in engagement:
            insights.append("社区活跃度高，适合互动性内容")
        
        return "；".join(insights) if insights else "观众群体多元化"


# Initialize analyzers
content_analyzer = EnhancedContentAnalyzer()
audience_analyzer = EnhancedAudienceAnalyzer()


def analyze_channel_deeply(videos: List[Dict], channel_data: Dict) -> Dict:
    """
    Comprehensive channel analysis with all new features
    
    Returns:
        {
            'topics': [...],           # Extracted topics
            'high_performers': {...},  # What works well
            'content_style': {...},    # Channel style
            'target_audience': {...},  # Audience insights
            'video_analyses': [...]    # Individual video insights
        }
    """
    # Extract topics
    titles = [v['title'] for v in videos]
    topics = content_analyzer.extract_topics_from_titles(titles)
    
    # Analyze high performers
    high_performers = content_analyzer.analyze_high_performing_videos(videos)
    
    # Identify content style
    content_style = content_analyzer.identify_content_style(videos)
    
    # Analyze target audience
    target_audience = audience_analyzer.analyze_target_audience(videos, channel_data)
    
    # Analyze individual videos (DISABLED for performance - transcript analysis is slow)
    # This can be enabled if needed, but significantly slows down analysis
    video_analyses = []
    # Skip transcript analysis for faster processing
    # top_videos = sorted(videos, key=lambda x: x.get('viewCount', 0), reverse=True)[:5]
    # for video in top_videos:
    #     analysis = content_analyzer.analyze_video_content(video['videoId'])
    #     if analysis and analysis.get('has_transcript'):
    #         video_analyses.append({
    #             'video_id': video['videoId'],
    #             'title': video['title'],
    #             'views': video.get('viewCount', 0),
    #             'analysis': analysis
    #         })
    
    return {
        'topics': topics,
        'high_performers': high_performers,
        'content_style': content_style,
        'target_audience': target_audience,
        'video_analyses': video_analyses,
        'total_videos_analyzed': len(videos)
    }
