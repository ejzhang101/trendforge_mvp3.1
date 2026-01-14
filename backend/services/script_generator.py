"""
Intelligent Script Generator
Generates video scripts based on channel analysis, trending topics, and product info
Enhanced with LLM (OpenAI) for semantic analysis and intelligent script generation
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
import os
import re

# LLM API Support
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available. Install: pip install openai")


class ScriptGeneratorEngine:
    """
    智能脚本生成引擎
    
    基于以下信息生成视频脚本：
    1. 频道分析数据（风格、受众、高表现视频）
    2. AI 推荐话题
    3. 用户产品/服务信息
    """
    
    def __init__(self):
        self.script_templates = self._initialize_templates()
        # Initialize OpenAI client if available
        self.llm_available = False
        self.llm_client = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                try:
                    self.llm_client = OpenAI(api_key=api_key)
                    self.llm_available = True
                    print("✅ LLM (OpenAI) initialized for script generation")
                except Exception as e:
                    print(f"⚠️ Failed to initialize OpenAI: {e}")
                    self.llm_available = False
            else:
                print("⚠️ OPENAI_API_KEY not found in environment variables")
        else:
            print("⚠️ OpenAI library not installed, using template-based generation")
    
    def generate_scripts(
        self,
        user_prompt: str,
        channel_analysis: Dict,
        recommendations: List[Dict],
        count: int = 3
    ) -> List[Dict]:
        """
        生成视频脚本
        
        Args:
            user_prompt: 用户输入的产品/服务描述
            channel_analysis: 频道分析数据
            recommendations: AI 推荐的话题列表
            count: 生成脚本数量
        
        Returns:
            List of script objects with performance predictions
        """
        # 解析用户输入
        product_info = self._parse_user_prompt(user_prompt)
        
        # 选择最匹配的推荐话题（前3个）
        top_recommendations = recommendations[:3] if recommendations else []
        
        # 如果没有推荐，使用默认推荐
        if not top_recommendations:
            # 从频道分析中提取主题作为默认推荐
            topics = channel_analysis.get('topics', [])
            if topics:
                # 使用前3个主题创建默认推荐
                top_recommendations = [
                    {
                        'keyword': topic.get('topic', '热门话题') if isinstance(topic, dict) else str(topic),
                        'match_score': topic.get('score', 0.7) * 100 if isinstance(topic, dict) else 70,
                        'viral_potential': 60,
                        'performance_score': 65,
                        'relevance_score': 75,
                        'opportunity_score': 60,
                        'content_angle': f"制作关于 {topic.get('topic', '热门话题') if isinstance(topic, dict) else str(topic)} 的内容",
                        'suggested_format': channel_analysis.get('content_style', {}).get('format', '8-12分钟综合内容'),
                        'urgency': 'medium'
                    }
                    for topic in topics[:3]
                ]
            else:
                # 如果连主题都没有，创建一个通用推荐
                top_recommendations = [
                    {
                        'keyword': '产品推广',
                        'match_score': 70,
                        'viral_potential': 60,
                        'performance_score': 65,
                        'relevance_score': 75,
                        'opportunity_score': 60,
                        'content_angle': '产品介绍和推广',
                        'suggested_format': '8-12分钟综合内容',
                        'urgency': 'medium'
                    }
                ]
        
        # 提取频道特征
        channel_style = channel_analysis.get('content_style', {})
        target_audience = channel_analysis.get('target_audience', {})
        high_performers = channel_analysis.get('high_performers', {})
        
        # 为每个推荐话题生成脚本
        scripts = []
        for i, rec in enumerate(top_recommendations):
            script = self._generate_single_script(
                product_info=product_info,
                recommendation=rec,
                channel_style=channel_style,
                target_audience=target_audience,
                high_performers=high_performers,
                index=i
            )
            scripts.append(script)
        
        # 按预测效果排序
        scripts.sort(key=lambda x: x['predicted_performance']['composite_score'], reverse=True)
        
        return scripts[:count]
    
    def _parse_user_prompt(self, prompt: str) -> Dict:
        """
        解析用户输入，提取关键信息
        
        使用 LLM 进行语义分析（支持中英文）
        如果 LLM 不可用，回退到基础关键词提取
        """
        if self.llm_available and self.llm_client:
            return self._parse_with_llm(prompt)
        else:
            return self._parse_basic(prompt)
    
    def _parse_with_llm(self, prompt: str) -> Dict:
        """
        使用 LLM 进行智能语义分析
        """
        try:
            system_prompt = """你是一个专业的产品信息提取助手。请从用户输入中提取以下结构化信息（支持中文和英文）：
1. 产品/服务类型（product_type）
2. 目标客户群体（target_customers）
3. 核心优势/卖点（key_advantages，至少3个）
4. 使用场景（use_cases）
5. 行业领域（industry）
6. 产品名称（product_name，如果有）

请以 JSON 格式返回，确保所有字段都有值。如果某个信息不明确，请根据上下文合理推断。"""
            
            user_prompt = f"请分析以下产品/服务描述，提取关键信息：\n\n{prompt}"
            
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",  # 使用更经济的模型
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            llm_output = response.choices[0].message.content.strip()
            
            # 尝试解析 JSON
            try:
                # 提取 JSON 部分（可能包含 markdown 代码块）
                json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                else:
                    parsed_data = json.loads(llm_output)
            except json.JSONDecodeError:
                # 如果 JSON 解析失败，使用基础解析
                print("⚠️ LLM returned invalid JSON, falling back to basic parsing")
                return self._parse_basic(prompt)
            
            # 合并解析结果
            result = {
                'raw_prompt': prompt,
                'description': prompt,
                'product_type': parsed_data.get('product_type', ''),
                'target_customers': parsed_data.get('target_customers', ''),
                'key_advantages': parsed_data.get('key_advantages', []),
                'use_cases': parsed_data.get('use_cases', ''),
                'industry': parsed_data.get('industry', ''),
                'product_name': parsed_data.get('product_name', ''),
                'keywords': self._extract_keywords(prompt),
                'parsed_by': 'llm'
            }
            
            return result
            
        except Exception as e:
            print(f"⚠️ LLM parsing failed: {e}, falling back to basic parsing")
            return self._parse_basic(prompt)
    
    def _parse_basic(self, prompt: str) -> Dict:
        """
        基础解析（不使用 LLM）
        """
        return {
            'raw_prompt': prompt,
            'description': prompt,
            'product_type': '',
            'target_customers': '',
            'key_advantages': [],
            'use_cases': '',
            'industry': '',
            'product_name': '',
            'keywords': self._extract_keywords(prompt),
            'parsed_by': 'basic'
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """简单的关键词提取"""
        # 简化版本：分词
        words = text.split()
        # 过滤停用词
        stop_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
        keywords = [w for w in words if w not in stop_words and len(w) > 1]
        return keywords[:5]
    
    def _generate_single_script(
        self,
        product_info: Dict,
        recommendation: Dict,
        channel_style: Dict,
        target_audience: Dict,
        high_performers: Dict,
        index: int
    ) -> Dict:
        """
        生成单个视频脚本
        """
        # 获取话题信息（使用安全的访问方式）
        keyword = recommendation.get('keyword', '热门话题')
        if not keyword:
            keyword = '产品推广'  # 默认关键词
        content_angle = recommendation.get('content_angle', f'制作关于 {keyword} 的内容')
        suggested_format = recommendation.get('suggested_format', recommendation.get('suggestedFormat', '8-12分钟综合内容'))
        
        # 获取频道风格
        primary_style = channel_style.get('primary_style', 'general')
        age_group = target_audience.get('primary_age_group', '18-24岁')
        
        # 选择脚本模板
        template_type = self._select_template(primary_style, index)
        
        # 生成脚本内容（使用 LLM 或模板）
        if self.llm_available and self.llm_client:
            script_content = self._generate_script_with_llm(
                template_type=template_type,
                keyword=keyword,
                product_info=product_info,
                content_angle=content_angle,
                age_group=age_group,
                channel_style=channel_style,
                target_audience=target_audience
            )
        else:
            script_content = self._generate_script_content(
                template_type=template_type,
                keyword=keyword,
                product_info=product_info,
                content_angle=content_angle,
                age_group=age_group
            )
        
        # 预测性能
        performance = self._predict_script_performance(
            script_content=script_content,
            recommendation=recommendation,
            high_performers=high_performers,
            template_type=template_type
        )
        
        # 生成推荐理由
        reasoning = self._generate_reasoning(
            keyword=keyword,
            recommendation=recommendation,
            performance=performance,
            template_type=template_type
        )
        
        return {
            'id': f"script_{index + 1}",
            'title': script_content['title'],
            'keyword': keyword,
            'template_type': template_type,
            'script': script_content,
            'predicted_performance': performance,
            'reasoning': reasoning,
            'recommendation_source': {
                'match_score': recommendation.get('match_score', 0),
                'urgency': recommendation.get('urgency', 'medium')
            },
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _select_template(self, style: str, index: int) -> str:
        """
        根据频道风格和序号选择脚本模板
        """
        style_templates = {
            'tutorial': ['step_by_step', 'problem_solution', 'tips_tricks'],
            'review': ['honest_review', 'comparison', 'unboxing'],
            'entertainment': ['story_telling', 'challenge', 'reaction'],
            'educational': ['explainer', 'deep_dive', 'myth_busting'],
            'vlog': ['day_in_life', 'behind_scenes', 'personal_story']
        }
        
        templates = style_templates.get(style, ['hook_content_cta', 'problem_solution', 'story_telling'])
        return templates[index % len(templates)]
    
    def _generate_script_with_llm(
        self,
        template_type: str,
        keyword: str,
        product_info: Dict,
        content_angle: str,
        age_group: str,
        channel_style: Dict,
        target_audience: Dict
    ) -> Dict:
        """
        使用 LLM 生成智能脚本内容
        """
        try:
            # 构建详细的上下文信息
            product_desc = product_info.get('description', '')
            product_type = product_info.get('product_type', '')
            key_advantages = product_info.get('key_advantages', [])
            target_customers = product_info.get('target_customers', '')
            
            primary_style = channel_style.get('primary_style', 'general')
            primary_age = target_audience.get('primary_age_group', age_group)
            
            # 模板说明
            template_descriptions = {
                'hook_content_cta': '经典三段式：Hook（吸引注意力）- 主体内容 - CTA（行动号召）',
                'problem_solution': '问题-解决方案模式：提出问题 → 分析问题 → 提供解决方案',
                'story_telling': '故事叙述模式：通过真实故事展示产品价值',
                'step_by_step': '分步教程模式：清晰的步骤指导',
                'honest_review': '真实测评模式：客观评价产品优缺点'
            }
            
            template_desc = template_descriptions.get(template_type, '综合内容模式')
            
            system_prompt = f"""你是一个专业的 YouTube 视频脚本创作专家。请根据以下信息生成一个完整的视频脚本。

脚本结构要求：
- 模板类型：{template_desc}
- 时长：8-12分钟
- 目标受众：{primary_age}
- 频道风格：{primary_style}

请生成包含以下部分的完整脚本（JSON 格式）：
1. title: 吸引人的视频标题
2. duration: 建议时长（如 "8-10分钟"）
3. structure: 脚本结构说明
4. hook: 开场部分（包含 content, duration, techniques, visual_suggestion）
5. main_content: 主体内容（包含多个 sections，每个 section 有 title, duration, content, engagement）
6. cta: 结尾行动号召（包含 content, duration, techniques, placement）
7. key_points: 关键要点列表（至少4个）

要求：
- 内容要自然融入产品信息，避免硬广
- 语言风格要符合目标受众年龄
- 要有具体的视觉建议和互动技巧
- 确保脚本结构完整、逻辑清晰"""

            user_prompt = f"""请为以下内容生成视频脚本：

【话题关键词】{keyword}
【内容角度】{content_angle}
【产品/服务描述】{product_desc}
【产品类型】{product_type}
【核心优势】{', '.join(key_advantages) if key_advantages else '未指定'}
【目标客户】{target_customers}

请生成一个专业、吸引人且实用的视频脚本。"""
            
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            llm_output = response.choices[0].message.content.strip()
            
            # 尝试解析 JSON
            try:
                json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
                if json_match:
                    script_data = json.loads(json_match.group())
                else:
                    script_data = json.loads(llm_output)
                
                # 验证必要字段
                if 'title' not in script_data:
                    script_data['title'] = self._generate_title(template_type, keyword, product_desc)
                if 'hook' not in script_data:
                    raise ValueError("LLM response missing required fields")
                
                return script_data
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ LLM returned invalid script format: {e}, falling back to template")
                return self._generate_script_content(
                    template_type=template_type,
                    keyword=keyword,
                    product_info=product_info,
                    content_angle=content_angle,
                    age_group=age_group
                )
                
        except Exception as e:
            print(f"⚠️ LLM script generation failed: {e}, falling back to template")
            return self._generate_script_content(
                template_type=template_type,
                keyword=keyword,
                product_info=product_info,
                content_angle=content_angle,
                age_group=age_group
            )
    
    def _generate_script_content(
        self,
        template_type: str,
        keyword: str,
        product_info: Dict,
        content_angle: str,
        age_group: str
    ) -> Dict:
        """
        根据模板生成脚本内容
        """
        product_desc = product_info.get('description', '')
        
        # 生成标题
        title = self._generate_title(template_type, keyword, product_desc)
        
        # 生成脚本各部分
        if template_type == 'hook_content_cta':
            script = self._template_hook_content_cta(keyword, product_desc, age_group)
        elif template_type == 'problem_solution':
            script = self._template_problem_solution(keyword, product_desc, age_group)
        elif template_type == 'story_telling':
            script = self._template_story_telling(keyword, product_desc, age_group)
        elif template_type == 'step_by_step':
            script = self._template_step_by_step(keyword, product_desc, age_group)
        elif template_type == 'honest_review':
            script = self._template_honest_review(keyword, product_desc, age_group)
        else:
            script = self._template_hook_content_cta(keyword, product_desc, age_group)
        
        return {
            'title': title,
            'duration': script['duration'],
            'structure': script['structure'],
            'hook': script['hook'],
            'main_content': script['main_content'],
            'cta': script['cta'],
            'key_points': script['key_points']
        }
    
    def _generate_title(self, template_type: str, keyword: str, product: str) -> str:
        """生成视频标题"""
        title_templates = {
            'hook_content_cta': f"🔥 {keyword}最强攻略！99%的人不知道的{product}秘密",
            'problem_solution': f"还在为{keyword}烦恼？{product}帮你轻松解决！",
            'story_telling': f"我是如何用{product}改变{keyword}的...",
            'step_by_step': f"{keyword}完整教程：5步掌握{product}",
            'honest_review': f"{keyword}真实测评：{product}值得买吗？"
        }
        return title_templates.get(template_type, f"{keyword} × {product}")
    
    def _template_hook_content_cta(self, keyword: str, product: str, age_group: str) -> Dict:
        """Hook-Content-CTA 模板"""
        return {
            'duration': '8-10分钟',
            'structure': 'Hook (0-15秒) → 主体内容 (6-8分钟) → CTA (30-60秒)',
            'hook': {
                'content': f"你知道吗？关于{keyword}，有90%的人都理解错了！今天我要揭秘{product}背后的真相...",
                'duration': '前15秒',
                'techniques': ['惊人数据', '反常识观点', '制造悬念'],
                'visual_suggestion': '快节奏剪辑 + 醒目字幕'
            },
            'main_content': {
                'sections': [
                    {
                        'title': f'为什么{keyword}这么重要？',
                        'duration': '1-2分钟',
                        'content': f'分析{keyword}的现状和痛点，引出{product}的必要性',
                        'engagement': '使用数据、案例、对比'
                    },
                    {
                        'title': f'{product}的3大核心优势',
                        'duration': '3-4分钟',
                        'content': '详细展示产品特点和使用效果',
                        'engagement': '实际演示 + 用户评价 + 前后对比'
                    },
                    {
                        'title': '常见问题解答',
                        'duration': '2-3分钟',
                        'content': '回答观众最关心的问题',
                        'engagement': '问答形式 + 互动评论'
                    }
                ]
            },
            'cta': {
                'content': f"如果你也想尝试{product}，记得点赞收藏！评论区告诉我你最关心的是什么～",
                'duration': '最后30秒',
                'techniques': ['软性引导', '互动提问', '福利预告'],
                'placement': ['视频结尾', '置顶评论', '视频描述']
            },
            'key_points': [
                f'开场15秒内必须抓住注意力',
                f'主体内容围绕{product}解决{keyword}问题',
                f'结尾CTA自然不突兀',
                f'全程保持{age_group}的语言风格'
            ]
        }
    
    def _template_problem_solution(self, keyword: str, product: str, age_group: str) -> Dict:
        """问题-解决方案模板"""
        return {
            'duration': '8-12分钟',
            'structure': '提出问题 (1分钟) → 分析问题 (3分钟) → 解决方案 (4-6分钟) → 总结 (1分钟)',
            'hook': {
                'content': f"你是不是也遇到过这种情况：{keyword}总是让人头疼？今天教你一招彻底解决！",
                'duration': '前30秒',
                'techniques': ['共鸣式开场', '列举常见痛点', '承诺解决方案'],
                'visual_suggestion': '场景重现 + 夸张表演'
            },
            'main_content': {
                'sections': [
                    {
                        'title': f'为什么{keyword}这么难搞？',
                        'duration': '2-3分钟',
                        'content': '深入分析问题原因，3-5个常见误区',
                        'engagement': '观众痛点列举 + 错误案例'
                    },
                    {
                        'title': f'我的解决方案：{product}',
                        'duration': '4-6分钟',
                        'content': '分步演示如何使用产品解决问题',
                        'engagement': '手把手教学 + 实时效果展示'
                    },
                    {
                        'title': '效果对比',
                        'duration': '1-2分钟',
                        'content': '使用前后的真实对比',
                        'engagement': '数据对比 + 视觉对比'
                    }
                ]
            },
            'cta': {
                'content': f"现在你知道怎么解决{keyword}的问题了！试试看，记得在评论区告诉我效果如何！",
                'duration': '最后30秒',
                'techniques': ['价值总结', '行动呼吁', '互动引导'],
                'placement': ['视频结尾', '字幕提示']
            },
            'key_points': [
                '问题描述要具体、有共鸣',
                '解决方案要清晰、可执行',
                '效果对比要真实、有说服力',
                '语言要简单易懂'
            ]
        }
    
    def _template_story_telling(self, keyword: str, product: str, age_group: str) -> Dict:
        """故事叙述模板"""
        return {
            'duration': '10-15分钟',
            'structure': '故事背景 (1-2分钟) → 冲突/挑战 (3-4分钟) → 转折点 (4-5分钟) → 结局/启示 (2-3分钟)',
            'hook': {
                'content': f"说实话，我以前从来不相信{keyword}能改变什么...直到我遇到了{product}",
                'duration': '前20秒',
                'techniques': ['个人化开场', '制造好奇', '情感连接'],
                'visual_suggestion': '第一人称视角 + 真实场景'
            },
            'main_content': {
                'sections': [
                    {
                        'title': '我的故事',
                        'duration': '3-4分钟',
                        'content': f'讲述自己在{keyword}方面的真实经历和困扰',
                        'engagement': '细节描述 + 情感表达 + 共鸣点'
                    },
                    {
                        'title': f'遇见{product}的转折',
                        'duration': '4-5分钟',
                        'content': f'如何发现并开始使用{product}，过程中的变化',
                        'engagement': '时间线叙述 + 过程记录 + 感受分享'
                    },
                    {
                        'title': '现在的改变',
                        'duration': '2-3分钟',
                        'content': '使用后的真实效果和生活改变',
                        'engagement': '前后对比 + 具体数据 + 感悟总结'
                    }
                ]
            },
            'cta': {
                'content': f"这是我的{keyword}改变之路，你也有类似的经历吗？评论区聊聊～",
                'duration': '最后1分钟',
                'techniques': ['情感共鸣', '开放式提问', '社区归属感'],
                'placement': ['自然融入故事结尾']
            },
            'key_points': [
                '故事要真实可信',
                '情感要真挚自然',
                '产品植入要自然不生硬',
                '结尾要有启发性'
            ]
        }
    
    def _template_step_by_step(self, keyword: str, product: str, age_group: str) -> Dict:
        """分步教程模板"""
        return {
            'duration': '10-12分钟',
            'structure': '简介 (30秒) → 准备工作 (1分钟) → 分步教学 (7-8分钟) → 总结 (1-2分钟)',
            'hook': {
                'content': f"今天教大家如何用{product}轻松搞定{keyword}！全程手把手，新手也能学会！",
                'duration': '前30秒',
                'techniques': ['明确目标', '降低门槛', '承诺结果'],
                'visual_suggestion': '清晰字幕 + 步骤预览'
            },
            'main_content': {
                'sections': [
                    {
                        'title': '准备工作',
                        'duration': '1分钟',
                        'content': f'需要的工具和{product}的准备',
                        'engagement': '清单展示 + 注意事项'
                    },
                    {
                        'title': '第一步：基础设置',
                        'duration': '2-3分钟',
                        'content': f'如何开始使用{product}解决{keyword}',
                        'engagement': '屏幕录制 + 详细解说'
                    },
                    {
                        'title': '第二步：核心操作',
                        'duration': '3-4分钟',
                        'content': '最重要的使用技巧和方法',
                        'engagement': '实时演示 + 常见错误提示'
                    },
                    {
                        'title': '第三步：优化提升',
                        'duration': '2-3分钟',
                        'content': '进阶技巧和个性化调整',
                        'engagement': '对比展示 + 效果说明'
                    }
                ]
            },
            'cta': {
                'content': "教程就到这里！是不是很简单？点赞收藏，下次需要的时候能找到～",
                'duration': '最后1分钟',
                'techniques': ['操作总结', '保存提示', '系列预告'],
                'placement': ['视频结尾 + 字幕总结']
            },
            'key_points': [
                '每一步都要清晰明确',
                '节奏不要太快',
                '重点部分可以重复或慢放',
                '配上清晰的字幕和箭头指示'
            ]
        }
    
    def _template_honest_review(self, keyword: str, product: str, age_group: str) -> Dict:
        """真实测评模板"""
        return {
            'duration': '8-10分钟',
            'structure': '产品介绍 (1分钟) → 优点分析 (3-4分钟) → 缺点分析 (2-3分钟) → 购买建议 (1-2分钟)',
            'hook': {
                'content': f"关于{product}在{keyword}方面的表现，我有话要说！这是我用了一个月的真实感受",
                'duration': '前20秒',
                'techniques': ['真实性强调', '使用时长证明', '客观态度'],
                'visual_suggestion': '产品实拍 + 使用痕迹'
            },
            'main_content': {
                'sections': [
                    {
                        'title': f'{product}基本介绍',
                        'duration': '1分钟',
                        'content': f'产品定位、适用场景、与{keyword}的关系',
                        'engagement': '快速展示 + 核心卖点'
                    },
                    {
                        'title': '我喜欢的3个优点',
                        'duration': '3-4分钟',
                        'content': '详细说明产品的突出优势',
                        'engagement': '实际使用场景 + 对比展示'
                    },
                    {
                        'title': '说说缺点（很重要）',
                        'duration': '2-3分钟',
                        'content': '客观指出不足之处',
                        'engagement': '真实使用问题 + 改进建议'
                    },
                    {
                        'title': '适合谁？不适合谁？',
                        'duration': '1-2分钟',
                        'content': '给出明确的购买建议',
                        'engagement': '用户画像 + 使用场景'
                    }
                ]
            },
            'cta': {
                'content': f"以上就是我对{product}的真实看法！你们用过吗？评论区聊聊你的体验～",
                'duration': '最后30秒',
                'techniques': ['观点总结', '互动邀请', '持续关注'],
                'placement': ['客观总结 + 互动引导']
            },
            'key_points': [
                '态度要客观中立',
                '优缺点都要说',
                '给出明确的适用人群',
                '避免过度营销感'
            ]
        }
    
    def _predict_script_performance(
        self,
        script_content: Dict,
        recommendation: Dict,
        high_performers: Dict,
        template_type: str
    ) -> Dict:
        """
        预测脚本表现
        """
        # 基础预测播放量
        avg_views = high_performers.get('avg_views', 10000) if high_performers else 10000
        median_views = high_performers.get('median_views', avg_views) if high_performers else avg_views
        
        # 基于推荐评分的系数
        match_score = recommendation.get('match_score', 70)
        viral_potential = recommendation.get('viral_potential', 50)
        
        # 模板类型加成
        template_multipliers = {
            'hook_content_cta': 1.2,      # 经典结构，效果稳定
            'problem_solution': 1.15,     # 实用性强
            'story_telling': 1.3,         # 情感共鸣，容易分享
            'step_by_step': 1.1,          # 教程类，收藏率高
            'honest_review': 1.25         # 真实性强，信任度高
        }
        
        template_multiplier = template_multipliers.get(template_type, 1.0)
        
        # 计算预测播放量
        base_multiplier = 1.0 + (match_score / 100) * 0.5
        viral_multiplier = 1.0 + (viral_potential / 100) * 0.3
        
        predicted_views = int(
            median_views * base_multiplier * viral_multiplier * template_multiplier
        )
        
        # 预测互动率
        predicted_engagement_rate = self._calculate_engagement_rate(
            template_type, match_score
        )
        
        predicted_likes = int(predicted_views * predicted_engagement_rate * 0.05)
        predicted_comments = int(predicted_views * predicted_engagement_rate * 0.01)
        predicted_shares = int(predicted_views * predicted_engagement_rate * 0.005)
        
        # 综合评分
        composite_score = (
            (match_score * 0.4) +
            (viral_potential * 0.3) +
            (template_multiplier * 100 * 0.3)
        )
        
        return {
            'predicted_views': predicted_views,
            'predicted_views_range': {
                'min': int(predicted_views * 0.7),
                'max': int(predicted_views * 1.5)
            },
            'predicted_engagement': {
                'rate': round(predicted_engagement_rate, 4),
                'likes': predicted_likes,
                'comments': predicted_comments,
                'shares': predicted_shares
            },
            'composite_score': round(composite_score, 2),
            'confidence': self._calculate_confidence(match_score, viral_potential),
            'viral_potential': recommendation.get('viral_potential', 50),
            'expected_performance_tier': self._determine_tier(composite_score)
        }
    
    def _calculate_engagement_rate(self, template_type: str, match_score: float) -> float:
        """计算预测互动率"""
        # 基础互动率
        base_rates = {
            'hook_content_cta': 0.045,
            'problem_solution': 0.042,
            'story_telling': 0.055,  # 故事类互动率最高
            'step_by_step': 0.048,
            'honest_review': 0.050
        }
        
        base_rate = base_rates.get(template_type, 0.045)
        
        # 基于匹配度调整
        adjustment = 1.0 + (match_score - 70) / 100 * 0.2
        
        return base_rate * adjustment
    
    def _calculate_confidence(self, match_score: float, viral_potential: float) -> float:
        """计算预测置信度"""
        return round((match_score * 0.6 + viral_potential * 0.4), 1)
    
    def _determine_tier(self, composite_score: float) -> str:
        """确定表现等级"""
        if composite_score >= 85:
            return 'excellent'
        elif composite_score >= 70:
            return 'good'
        elif composite_score >= 55:
            return 'moderate'
        else:
            return 'average'
    
    def _generate_reasoning(
        self,
        keyword: str,
        recommendation: Dict,
        performance: Dict,
        template_type: str
    ) -> Dict:
        """
        生成推荐理由
        """
        reasons = []
        
        # 话题匹配度
        match_score = recommendation.get('match_score', 0)
        if match_score >= 80:
            reasons.append(f"✅ 话题'{keyword}'与频道高度匹配（{match_score:.0f}分）")
        elif match_score >= 60:
            reasons.append(f"✓ 话题'{keyword}'与频道较为匹配（{match_score:.0f}分）")
        
        # 病毒潜力
        viral_potential = recommendation.get('viral_potential', 0)
        if viral_potential >= 80:
            reasons.append(f"🔥 话题热度极高，病毒传播潜力大（{viral_potential:.0f}分）")
        elif viral_potential >= 60:
            reasons.append(f"📈 话题当前热度较高（{viral_potential:.0f}分）")
        
        # 模板优势
        template_advantages = {
            'hook_content_cta': '采用经典Hook-Content-CTA结构，播放完成率高',
            'problem_solution': '问题-解决方案模式，实用性强，收藏率高',
            'story_telling': '故事化叙述，情感共鸣强，分享率高',
            'step_by_step': '分步教程清晰易懂，用户粘性强',
            'honest_review': '真实测评客观中立，建立信任感'
        }
        reasons.append(f"💡 {template_advantages.get(template_type, '脚本结构合理')}")
        
        # 预测表现
        tier = performance['expected_performance_tier']
        if tier == 'excellent':
            reasons.append("⭐ 预计表现优异，可能成为爆款内容")
        elif tier == 'good':
            reasons.append("✓ 预计表现良好，高于平均水平")
        
        # 紧急度
        urgency = recommendation.get('urgency', 'medium')
        if urgency == 'urgent':
            reasons.append("⏰ 话题时效性强，建议48小时内发布")
        elif urgency == 'high':
            reasons.append("📅 建议本周内发布，抓住热度窗口")
        
        return {
            'summary': '；'.join(reasons),
            'strengths': [
                f"话题热度: {viral_potential:.0f}/100",
                f"匹配度: {match_score:.0f}/100",
                f"脚本质量: {template_type} 模板"
            ],
            'tips': [
                "开场15秒内抓住观众注意力",
                "自然融入产品，避免硬广",
                "结尾引导互动，提升参与度",
                "配上高质量字幕和剪辑"
            ]
        }
    
    def _initialize_templates(self) -> Dict:
        """初始化脚本模板库"""
        return {
            'hook_content_cta': '经典三段式',
            'problem_solution': '问题解决',
            'story_telling': '故事叙述',
            'step_by_step': '分步教程',
            'honest_review': '真实测评'
        }


# 初始化引擎
script_generator = ScriptGeneratorEngine()
