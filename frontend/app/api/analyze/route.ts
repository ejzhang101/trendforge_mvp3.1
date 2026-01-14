import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { analyzePublicChannel } from '@/lib/youtube-public';

export async function POST(request: NextRequest) {
  try {
    const { channelIdentifier } = await request.json();

    if (!channelIdentifier) {
      return NextResponse.json(
        { error: 'Channel identifier is required' },
        { status: 400 }
      );
    }

    console.log('🔍 Starting MVP 2.0 analysis for:', channelIdentifier);

    // Step 0: Quick cache check - 先尝试通过 channelId 或 customUrl 查找缓存
    let cachedChannel = null;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // 如果是 channelId 格式，直接查询
    if (channelIdentifier.startsWith('UC') && channelIdentifier.length === 24) {
      cachedChannel = await prisma.channel.findUnique({
        where: { channelId: channelIdentifier },
        include: {
          trends: {
            include: { trend: true },
            take: 10,
            orderBy: { matchScore: 'desc' }
          }
        }
      });
    } else {
      // 尝试通过 customUrl 查找
      const cleanUrl = channelIdentifier.replace('@', '').replace('https://www.youtube.com/', '').replace('c/', '').replace('channel/', '');
      cachedChannel = await prisma.channel.findFirst({
        where: {
          OR: [
            { customUrl: { contains: cleanUrl } },
            { title: { contains: cleanUrl } }
          ]
        },
        include: {
          trends: {
            include: { trend: true },
            take: 10,
            orderBy: { matchScore: 'desc' }
          }
        }
      });
    }

    // 如果找到缓存且是今天分析的，直接返回缓存结果
    if (cachedChannel && cachedChannel.lastAnalyzed) {
      const lastAnalyzed = new Date(cachedChannel.lastAnalyzed);
      lastAnalyzed.setHours(0, 0, 0, 0);
      
      if (lastAnalyzed.getTime() === today.getTime()) {
        console.log('✅ Using cached analysis from today (avoiding API calls)');
        
        const cachedAnalysis = (cachedChannel.fingerprint as any)?.v2_analysis || {};
        
        return NextResponse.json({
          success: true,
          cached: true,
          channelId: cachedChannel.channelId,
          channel: {
            title: cachedChannel.title,
            subscriberCount: cachedChannel.subscriberCount,
            thumbnailUrl: cachedChannel.thumbnailUrl,
            description: cachedChannel.description,
          },
          analysis: {
            topics: cachedAnalysis.topics || [],
            contentStyle: cachedAnalysis.content_style || {},
            targetAudience: cachedAnalysis.target_audience || {},
            highPerformers: cachedAnalysis.high_performers || {},
            videosAnalyzed: cachedAnalysis.total_videos_analyzed || 0,
          },
          socialTrends: cachedAnalysis.social_trends || {},
          recommendations: cachedChannel.trends.map(ct => ({
            id: ct.id,
            keyword: ct.trend.keyword,
            matchScore: ct.matchScore,
            ...(ct.recommendationData as any || {})
          })),
          summary: {
            total_recommendations: cachedChannel.trends.length,
          },
          backtest: cachedAnalysis.backtest || null,
          lastAnalyzed: cachedChannel.lastAnalyzed,
        });
      } else {
        console.log('ℹ️ Found cached data but from previous day, will refresh');
      }
    }

    // Step 1: Analyze the channel using YouTube API (only if not cached today)
    const analysis = await analyzePublicChannel(channelIdentifier);

    if (!analysis) {
      return NextResponse.json(
        { error: 'Channel not found or analysis failed' },
        { status: 404 }
      );
    }

    console.log('✅ Channel data collected:', analysis.channelId);

    // Step 2: Call enhanced backend for full analysis
    const backendUrl = process.env.BACKEND_SERVICE_URL || 'http://localhost:8000';
    
    console.log('🌐 Calling enhanced backend...');
    
    // Create AbortController for timeout handling (4 minutes - increased for social API delays)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 240000); // 4 minutes
    
    let backendResponse;
    try {
      backendResponse = await fetch(`${backendUrl}/api/v2/full-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          videos: analysis.videos.map(v => ({
            videoId: v.videoId,
            title: v.title,
            description: v.description,
            publishedAt: v.publishedAt.toISOString(),
            viewCount: v.viewCount,
            likeCount: v.likeCount,
            commentCount: v.commentCount,
          })),
          channel_data: {
            channelId: analysis.channelId,
            title: analysis.title,
            subscriberCount: analysis.subscriberCount,
            videoCount: analysis.videoCount,
            viewCount: analysis.viewCount,
          },
          geo: 'US',
          analyze_transcripts: false, // Set to true for deeper analysis (slower)
          max_recommendations: 10, // 恢复推荐数量
          enable_backtest: true, // 启用回测分析 (MVP 2.0)
          enable_predictions: true, // MVP 3.0: 启用 Prophet 预测
          use_simple_mode: false, // 标准模式：包含社交媒体收集（但会快速失败）
        }),
      });
      
      clearTimeout(timeoutId);
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        console.error('Backend request timeout after 4 minutes');
        throw new Error('分析超时（超过4分钟）。可能是社交API限流或处理时间过长，请稍后重试。');
      }
      throw new Error(`后端连接失败: ${fetchError.message}`);
    }

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error('Backend error:', errorText);
      throw new Error(`后端分析失败: ${errorText}`);
    }

    const backendData = await backendResponse.json();
    console.log('✅ Backend analysis complete');
    console.log('📊 Backend response includes backtest:', {
      hasBacktest: !!backendData.backtest,
      backtestKeys: backendData.backtest ? Object.keys(backendData.backtest) : [],
      videoCount: analysis.videos.length,
      enableBacktest: true
    });

    // Step 3: Save to database
    console.log('💾 Saving to database...');
    
    // Get or create public user
    const publicUser = await prisma.user.upsert({
      where: { email: 'public@trendforge.app' },
      create: {
        email: 'public@trendforge.app',
        name: 'Public User',
      },
      update: {},
    });
    
    // Save/update channel
    const channel = await prisma.channel.upsert({
      where: { channelId: analysis.channelId },
      create: {
        channelId: analysis.channelId,
        userId: publicUser.id,
        title: analysis.title,
        description: analysis.description,
        customUrl: analysis.customUrl,
        thumbnailUrl: analysis.thumbnailUrl,
        subscriberCount: analysis.subscriberCount,
        videoCount: analysis.videoCount,
        viewCount: BigInt(analysis.viewCount),
        fingerprint: {
          ...analysis.fingerprint,
          v2_analysis: {
            ...backendData.channel_analysis,
            backtest: backendData.backtest || null, // 保存回测结果 (MVP 2.0)
            backtest_status: backendData.backtest_status || null, // 保存回测状态
            social_trends: backendData.social_trends || {}, // 保存社交媒体趋势
            trend_predictions: Array.isArray(backendData.trend_predictions) ? backendData.trend_predictions : [], // MVP 3.0: Prophet 趋势预测 (确保是数组)
            emerging_trends: Array.isArray(backendData.emerging_trends) ? backendData.emerging_trends : [], // MVP 3.0: 新兴趋势 (确保是数组)
          },
        },
        nicheKeywords: backendData.channel_analysis.topics
          .slice(0, 15)
          .map((t: any) => t.topic),
      },
      update: {
        title: analysis.title,
        description: analysis.description,
        customUrl: analysis.customUrl,
        thumbnailUrl: analysis.thumbnailUrl, // 确保更新头像URL
        subscriberCount: analysis.subscriberCount,
        videoCount: analysis.videoCount,
        viewCount: BigInt(analysis.viewCount),
        fingerprint: {
          ...analysis.fingerprint,
          v2_analysis: {
            ...backendData.channel_analysis,
            backtest: backendData.backtest || null, // 保存回测结果 (MVP 2.0)
            backtest_status: backendData.backtest_status || null, // 保存回测状态
            social_trends: backendData.social_trends || {}, // 保存社交媒体趋势
            trend_predictions: Array.isArray(backendData.trend_predictions) ? backendData.trend_predictions : [], // MVP 3.0: Prophet 趋势预测 (确保是数组)
            emerging_trends: Array.isArray(backendData.emerging_trends) ? backendData.emerging_trends : [], // MVP 3.0: 新兴趋势 (确保是数组)
          },
        },
        nicheKeywords: backendData.channel_analysis.topics
          .slice(0, 15)
          .map((t: any) => t.topic),
        lastAnalyzed: new Date(),
      },
    });

    // Save recommendations as trends with full details
    // 确保有推荐数据，如果没有则从频道主题生成
    let recommendationsToSave = backendData.recommendations || [];
    if (recommendationsToSave.length === 0 && backendData.channel_analysis?.topics) {
      console.log('⚠️ No recommendations from backend, generating from topics...');
      const topics = backendData.channel_analysis.topics.slice(0, 10);
      recommendationsToSave = topics.map((topic: any, idx: number) => ({
        keyword: topic.topic || topic,
        match_score: (topic.score || 0.5) * 100,
        viral_potential: 50 + (topic.score || 0.5) * 40,
        performance_score: 60 + (topic.score || 0.5) * 30,
        relevance_score: (topic.score || 0.5) * 100,
        opportunity_score: 50 + (topic.score || 0.5) * 30,
        reasoning: `基于频道内容分析，'${topic.topic || topic}' 是该频道的核心主题之一`,
        content_angle: `深入探讨 ${topic.topic || topic} 的相关内容`,
        urgency: (topic.score || 0.5) >= 0.8 ? 'urgent' : (topic.score || 0.5) >= 0.6 ? 'high' : 'medium',
        predicted_performance: {
          tier: (topic.score || 0.5) >= 0.8 ? 'excellent' : (topic.score || 0.5) >= 0.6 ? 'good' : 'moderate',
          predicted_views: backendData.channel_analysis.high_performers?.avg_views || 10000,
          description: '基于频道主题的推荐',
          confidence: Math.round((topic.score || 0.5) * 100),
        },
        suggested_format: backendData.channel_analysis.content_style?.format || '8-12分钟综合内容',
        suggested_titles: [],
        sources: ['channel_analysis'],
        related_info: {},
      }));
    }
    
    const savedRecommendations = await Promise.all(
      recommendationsToSave.slice(0, 10).map(async (rec: any) => {
        // Create trend snapshot
        const trendSnapshot = await prisma.trendSnapshot.create({
          data: {
            keyword: rec.keyword,
            searchVolume: 0, // Placeholder
            growthRate: rec.composite_social_score || rec.opportunity_score || 0,
            competition: 0,
            trendScore: rec.match_score,
            geo: 'US',
            category: rec.suggested_format || 'general',
            relatedKeywords: rec.related_info?.rising_queries || [],
          },
        });

        // Create channel-trend relationship with full recommendation data stored as JSON
        const channelTrend = await prisma.channelTrend.create({
          data: {
            channelId: analysis.channelId,
            trendId: trendSnapshot.id,
            matchScore: rec.match_score,
            reasoning: rec.reasoning,
            contentAngle: rec.content_angle,
            recommendationData: {
              viralPotential: rec.viral_potential,
              performanceScore: rec.performance_score,
              relevanceScore: rec.relevance_score,
              opportunityScore: rec.opportunity_score,
              urgency: rec.urgency,
              predictedPerformance: rec.predicted_performance,
              suggestedFormat: rec.suggested_format,
              suggestedTitles: rec.suggested_titles,
              sources: rec.sources,
              relatedInfo: rec.related_info,
              // MVP 3.0: Save prediction data if available
              prediction: rec.prediction || null,
            },
          },
        });

        return {
          id: channelTrend.id,
          keyword: rec.keyword,
          matchScore: rec.match_score,
          viralPotential: rec.viral_potential,
          performanceScore: rec.performance_score,
          relevanceScore: rec.relevance_score,
          opportunityScore: rec.opportunity_score,
          reasoning: rec.reasoning,
          contentAngle: rec.content_angle,
          urgency: rec.urgency,
          predictedPerformance: rec.predicted_performance,
          suggestedFormat: rec.suggested_format,
          suggestedTitles: rec.suggested_titles,
          sources: rec.sources,
          relatedInfo: rec.related_info,
          // MVP 3.0: Include prediction data
          prediction: rec.prediction || null,
        };
      })
    );

    console.log('✅ Data saved successfully');

    return NextResponse.json({
      success: true,
      channelId: analysis.channelId,
      channel: {
        title: analysis.title,
        subscriberCount: analysis.subscriberCount,
        thumbnailUrl: analysis.thumbnailUrl,
        description: analysis.description,
      },
      analysis: {
        topics: backendData.channel_analysis.topics,
        contentStyle: backendData.channel_analysis.content_style,
        targetAudience: backendData.channel_analysis.target_audience,
        highPerformers: backendData.channel_analysis.high_performers,
        videosAnalyzed: backendData.channel_analysis.total_videos_analyzed,
      },
      socialTrends: backendData.social_trends,
      recommendations: savedRecommendations,
      summary: backendData.summary,
      backtest: backendData.backtest || null, // 回测结果（已保存到fingerprint中）
      backtest_status: backendData.backtest_status || null, // 回测状态信息
      trendPredictions: backendData.trend_predictions || [], // MVP 3.0: Prophet 趋势预测 (确保是数组)
      emergingTrends: backendData.emerging_trends || [], // MVP 3.0: 新兴趋势 (确保是数组)
      predictionsEnabled: backendData.performance?.predictions_enabled || false, // MVP 3.0: 预测功能状态
    });
  } catch (error: any) {
    console.error('Analysis error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to analyze channel' },
      { status: 500 }
    );
  }
}
