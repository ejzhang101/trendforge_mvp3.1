'use client';

import { useEffect, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  TrendingUp,
  Users,
  Video,
  Eye,
  ThumbsUp,
  Sparkles,
  ArrowLeft,
  ExternalLink,
  Target,
  Zap,
  Clock,
  TrendingDown,
  Award,
  AlertCircle,
} from 'lucide-react';
import TrendPredictionChart from '@/components/TrendPredictionChart';

interface Recommendation {
  id: string;
  keyword: string;
  matchScore: number;
  viralPotential?: number;
  performanceScore?: number;
  relevanceScore: number;
  opportunityScore: number;
  reasoning: string;
  contentAngle: string;
  urgency: string;
  predictedPerformance: {
    tier: string;
    predicted_views: number;
    description: string;
    confidence: number;
  };
  suggestedFormat: string;
  suggestedTitles: Array<{
    title: string;
    strategy: string;
    predicted_ctr: number;
    reasoning: string;
    character_count: number;
  }>;
  sources: string[];
  relatedInfo: {
    rising_queries: string[];
    hashtags: string[];
    subreddits: string[];
  };
  prediction?: {  // MVP 3.0: Prophet 预测数据
    trend_direction: 'rising' | 'falling' | 'stable';
    trend_strength: number;
    confidence: number;
    peak_day: number | null;
    peak_score: number;
    summary: string;
  };
}

export default function AnalysisPageV2() {
  const params = useParams();
  const router = useRouter();
  const channelId = params.channelId as string;

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);
  const [activeTab, setActiveTab] = useState<'details' | 'prediction'>('details');
  const [error, setError] = useState<string | null>(null);
  const fetchedForChannelIdRef = useRef<string | null>(null);

  const fetchResults = async () => {
    try {
      setError(null);
      const res = await fetch(`/api/analysis/${channelId}`);
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      const result = await res.json();
      
      // Debug: Log prediction data
      console.log('📊 Analysis data received:', {
        hasTrendPredictions: !!result.trendPredictions,
        trendPredictionsCount: result.trendPredictions?.length || 0,
        hasEmergingTrends: !!result.emergingTrends,
        emergingTrendsCount: result.emergingTrends?.length || 0,
        recommendationsWithPrediction: result.recommendations?.filter((r: any) => r.prediction?.peak_day).length || 0,
        firstPrediction: result.trendPredictions?.[0],
        firstEmergingTrend: result.emergingTrends?.[0],
        firstRecommendation: result.recommendations?.[0]
      });
      
      setData(result);
    } catch (error) {
      console.error('Failed to fetch:', error);
      setError(error instanceof Error ? error.message : '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // React StrictMode (dev) may invoke effects twice; guard to avoid duplicate long requests
    if (!channelId) return;
    if (fetchedForChannelIdRef.current === channelId) return;
    fetchedForChannelIdRef.current = channelId;
    fetchResults();
  }, [channelId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-500 mx-auto mb-4"></div>
          <p className="text-purple-300 text-lg">AI 正在深度分析频道...</p>
          <p className="text-purple-400 text-sm mt-2">分析内容、社交趋势、生成建议</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <p className="text-white text-xl mb-2">加载失败</p>
          <p className="text-purple-300 text-sm mb-4">{error}</p>
          <button
            onClick={() => {
              setError(null);
              setLoading(true);
              fetchResults();
            }}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg mr-4"
          >
            重试
          </button>
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg"
          >
            返回首页
          </button>
        </div>
      </div>
    );
  }

  if (!data || !data.channel) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <p className="text-white text-xl">未找到分析结果</p>
          <button
            onClick={() => router.push('/')}
            className="mt-4 px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
          >
            返回首页
          </button>
        </div>
      </div>
    );
  }

  const getUrgencyBadge = (urgency: string) => {
    const badges = {
      urgent: { color: 'bg-red-500', icon: '🔥', text: '紧急' },
      high: { color: 'bg-orange-500', icon: '⚡', text: '高优先级' },
      medium: { color: 'bg-yellow-500', icon: '📌', text: '中等' },
      low: { color: 'bg-blue-500', icon: '💡', text: '低优先级' },
    };
    const badge = badges[urgency as keyof typeof badges] || badges.low;
    return (
      <span className={`${badge.color} text-white px-2 py-1 rounded text-xs font-bold`}>
        {badge.icon} {badge.text}
      </span>
    );
  };

  const getPerformanceTierColor = (tier: string) => {
    const colors = {
      excellent: 'text-green-400',
      good: 'text-blue-400',
      moderate: 'text-yellow-400',
      low: 'text-gray-400',
    };
    return colors[tier as keyof typeof colors] || colors.low;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-purple-300 hover:text-white mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          分析其他频道
        </button>

        {/* Channel Header */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-8 border border-white/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              {data.channel.thumbnailUrl ? (
                <img
                  src={data.channel.thumbnailUrl}
                  alt={data.channel.title}
                  className="w-24 h-24 rounded-full border-4 border-purple-400 object-cover"
                  onError={(e) => {
                    // Fallback to default avatar if image fails to load
                    (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${encodeURIComponent(data.channel.title || 'Channel')}&background=8b5cf6&color=fff&size=128`;
                  }}
                />
              ) : (
                <div className="w-24 h-24 rounded-full border-4 border-purple-400 bg-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                  {data.channel.title?.[0]?.toUpperCase() || '?'}
                </div>
              )}
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">{data.channel.title}</h1>
                <div className="flex items-center gap-6 text-purple-200">
                  <span className="flex items-center gap-2">
                    <Users className="w-5 h-5" />
                    {data.channel.subscriberCount.toLocaleString()} 订阅者
                  </span>
                  {data.analysis && (
                    <span className="flex items-center gap-2">
                      <Video className="w-5 h-5" />
                      分析了 {data.analysis.videosAnalyzed} 个视频
                    </span>
                  )}
                </div>
              </div>
            </div>
            <a
              href={`https://youtube.com/channel/${channelId}`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center gap-2"
            >
              访问频道
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>

        {/* Analysis Summary */}
        {data.analysis && (
          <>
            {/* Content Style & Audience */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <Target className="w-6 h-6 text-purple-400" />
                  内容风格
                </h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-purple-300">主要风格：</span>
                    <span className="text-white font-semibold ml-2">
                      {data.analysis.contentStyle?.primary_style || 'general'}
                    </span>
                  </div>
                  {data.analysis.contentStyle?.style_distribution && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {Object.entries(data.analysis.contentStyle.style_distribution).map(
                        ([style, count]: [string, any]) => (
                          <span
                            key={style}
                            className="px-3 py-1 bg-purple-600/50 rounded-full text-white text-sm"
                          >
                            {style}: {count}
                          </span>
                        )
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <Users className="w-6 h-6 text-blue-400" />
                  目标受众
                </h3>
                <div className="space-y-4">
                  {/* 精细年龄段分类 */}
                  <div>
                    <span className="text-purple-300 text-sm">精细年龄段分类：</span>
                    <div className="mt-2">
                      <div className="flex items-center gap-2">
                        <span className="text-white font-semibold">
                          {data.analysis.targetAudience?.primary_age_group || '18-24岁 (大学生/年轻人)'}
                        </span>
                        {data.analysis.targetAudience?.age_confidence && (
                          <span className="text-purple-400 text-xs">
                            ({data.analysis.targetAudience.age_confidence})
                          </span>
                        )}
                      </div>
                      {data.analysis.targetAudience?.secondary_age_group && (
                        <div className="mt-1 text-purple-300 text-sm">
                          次要：<span className="text-white">{data.analysis.targetAudience.secondary_age_group}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {/* 核心兴趣标签 */}
                  {data.analysis.targetAudience?.top_interests && data.analysis.targetAudience.top_interests.length > 0 && (
                    <div>
                      <span className="text-purple-300 text-sm">核心兴趣标签：</span>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {data.analysis.targetAudience.top_interests.map((interest: string, idx: number) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-blue-600/50 rounded-full text-white text-sm"
                          >
                            {interest}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* 互动水平 */}
                  <div>
                    <span className="text-purple-300 text-sm">互动水平：</span>
                    <span className="text-white font-semibold ml-2">
                      {data.analysis.targetAudience?.engagement_level || '中等 (正常水平)'}
                    </span>
                    {data.analysis.targetAudience?.engagement_rate && (
                      <span className="text-purple-400 text-xs ml-2">
                        ({data.analysis.targetAudience.engagement_rate})
                      </span>
                    )}
                  </div>
                  
                  {/* 消费能力 */}
                  <div>
                    <span className="text-purple-300 text-sm">消费能力：</span>
                    <span className="text-white font-semibold ml-2">
                      {data.analysis.targetAudience?.purchasing_power || '中等消费'}
                    </span>
                  </div>
                  
                  {/* 频道规模 */}
                  <div>
                    <span className="text-purple-300 text-sm">频道规模：</span>
                    <span className="text-white font-semibold ml-2">
                      {data.analysis.targetAudience?.audience_size_tier || '中型频道 (1万-10万)'}
                    </span>
                  </div>
                  
                  {/* 受众洞察 */}
                  {data.analysis.targetAudience?.audience_insights && (
                    <div className="mt-4 pt-3 border-t border-white/10">
                      <p className="text-purple-200 text-sm italic">
                        💡 {data.analysis.targetAudience.audience_insights}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Core Topics */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 mb-8 border border-white/20">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white">🎯 核心主题</h3>
                <div className="text-xs text-purple-300 flex items-center gap-2">
                  <span className="px-2 py-1 bg-purple-600/30 rounded">分数说明</span>
                  <span className="text-purple-400">0.9-1.0: 核心</span>
                  <span className="text-purple-300">0.7-0.9: 次要</span>
                  <span className="text-purple-200">0.5-0.7: 辅助</span>
                  <span className="text-gray-400">&lt;0.5: 边缘</span>
                </div>
              </div>
              <div className="flex flex-wrap gap-3">
                {data.analysis.topics?.slice(0, 15).map((topic: any, idx: number) => {
                  const score = topic.score || 0;
                  let label = '';
                  let labelColor = 'bg-gray-500';
                  
                  if (score >= 0.9) {
                    label = '核心';
                    labelColor = 'bg-red-500';
                  } else if (score >= 0.7) {
                    label = '次要';
                    labelColor = 'bg-orange-500';
                  } else if (score >= 0.5) {
                    label = '辅助';
                    labelColor = 'bg-yellow-500';
                  } else {
                    label = '边缘';
                    labelColor = 'bg-gray-500';
                  }
                  
                  return (
                    <div
                      key={idx}
                      className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full flex items-center gap-2"
                    >
                      <span className="text-white font-medium">{topic.topic}</span>
                      <span className={`${labelColor} text-white text-xs px-2 py-0.5 rounded-full font-bold`}>
                        {label}
                      </span>
                      <span className="text-purple-200 text-xs" title={`TF-IDF 重要性分数: ${score.toFixed(2)} (${(score * 100).toFixed(0)}%)`}>
                        {score.toFixed(2)}
                      </span>
                    </div>
                  );
                })}
              </div>
              <p className="text-purple-300 text-xs mt-4 italic">
                💡 数字是 TF-IDF 重要性分数 (0-1之间)，表示该主题在频道中的重要程度
              </p>
            </div>
          </>
        )}


        {/* MVP 3.0: Emerging Trends Section */}
        {(() => {
          // 去重逻辑：过滤掉那些已经在"AI 智能推荐话题"中显示的关键词
          const recommendationKeywords = new Set(
            (data.recommendations || []).map((rec: Recommendation) => rec.keyword?.toLowerCase().trim())
          );
          
          const allTrends = Array.isArray(data.emergingTrends) ? data.emergingTrends : [];
          const uniqueTrends = allTrends.filter((trend: any) => {
            const keyword = trend.keyword?.toLowerCase().trim();
            // 只显示不在推荐列表中的新兴趋势，避免重复
            return keyword && !recommendationKeywords.has(keyword);
          });
          
          if (uniqueTrends.length === 0) {
            return null;
          }
          
          return (
          <div className="bg-gradient-to-br from-yellow-600/20 to-orange-600/20 rounded-2xl p-6 mb-8 border border-yellow-500/30">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
              <Zap className="w-6 h-6 text-yellow-400" />
              ⚡ 新兴趋势识别 - 即将爆发的话题
            </h2>
            <p className="text-purple-300 text-sm mb-6">
              基于 Prophet 预测模型识别的高置信度上升趋势话题，建议优先关注
              {recommendationKeywords.size > 0 && (
                <span className="block mt-2 text-xs text-yellow-400">
                  💡 已过滤与"AI 智能推荐话题"重复的关键词，避免重复展示
                </span>
              )}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {uniqueTrends.map((trend: any, idx: number) => {
                console.log(`📊 Rendering emerging trend ${idx}:`, {
                  keyword: trend.keyword,
                  peak_day: trend.peak_day,
                  peak_score: trend.peak_score,
                  hasPeakDay: trend.peak_day != null && trend.peak_day > 0
                });
                return (
                  <div
                    key={idx}
                    className="bg-white/10 rounded-xl p-4 border border-yellow-500/20"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-semibold text-white">{trend.keyword}</h3>
                      <span className="px-2 py-1 bg-yellow-500/30 text-yellow-200 rounded text-xs font-semibold">
                        紧急度: {trend.urgency?.toFixed(0) || 'N/A'}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm mb-2">
                      <span className="text-purple-300">
                        置信度: <span className="font-semibold text-green-400">{trend.confidence?.toFixed(0) || 'N/A'}%</span>
                      </span>
                      <span className="text-purple-300">
                        趋势强度: <span className="font-semibold text-yellow-400">{trend.trend_strength?.toFixed(0) || 'N/A'}</span>
                      </span>
                    </div>
                    {trend.peak_day != null && trend.peak_day > 0 && (
                      <p className="text-xs text-yellow-300">
                        🎯 预计第{trend.peak_day}天达到峰值
                      </p>
                    )}
                    {trend.summary && (
                      <p className="text-xs text-purple-200 mt-2 italic">{trend.summary}</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          );
        })()}

        {/* Recommendations Section */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-8 border border-white/20">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-yellow-400" />
              AI 智能推荐话题
            </h2>
            {data.summary && (
              <div className="text-sm text-purple-300">
                {data.summary.total_recommendations} 个推荐 ·{' '}
                {data.summary.urgent_count} 个紧急 ·{' '}
                平均匹配度 {data.summary.avg_match_score?.toFixed(0)}
              </div>
            )}
          </div>

          {data.recommendations && data.recommendations.length > 0 ? (() => {
            // 前端去重：确保每个关键词只显示一次（保留匹配度最高的）
            const seenKeywords = new Map<string, Recommendation>();
            data.recommendations.forEach((rec: Recommendation) => {
              const keywordLower = rec.keyword?.toLowerCase().trim() || '';
              if (keywordLower) {
                const existing = seenKeywords.get(keywordLower);
                if (!existing || (rec.matchScore > existing.matchScore)) {
                  seenKeywords.set(keywordLower, rec);
                }
              }
            });
            const uniqueRecommendations = Array.from(seenKeywords.values());
            
            return (
              <div className="space-y-4">
                {uniqueRecommendations.map((rec: Recommendation) => (
                <div
                  key={rec.id}
                  className="bg-white/5 hover:bg-white/10 rounded-xl p-5 border border-white/10 transition-all cursor-pointer"
                  onClick={() => {
                    setSelectedRec(rec);
                    setActiveTab('details'); // Reset to details tab when opening
                  }}
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold text-white">{rec.keyword}</h3>
                        {getUrgencyBadge(rec.urgency)}
                        {rec.sources && rec.sources.length > 1 && (
                          <span className="px-2 py-1 bg-blue-500/30 text-blue-200 rounded text-xs">
                            {rec.sources.length} 平台
                          </span>
                        )}
                      </div>
                      <p className="text-purple-300 text-sm">{rec.contentAngle}</p>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-3xl font-bold text-purple-400">{rec.matchScore}</div>
                      <div className="text-xs text-purple-300">匹配度</div>
                    </div>
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-4 gap-4 mb-3 pt-3 border-t border-white/10">
                    <div className="group relative">
                      <div className="text-sm text-purple-300 flex items-center gap-1">
                        匹配度
                        <span className="text-xs cursor-help" title="综合评分 = 互联网热度×40% + 表现潜力×25% + 内容相关性×35%">ℹ️</span>
                      </div>
                      <div className="text-lg font-semibold text-white">
                        {rec.matchScore?.toFixed(0)}
                      </div>
                      <div className="text-xs text-purple-400 mt-1">
                        {rec.matchScore >= 80 ? '⭐⭐⭐ 强烈推荐' : 
                         rec.matchScore >= 60 ? '⭐⭐ 推荐' : 
                         rec.matchScore >= 40 ? '⭐ 可考虑' : '不推荐'}
                      </div>
                    </div>
                    <div className="group relative">
                      <div className="text-sm text-purple-300 flex items-center gap-1">
                        互联网热度
                        <span className="text-xs cursor-help" title="衡量话题在社交媒体的讨论热度（Twitter+Reddit+Google Trends）">ℹ️</span>
                      </div>
                      <div className="text-lg font-semibold text-green-400">
                        {rec.viralPotential?.toFixed(0) || rec.opportunityScore?.toFixed(0) || 'N/A'}
                      </div>
                      <div className="text-xs text-purple-400 mt-1">
                        {(rec.viralPotential ?? 0) >= 90 || (rec.opportunityScore ?? 0) >= 90 ? '🔥 爆火' : 
                         (rec.viralPotential ?? 0) >= 70 || (rec.opportunityScore ?? 0) >= 70 ? '⚡ 热门' : 
                         (rec.viralPotential ?? 0) >= 50 || (rec.opportunityScore ?? 0) >= 50 ? '📈 上升' : '💡 小众'}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-purple-300">内容相关性</div>
                      <div className="text-lg font-semibold text-blue-400">
                        {rec.relevanceScore?.toFixed(0)}
                      </div>
                      <div className="text-xs text-purple-400 mt-1">
                        {rec.relevanceScore >= 90 ? '完美匹配' : 
                         rec.relevanceScore >= 70 ? '高度相关' : 
                         rec.relevanceScore >= 50 ? '相关' : '不相关'}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-purple-300">预测观看</div>
                      <div className="text-lg font-semibold text-white">
                        {rec.predictedPerformance?.predicted_views.toLocaleString()}
                      </div>
                      <div
                        className={`text-xs mt-1 ${getPerformanceTierColor(
                          rec.predictedPerformance?.tier
                        )}`}
                      >
                        {rec.predictedPerformance?.tier}
                      </div>
                    </div>
                  </div>

                  {/* MVP 3.0: Prophet Prediction Info */}
                  {rec.prediction && (
                    <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-lg p-3 mb-3 border border-purple-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <Target className="w-4 h-4 text-purple-400" />
                        <span className="text-sm font-semibold text-purple-300">🔮 趋势预测</span>
                        {rec.prediction.trend_direction === 'rising' && (
                          <TrendingUp className="w-4 h-4 text-green-400" />
                        )}
                        {rec.prediction.trend_direction === 'falling' && (
                          <TrendingDown className="w-4 h-4 text-red-400" />
                        )}
                      </div>
                      <p className="text-xs text-purple-200 mb-2">{rec.prediction.summary}</p>
                      <div className="flex items-center gap-4 text-xs">
                        <span className="text-purple-300">
                          置信度: <span className="font-semibold text-purple-200">{rec.prediction.confidence?.toFixed(0) || 'N/A'}%</span>
                        </span>
                        {rec.prediction?.peak_day != null && rec.prediction.peak_day > 0 && (
                          <span className="text-yellow-300">
                            峰值: 第{rec.prediction.peak_day}天 ({rec.prediction.peak_score?.toFixed(0) || 'N/A'}分)
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* AI Reasoning */}
                  <p className="text-sm text-purple-200 mb-3 italic">💡 {rec.reasoning}</p>

                  {/* Suggested Format */}
                  <div className="text-sm text-purple-300 mb-3">
                    <Clock className="w-4 h-4 inline mr-1" />
                    推荐格式：{rec.suggestedFormat}
                  </div>

                  {/* Titles Preview */}
                  {rec.suggestedTitles && rec.suggestedTitles.length > 0 && (
                    <div className="bg-white/5 rounded-lg p-3 mt-3">
                      <div className="text-sm text-purple-300 mb-2 font-semibold">
                        ✍️ AI 生成标题（点击查看更多）:
                      </div>
                      <div className="text-white text-sm">
                        {rec.suggestedTitles[0].title}
                      </div>
                      <div className="text-purple-400 text-xs mt-1">
                        预测 CTR: {rec.suggestedTitles[0].predicted_ctr}%
                      </div>
                    </div>
                  )}
                </div>
              ))}
              </div>
            );
          })() : (
            <div className="text-center py-12">
              <TrendingDown className="w-16 h-16 text-purple-400 mx-auto mb-4 opacity-50" />
              <p className="text-purple-300">暂无推荐，请稍后重试</p>
            </div>
          )}
        </div>

        {/* 历史视频分析 Section */}
        {(data.backtest || (data.backtest_status && data.backtest_status.enabled)) ? (
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-8 border border-white/20">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2 mb-6">
              <TrendingUp className="w-6 h-6 text-green-400" />
              历史视频分析
            </h2>
            
            <p className="text-purple-300 text-sm mb-6">
              基于历史视频数据回测预测算法，评估算法准确性并分析优秀表现视频的成功因素
            </p>

            {/* Accuracy Metrics */}
            {data.backtest?.accuracy_metrics && (
              <div className="mb-8">
                <h3 className="text-lg font-bold text-white mb-4">📊 算法准确度指标</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <div className="text-purple-300 text-xs mb-1">平均绝对误差</div>
                    <div className="text-xl font-bold text-white">
                      {data.backtest?.accuracy_metrics?.mae?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                    <div className="text-purple-400 text-xs mt-1">MAE</div>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <div className="text-purple-300 text-xs mb-1">平均百分比误差</div>
                    <div className="text-xl font-bold text-white">
                      {data.backtest?.accuracy_metrics?.mape?.toFixed(1)}%
                    </div>
                    <div className="text-purple-400 text-xs mt-1">MAPE</div>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <div className="text-purple-300 text-xs mb-1">均方根误差</div>
                    <div className="text-xl font-bold text-white">
                      {data.backtest?.accuracy_metrics?.rmse?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                    <div className="text-purple-400 text-xs mt-1">RMSE</div>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <div className="text-purple-300 text-xs mb-1">R² 分数</div>
                    <div className="text-xl font-bold text-white">
                      {data.backtest?.accuracy_metrics?.r2_score?.toFixed(3)}
                    </div>
                    <div className="text-purple-400 text-xs mt-1">
                      {(data.backtest?.accuracy_metrics?.r2_score || 0) > 0.7 ? '✅ 优秀' : 
                       (data.backtest?.accuracy_metrics?.r2_score || 0) > 0.5 ? '✓ 良好' : '⚠️ 需改进'}
                    </div>
                  </div>
                  <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                    <div className="text-purple-300 text-xs mb-1">相关系数</div>
                    <div className="text-xl font-bold text-white">
                      {data.backtest?.accuracy_metrics?.correlation?.toFixed(3)}
                    </div>
                    <div className="text-purple-400 text-xs mt-1">
                      {(data.backtest?.accuracy_metrics?.correlation || 0) > 0.7 ? '✅ 强相关' : 
                       (data.backtest?.accuracy_metrics?.correlation || 0) > 0.5 ? '✓ 中等' : '⚠️ 弱相关'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Top Outliers - 优秀表现视频分析 */}
            {data.backtest?.top_outliers && (data.backtest?.top_outliers?.length || 0) > 0 ? (
              <div>
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <Award className="w-5 h-5 text-yellow-400" />
                  优秀表现视频分析（Top {data.backtest?.top_outliers?.length || 0}）
                </h3>
                <p className="text-purple-300 text-sm mb-4">
                  这些视频在发布时表现突出，播放量显著高于同期平均水平（基于同期对比，而非简单播放量排名）
                </p>
                
                <div className="space-y-4">
                  {data.backtest?.top_outliers?.map((outlier: any, idx: number) => (
                    <div
                      key={idx}
                      className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 rounded-xl p-5 border border-yellow-500/30"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="px-3 py-1 bg-yellow-500 text-white rounded-full text-sm font-bold">
                              #{idx + 1}
                            </span>
                            <h4 className="text-lg font-semibold text-white">{outlier.title}</h4>
                          </div>
                          <div className="grid grid-cols-3 gap-4 text-sm mb-2">
                            <div>
                              <span className="text-purple-300">实际播放：</span>
                              <span className="text-white font-semibold ml-2">
                                {outlier.actual_views.toLocaleString()}
                              </span>
                            </div>
                            <div>
                              <span className="text-purple-300">预测播放：</span>
                              <span className="text-white font-semibold ml-2">
                                {outlier.predicted_views.toLocaleString()}
                              </span>
                            </div>
                            <div>
                              <span className="text-purple-300">同期平均：</span>
                              <span className="text-white font-semibold ml-2">
                                {outlier.period_avg_views.toLocaleString()}
                              </span>
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-sm">
                            <div>
                              <span className="text-yellow-300 font-bold">
                                超出同期平均 {outlier.outlier_ratio.toFixed(1)} 倍
                              </span>
                            </div>
                            {outlier.published_at && (
                              <span className="text-purple-400">
                                发布时间：{new Date(outlier.published_at).toLocaleDateString('zh-CN')}
                              </span>
                            )}
                            {outlier.error_percentage && (
                              <span className="text-purple-300">
                                预测误差：{outlier.error_percentage.toFixed(1)}%
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* 成功因素分析 */}
                      {outlier.analysis && (
                        <div className="mt-4 pt-4 border-t border-yellow-500/20">
                          <h5 className="text-white font-semibold mb-3 flex items-center gap-2">
                            <Zap className="w-4 h-4 text-yellow-400" />
                            成功因素分析
                          </h5>
                          <p className="text-purple-200 text-sm mb-3 italic bg-white/5 rounded-lg p-3">
                            {outlier.analysis.summary}
                          </p>
                          {outlier.analysis.reasons && outlier.analysis.reasons.length > 0 && (
                            <div className="space-y-2">
                              {outlier.analysis.reasons.map((reason: any, rIdx: number) => (
                                <div key={rIdx} className="bg-white/5 rounded-lg p-3 border border-white/10">
                                  <div className="flex items-center justify-between mb-1">
                                    <span className="text-white font-medium">{reason.factor}</span>
                                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                                      reason.impact === '极高' ? 'bg-red-500 text-white' :
                                      reason.impact === '高' ? 'bg-orange-500 text-white' :
                                      'bg-yellow-500 text-white'
                                    }`}>
                                      {reason.impact}
                                    </span>
                                  </div>
                                  <p className="text-purple-300 text-sm">{reason.description}</p>
                                  <div className="mt-2 flex items-center gap-2">
                                    <div className="flex-1 bg-purple-900/50 rounded-full h-2">
                                      <div 
                                        className="bg-purple-400 h-2 rounded-full"
                                        style={{ width: `${Math.min(reason.score, 100)}%` }}
                                      ></div>
                                    </div>
                                    <span className="text-purple-400 text-xs">
                                      {reason.score.toFixed(0)}/100
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white/5 rounded-lg p-6 border border-white/10">
                <div className="text-center py-8">
                  <Award className="w-12 h-12 text-purple-400 mx-auto mb-4 opacity-50" />
                  <p className="text-purple-300 mb-2">暂无优秀表现视频</p>
                  <p className="text-purple-400 text-sm">
                    所有视频的表现都在正常范围内，没有明显超出同期平均水平的视频
                  </p>
                  <p className="text-purple-400 text-sm mt-2">
                    💡 提示：优秀表现视频是指播放量高于同期平均1.2倍以上的视频
                  </p>
                </div>
              </div>
            )}

            <div className="mt-6 pt-4 border-t border-white/10">
              <div className="flex items-center justify-between text-sm text-purple-300">
                <p>📊 回测了 {data.backtest?.total_videos_tested || 0} 个历史视频</p>
                <p className="text-purple-400 italic">
                  💡 基于同期对比识别优秀表现，而非简单播放量排名
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-8 border border-white/20">
            <h2 className="text-2xl font-bold text-white flex items-center gap-2 mb-6">
              <TrendingUp className="w-6 h-6 text-green-400" />
              历史视频分析
            </h2>
            <div className="bg-yellow-600/20 border border-yellow-500/30 rounded-lg p-6">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-2">暂无回测数据</h3>
                  <p className="text-purple-200 text-sm mb-4">
                    该频道的分析数据是在回测功能添加之前生成的，因此没有历史视频回测数据。
                  </p>
                  <p className="text-purple-300 text-sm mb-4">
                    要查看历史视频分析，请重新分析该频道：
                  </p>
                  <button
                    onClick={() => {
                      // 触发重新分析
                      router.push(`/?reanalyze=${channelId}`);
                    }}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all"
                  >
                    🔄 重新分析此频道
                  </button>
                  <p className="text-purple-400 text-xs mt-4">
                    💡 回测分析需要频道有至少10个视频，分析过程可能需要30-60秒
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modal for detailed recommendation */}
        {selectedRec && (() => {
          // 从 trendPredictions 中找到对应推荐关键词的完整预测数据
          const fullPrediction = (data.trendPredictions || []).find(
            (pred: any) => pred.keyword?.toLowerCase().trim() === selectedRec.keyword?.toLowerCase().trim()
          );
          
          return (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
              <div className="bg-slate-900 rounded-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto border border-white/20">
                <div className="sticky top-0 bg-slate-900 border-b border-white/10 p-6 z-10">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-2xl font-bold text-white mb-2">
                        {selectedRec.keyword}
                      </h3>
                      <p className="text-purple-300">{selectedRec.contentAngle}</p>
                    </div>
                    <button
                      onClick={() => {
                        setSelectedRec(null);
                        setActiveTab('details'); // Reset tab when closing
                      }}
                      className="text-purple-300 hover:text-white text-2xl"
                    >
                      ✕
                    </button>
                  </div>
                  
                  {/* Tab Navigation */}
                  <div className="flex gap-2 border-b border-white/10">
                    <button
                      onClick={() => setActiveTab('details')}
                      className={`px-4 py-2 font-semibold transition-all ${
                        activeTab === 'details'
                          ? 'text-white border-b-2 border-purple-400'
                          : 'text-purple-300 hover:text-white'
                      }`}
                    >
                      📋 详细信息
                    </button>
                    <button
                      onClick={() => setActiveTab('prediction')}
                      className={`px-4 py-2 font-semibold transition-all ${
                        activeTab === 'prediction'
                          ? 'text-white border-b-2 border-purple-400'
                          : 'text-purple-300 hover:text-white'
                      }`}
                      disabled={!fullPrediction}
                    >
                      🔮 7天趋势预测
                      {!fullPrediction && (
                        <span className="ml-2 text-xs text-purple-400">(暂无数据)</span>
                      )}
                    </button>
                  </div>
                </div>

                <div className="p-6">
                  {activeTab === 'details' ? (
                    <div className="space-y-6">
                {/* All Titles */}
                <div>
                  <h4 className="text-lg font-bold text-white mb-3">✍️ AI 生成标题</h4>
                  <div className="space-y-3">
                    {selectedRec.suggestedTitles?.map((title, idx) => (
                      <div key={idx} className="bg-white/5 rounded-lg p-4 border border-white/10">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="text-white font-medium mb-1">{title.title}</div>
                            <div className="text-purple-300 text-sm">{title.reasoning}</div>
                          </div>
                          <div className="ml-4 text-right">
                            <div className="text-green-400 font-bold text-lg">
                              {title.predicted_ctr}%
                            </div>
                            <div className="text-purple-300 text-xs">预测 CTR</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-purple-400 mt-2">
                          <span>策略: {title.strategy}</span>
                          <span>字符数: {title.character_count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Performance Prediction */}
                <div className="bg-white/5 rounded-lg p-4 border border-white/10">
                  <h4 className="text-lg font-bold text-white mb-3">📊 表现预测</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-purple-300 text-sm">预测级别</div>
                      <div
                        className={`text-2xl font-bold ${getPerformanceTierColor(
                          selectedRec.predictedPerformance?.tier
                        )}`}
                      >
                        {selectedRec.predictedPerformance?.tier.toUpperCase()}
                      </div>
                    </div>
                    <div>
                      <div className="text-purple-300 text-sm">预测观看数</div>
                      <div className="text-2xl font-bold text-white">
                        {selectedRec.predictedPerformance?.predicted_views.toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <p className="text-purple-200 mt-3 italic">
                    {selectedRec.predictedPerformance?.description}
                  </p>
                </div>

                {/* Related Info */}
                {selectedRec.relatedInfo && (
                  <div>
                    <h4 className="text-lg font-bold text-white mb-3">🔗 相关信息</h4>
                    
                    {selectedRec.relatedInfo.rising_queries && selectedRec.relatedInfo.rising_queries.length > 0 && (
                      <div className="mb-3">
                        <div className="text-purple-300 text-sm mb-2">上升查询：</div>
                        <div className="flex flex-wrap gap-2">
                          {selectedRec.relatedInfo.rising_queries.map((query, idx) => (
                            <span key={idx} className="px-3 py-1 bg-purple-600/30 text-purple-200 rounded text-sm">
                              {query}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedRec.relatedInfo.hashtags && selectedRec.relatedInfo.hashtags.length > 0 && (
                      <div className="mb-3">
                        <div className="text-purple-300 text-sm mb-2">相关标签：</div>
                        <div className="flex flex-wrap gap-2">
                          {selectedRec.relatedInfo.hashtags.map((tag, idx) => (
                            <span key={idx} className="px-3 py-1 bg-blue-600/30 text-blue-200 rounded text-sm">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedRec.relatedInfo.subreddits && selectedRec.relatedInfo.subreddits.length > 0 && (
                      <div>
                        <div className="text-purple-300 text-sm mb-2">热门 Subreddits：</div>
                        <div className="flex flex-wrap gap-2">
                          {selectedRec.relatedInfo.subreddits.map((sub, idx) => (
                            <span key={idx} className="px-3 py-1 bg-orange-600/30 text-orange-200 rounded text-sm">
                              r/{sub}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                    </div>
                  ) : (
                    /* Prediction Tab */
                    <div>
                      {fullPrediction ? (
                        <TrendPredictionChart
                          prediction={fullPrediction}
                          showAccuracy={true}
                        />
                      ) : (
                        <div className="bg-white/5 rounded-lg p-8 border border-white/10 text-center">
                          <TrendingUp className="w-16 h-16 text-purple-400 mx-auto mb-4 opacity-50" />
                          <p className="text-purple-300 mb-2">暂无趋势预测数据</p>
                          <p className="text-purple-400 text-sm">
                            该话题的 Prophet 预测数据暂不可用，请稍后重试或重新分析该频道
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })()}
      </div>
    </div>
  );
}
