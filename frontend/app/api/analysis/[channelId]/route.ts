import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

// Deduplicate concurrent prediction refreshes (React strict mode can double-call)
const globalForPredRefresh = globalThis as any;
const predictionRefreshLocks: Map<string, Promise<{ trendPredictions: any[]; emergingTrends: any[] }>> =
  globalForPredRefresh.__trendforge_prediction_refresh_locks ||
  (globalForPredRefresh.__trendforge_prediction_refresh_locks = new Map());

export async function GET(
  request: NextRequest,
  { params }: { params: { channelId: string } }
) {
  try {
    const { channelId } = params;

    if (!channelId) {
      return NextResponse.json(
        { error: 'Channel ID is required' },
        { status: 400 }
      );
    }

    // Get channel from database
    const channel = await prisma.channel.findUnique({
      where: { channelId },
      include: {
        trends: {
          include: {
            trend: true,
          },
          orderBy: {
            matchScore: 'desc',
          },
          take: 10,
        },
      },
    });

    if (!channel) {
      return NextResponse.json(
        { error: 'Channel not found. Please analyze the channel first.' },
        { status: 404 }
      );
    }

    // Extract analysis data from fingerprint
    const fingerprint = channel.fingerprint as any;
    const v2Analysis = fingerprint?.v2_analysis || {};
    const backtestData = v2Analysis?.backtest || null;

    // ==================== MVP 3.0: Auto-refresh predictions (confidence >= 75) ====================
    const PREDICTIONS_MIN_CONFIDENCE = 75;
    const PREDICTIONS_ALGO_VERSION = '2026-01-14-75plus';
    const backendBaseUrl = process.env.BACKEND_SERVICE_URL || 'http://localhost:8000';

    let trendPredictions = Array.isArray(v2Analysis?.trend_predictions)
      ? v2Analysis.trend_predictions
      : (v2Analysis?.trend_predictions ? [v2Analysis.trend_predictions] : []);
    let emergingTrends = Array.isArray(v2Analysis?.emerging_trends)
      ? v2Analysis.emerging_trends
      : (v2Analysis?.emerging_trends ? [v2Analysis.emerging_trends] : []);

    const storedAlgoVersion = v2Analysis?.predictions_algo_version || null;
    const storedMinConfidence = trendPredictions.length > 0
      ? Math.min(...trendPredictions.map((p: any) => Number(p?.confidence ?? 0)))
      : null;

    const shouldRefreshPredictions =
      (storedMinConfidence != null && storedMinConfidence < PREDICTIONS_MIN_CONFIDENCE) ||
      (storedAlgoVersion != null && storedAlgoVersion !== PREDICTIONS_ALGO_VERSION);

    if (shouldRefreshPredictions) {
      try {
        // unique top keywords (avoid duplicates)
        const keywords = Array.from(
          new Set(
            channel.trends
              .map((ct: { trend: { keyword: string | null } | null }) => ct.trend?.keyword)
              .filter(Boolean)
          )
        ).slice(0, 3) as string[]; // keep it fast for interactive load

        if (keywords.length > 0) {
          const lockKey = `${channel.channelId}:${PREDICTIONS_ALGO_VERSION}`;
          let refreshPromise = predictionRefreshLocks.get(lockKey);

          if (!refreshPromise) {
            refreshPromise = (async () => {
              console.log('🔄 Refreshing stored trend predictions...', {
                channelId: channel.channelId,
                storedAlgoVersion,
                targetAlgoVersion: PREDICTIONS_ALGO_VERSION,
                storedMinConfidence,
                targetMinConfidence: PREDICTIONS_MIN_CONFIDENCE,
                keywords,
              });

              const controller = new AbortController();
              const timeoutId = setTimeout(() => controller.abort(), 45000); // avoid hanging forever

              try {
                const resp = await fetch(`${backendBaseUrl}/api/v3/predict-trends`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  signal: controller.signal,
                  body: JSON.stringify({ keywords, forecast_days: 7 }),
                });

                if (!resp.ok) {
                  console.log('⚠️ Prediction refresh failed (backend response not ok)', { status: resp.status });
                  return { trendPredictions: [], emergingTrends: [] };
                }

                const predJson = await resp.json();
                if (!predJson?.success) {
                  return { trendPredictions: [], emergingTrends: [] };
                }

                const newTrendPredictions = Array.isArray(predJson.predictions) ? predJson.predictions : [];
                const newEmergingTrends = Array.isArray(predJson.emerging_trends) ? predJson.emerging_trends : [];

                // Persist refreshed predictions into fingerprint
                await prisma.channel.update({
                  where: { channelId: channel.channelId },
                  data: {
                    fingerprint: {
                      ...(fingerprint || {}),
                      v2_analysis: {
                        ...(v2Analysis || {}),
                        trend_predictions: newTrendPredictions,
                        emerging_trends: newEmergingTrends,
                        predictions_algo_version: PREDICTIONS_ALGO_VERSION,
                        predictions_enabled: true,
                      },
                    },
                  },
                });

                // Update stored recommendationData.prediction for top trends so purple cards can show peak info
                const predictionMap = new Map<string, any>(
                  newTrendPredictions.map((p: any) => [p.keyword, p])
                );

                await Promise.all(
                  channel.trends.map(async (ct: { trend: { keyword: string | null } | null }) => {
                    const kw = ct.trend?.keyword;
                    const pred = kw ? predictionMap.get(kw) : null;
                    if (!kw || !pred) return;

                    const recData = (ct.recommendationData as any) || {};
                    await prisma.channelTrend.update({
                      where: { id: ct.id },
                      data: {
                        recommendationData: {
                          ...recData,
                          prediction: {
                            trend_direction: pred.trend_direction,
                            trend_strength: pred.trend_strength,
                            confidence: pred.confidence,
                            peak_day: pred.peak_day,
                            peak_score: pred.peak_score,
                            summary: pred.summary,
                            predictions: Array.isArray(pred.predictions) ? pred.predictions.slice(0, 7) : [],
                          },
                        },
                      },
                    });
                  })
                );

                console.log('✅ Refreshed predictions saved', {
                  trendPredictionsCount: newTrendPredictions.length,
                  emergingTrendsCount: newEmergingTrends.length,
                });

                return { trendPredictions: newTrendPredictions, emergingTrends: newEmergingTrends };
              } finally {
                clearTimeout(timeoutId);
              }
            })().finally(() => {
              predictionRefreshLocks.delete(lockKey);
            });

            predictionRefreshLocks.set(lockKey, refreshPromise);
          }

          const refreshed = await refreshPromise;
          if (refreshed.trendPredictions.length > 0) {
            trendPredictions = refreshed.trendPredictions;
            emergingTrends = refreshed.emergingTrends;
          }
        }
      } catch (e) {
        console.log('⚠️ Prediction refresh error (non-fatal):', e);
      }
    }
    
    // Debug: Log backtest data availability
    console.log('📊 Backtest data check:', {
      hasFingerprint: !!fingerprint,
      hasV2Analysis: !!v2Analysis,
      hasBacktest: !!backtestData,
      backtestKeys: backtestData ? Object.keys(backtestData) : [],
      videoCount: channel.videoCount,
      lastAnalyzed: channel.lastAnalyzed
    });

    // Format recommendations from database with full details
    // 如果没有推荐数据，尝试从频道主题生成基础推荐
    let recommendations = channel.trends.map((ct: { trend: any; recommendationData: any; matchScore: number; id: string; reasoning: string | null }) => {
      const trendData = ct.trend;
      const recData = ct.recommendationData as any;
      
      // Use stored recommendation data if available, otherwise generate from trend data
      return {
        id: ct.id,
        keyword: trendData.keyword,
        matchScore: ct.matchScore,
        viralPotential: recData?.viralPotential || recData?.opportunityScore || trendData.trendScore,
        performanceScore: recData?.performanceScore || trendData.trendScore * 0.8,
        relevanceScore: recData?.relevanceScore || ct.matchScore * 0.6,
        opportunityScore: recData?.opportunityScore || trendData.growthRate || trendData.trendScore * 0.4,
        reasoning: ct.reasoning || recData?.reasoning || `基于趋势分析，${trendData.keyword} 与您的频道高度匹配`,
        contentAngle: ct.contentAngle || recData?.contentAngle || `制作关于 ${trendData.keyword} 的内容`,
        urgency: recData?.urgency || (trendData.trendScore > 80 ? 'urgent' : trendData.trendScore > 60 ? 'high' : 'medium'),
        predictedPerformance: (() => {
          // 如果有存储的预测数据，直接使用（但需要检查是否是旧数据）
          if (recData?.predictedPerformance) {
            const stored = recData.predictedPerformance;
            // 如果预测观看数是固定的12000或8000，说明是旧数据，需要重新计算
            if (stored.predicted_views === 12000 || stored.predicted_views === 8000) {
              // 继续使用动态算法重新计算
            } else {
              // 新数据，直接使用
              return stored;
            }
          }
          
          // 使用新的动态算法计算
          // 获取频道平均播放量（从 fingerprint 中）
          const fingerprint = channel.fingerprint as any;
          const v2Analysis = fingerprint?.v2_analysis || {};
          const highPerformers = v2Analysis.high_performers || {};
          // 优先使用 avg_views，如果没有则尝试从 fingerprint 中获取
          let avgViews = highPerformers.avg_views || highPerformers.median_views;
          if (!avgViews) {
            // 尝试从旧的 fingerprint 中获取
            avgViews = (fingerprint?.avgViews as number) || 10000;
          }
          
          // 使用新的多因素动态计算
          const viralPotential = recData?.viralPotential || recData?.opportunityScore || trendData.trendScore || 50;
          const relevanceScore = recData?.relevanceScore || ct.matchScore * 0.6 || 50;
          const performanceScore = recData?.performanceScore || trendData.trendScore * 0.8 || 50;
          const matchScore = ct.matchScore || trendData.trendScore || 50;
          
          // 热度增长系数
          let viralMultiplier = 1.0;
          if (viralPotential >= 90) viralMultiplier = 2.5;
          else if (viralPotential >= 70) viralMultiplier = 2.0;
          else if (viralPotential >= 50) viralMultiplier = 1.5;
          
          // 相关性调整
          const relevanceMultiplier = 0.7 + (relevanceScore / 100) * 0.6;
          
          // 表现潜力系数
          const performanceMultiplier = 0.8 + (performanceScore / 100) * 0.7;
          
          // 时效性加成
          const timelinessMultiplier = 0.9 + (matchScore / 100) * 0.3;
          
          // 随机波动（使用固定的种子确保一致性）
          const randomSeed = ct.id.charCodeAt(0) % 40; // 0-39
          const randomFactor = 0.8 + (randomSeed / 100); // 0.8-1.2
          
          // 综合计算
          const predictedViews = Math.max(1000, Math.round(
            avgViews * viralMultiplier * relevanceMultiplier * performanceMultiplier * timelinessMultiplier * randomFactor
          ));
          
          // Performance tiers
          let tier = 'moderate';
          let description = '预计表现中等，稳定流量';
          if (matchScore >= 80) {
            tier = 'excellent';
            description = '预计表现优异，可能成为爆款';
          } else if (matchScore >= 60) {
            tier = 'good';
            description = '预计表现良好，高于平均水平';
          } else if (matchScore < 40) {
            tier = 'low';
            description = '预计表现一般，可作为尝试';
          }
          
          return {
            tier,
            predicted_views: predictedViews,
            description,
            confidence: Math.round(matchScore),
          };
        })(),
        suggestedFormat: recData?.suggestedFormat || trendData.category || '8-12分钟综合内容',
        suggestedTitles: recData?.suggestedTitles || [
          {
            title: `${trendData.keyword} 完整指南：从入门到精通`,
            strategy: 'guide',
            predicted_ctr: 8.5,
            reasoning: '指南式标题通常有较高点击率',
            character_count: trendData.keyword.length + 12,
          },
          {
            title: `你真的了解${trendData.keyword}吗？`,
            strategy: 'question',
            predicted_ctr: 7.2,
            reasoning: '问题式标题，激发好奇心',
            character_count: trendData.keyword.length + 8,
          },
          {
            title: `${trendData.keyword}：99%的人都不知道的秘密`,
            strategy: 'emotional',
            predicted_ctr: 9.1,
            reasoning: '情感化标题，易引发共鸣和分享',
            character_count: trendData.keyword.length + 15,
          },
        ],
        sources: recData?.sources || ['database'],
          relatedInfo: recData?.relatedInfo || {
            rising_queries: trendData.relatedKeywords || [],
            hashtags: [],
            subreddits: [],
          },
          // MVP 3.0: Add prediction data if available
          prediction: recData?.prediction || null,
        };
      });

    // 如果没有推荐数据，从频道主题生成基础推荐
    if (recommendations.length === 0 && v2Analysis.topics && v2Analysis.topics.length > 0) {
      console.log('⚠️ No recommendations found, generating from channel topics...');
      const topics = v2Analysis.topics.slice(0, 10);
      const highPerformers = v2Analysis.high_performers || {};
      const avgViews = highPerformers.avg_views || highPerformers.median_views || (channel.fingerprint as any)?.avgViews || 10000;
      
      recommendations = topics.map((topic: any, idx: number) => {
        const topicName = topic.topic || topic;
        const score = topic.score || 0.5;
        const matchScore = Math.round(score * 100);
        
        return {
          id: `generated-${idx}`,
          keyword: topicName,
          matchScore,
          viralPotential: 50 + (score * 40), // 50-90
          performanceScore: 60 + (score * 30), // 60-90
          relevanceScore: Math.round(score * 100), // 基于主题分数
          opportunityScore: 50 + (score * 30),
          reasoning: `基于频道内容分析，'${topicName}' 是该频道的核心主题之一，与频道风格高度匹配`,
          contentAngle: `深入探讨 ${topicName} 的相关内容，结合频道特色`,
          urgency: matchScore >= 80 ? 'urgent' : matchScore >= 60 ? 'high' : 'medium',
          predictedPerformance: {
            tier: matchScore >= 80 ? 'excellent' : matchScore >= 60 ? 'good' : 'moderate',
            predicted_views: Math.round(avgViews * (0.8 + score * 0.4)),
            description: matchScore >= 80 ? '预计表现优异，可能成为爆款' : matchScore >= 60 ? '预计表现良好，高于平均水平' : '预计表现中等，稳定流量',
            confidence: matchScore,
          },
          suggestedFormat: v2Analysis.content_style?.format || '8-12分钟综合内容',
          suggestedTitles: [
            {
              title: `${topicName} 完整指南：从入门到精通`,
              strategy: 'guide',
              predicted_ctr: 8.5,
              reasoning: '指南式标题通常有较高点击率',
              character_count: topicName.length + 12,
            },
            {
              title: `你真的了解${topicName}吗？`,
              strategy: 'question',
              predicted_ctr: 7.2,
              reasoning: '问题式标题，激发好奇心',
              character_count: topicName.length + 8,
            },
            {
              title: `${topicName}：99%的人都不知道的秘密`,
              strategy: 'emotional',
              predicted_ctr: 9.1,
              reasoning: '情感化标题，易引发共鸣和分享',
              character_count: topicName.length + 15,
            },
          ],
          sources: ['channel_analysis'],
          relatedInfo: {
            rising_queries: [],
            hashtags: [],
            subreddits: [],
          },
        };
      });
    }

    return NextResponse.json({
      success: true,
      channelId: channel.channelId,
      channel: {
        title: channel.title,
        subscriberCount: channel.subscriberCount,
        thumbnailUrl: channel.thumbnailUrl,
        description: channel.description,
      },
      analysis: {
        topics: v2Analysis.topics?.slice(0, 15) || channel.nicheKeywords.slice(0, 15).map((k: string) => ({ topic: k, score: 0.5 })),
        contentStyle: v2Analysis.content_style || { primary_style: 'general' },
        targetAudience: (() => {
          // Use v2_analysis data if available, otherwise use defaults
          const ta = v2Analysis.target_audience;
          if (ta && ta.primary_age_group && ta.primary_age_group !== 'all_ages' && ta.primary_age_group !== 'general') {
            // Has new format data
            return ta;
          }
          // Return defaults with new format
          return {
            primary_age_group: '18-24岁 (大学生/年轻人)',
            engagement_level: '中等 (正常水平)',
            audience_size_tier: channel.subscriberCount > 100000 ? '大型频道 (10万+)' : 
                               channel.subscriberCount > 10000 ? '中型频道 (1万-10万)' : 
                               channel.subscriberCount > 1000 ? '小型频道 (1千-1万)' : '新频道 (<1千)',
            purchasing_power: '中等消费',
          };
        })(),
        highPerformers: v2Analysis.high_performers || {},
        videosAnalyzed: v2Analysis.total_videos_analyzed || 0,
      },
      recommendations,
      summary: {
        total_recommendations: recommendations.length,
        urgent_count: recommendations.filter((r) => r.urgency === 'urgent').length,
        high_match_count: recommendations.filter((r) => r.matchScore > 75).length,
        avg_match_score: recommendations.length > 0 
          ? recommendations.reduce((sum, r) => sum + r.matchScore, 0) / recommendations.length 
          : 0,
      },
      backtest: backtestData, // 从fingerprint中获取回测结果
      backtest_status: v2Analysis?.backtest_status || {
        enabled: true,
        video_count: channel.videoCount,
        meets_requirements: channel.videoCount >= 10,
        status: backtestData ? "success" : (channel.videoCount < 10 ? "insufficient_videos" : "not_run")
      }, // 回测状态信息
      trendPredictions, // MVP 3.0: Prophet 趋势预测数据（可能已自动刷新）
      emergingTrends, // MVP 3.0: 新兴趋势数据（可能已自动刷新）
      predictionsEnabled: v2Analysis?.predictions_enabled || shouldRefreshPredictions || false, // MVP 3.0: 预测功能状态
    });
  } catch (error: any) {
    console.error('Error fetching analysis:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to fetch analysis' },
      { status: 500 }
    );
  }
}
