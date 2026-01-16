// frontend/lib/youtube-public.ts
import { google } from 'googleapis'

const youtube = google.youtube({
  version: 'v3',
  auth: process.env.YOUTUBE_API_KEY,
})

interface VideoData {
  videoId: string
  title: string
  description: string
  publishedAt: Date
  viewCount: number
  likeCount: number
  commentCount: number
  thumbnailUrl: string
  duration: string
  tags: string[]
}

interface ChannelFingerprint {
  avgViews: number
  avgLikes: number
  avgComments: number
  uploadFrequency: string
  topPerformers: string[]
  contentCategories: Record<string, number>
}

export async function analyzePublicChannel(channelIdentifier: string) {
  try {
    // 1. 获取频道 ID
    let channelId = channelIdentifier

    // 如果是用户名或自定义 URL，先查找频道 ID
    if (!channelIdentifier.startsWith('UC') || channelIdentifier.startsWith('@')) {
      const searchResponse = await youtube.search.list({
        part: ['snippet'],
        q: channelIdentifier,
        type: ['channel'],
        maxResults: 1,
      })

      if (!searchResponse.data.items || searchResponse.data.items.length === 0) {
        throw new Error('Channel not found')
      }

      channelId = searchResponse.data.items[0].snippet?.channelId || channelIdentifier
    }

    // 2. 获取频道详情
    const channelResponse = await youtube.channels.list({
      part: ['snippet', 'statistics', 'brandingSettings'],
      id: [channelId],
    })

    if (!channelResponse.data.items || channelResponse.data.items.length === 0) {
      throw new Error('Channel not found')
    }

    const channel = channelResponse.data.items[0]
    const snippet = channel.snippet!
    const statistics = channel.statistics!

    // 3. 获取最近的视频列表（最多 50 个）
    const videosResponse = await youtube.search.list({
      part: ['snippet'],
      channelId,
      order: 'date',
      type: ['video'],
      maxResults: 50,
    })

    const videoIds = videosResponse.data.items
      ?.map((item) => item.id?.videoId)
      .filter(Boolean) as string[]

    // 4. 获取视频详细信息
    const videoDetailsResponse = await youtube.videos.list({
      part: ['snippet', 'statistics', 'contentDetails'],
      id: videoIds,
    })

    const videos: VideoData[] =
      videoDetailsResponse.data.items?.map((video) => ({
        videoId: video.id!,
        title: video.snippet?.title || '',
        description: video.snippet?.description || '',
        publishedAt: new Date(video.snippet?.publishedAt || ''),
        viewCount: parseInt(video.statistics?.viewCount || '0'),
        likeCount: parseInt(video.statistics?.likeCount || '0'),
        commentCount: parseInt(video.statistics?.commentCount || '0'),
        thumbnailUrl: video.snippet?.thumbnails?.high?.url || '',
        duration: video.contentDetails?.duration || '',
        tags: video.snippet?.tags || [],
      })) || []

    // 5. 生成频道指纹
    const fingerprint: ChannelFingerprint = {
      avgViews: videos.reduce((sum, v) => sum + v.viewCount, 0) / videos.length,
      avgLikes: videos.reduce((sum, v) => sum + v.likeCount, 0) / videos.length,
      avgComments: videos.reduce((sum, v) => sum + v.commentCount, 0) / videos.length,
      uploadFrequency: calculateUploadFrequency(videos),
      topPerformers: videos
        .sort((a, b) => b.viewCount - a.viewCount)
        .slice(0, 5)
        .map((v) => v.videoId),
      contentCategories: {},
    }

    return {
      channelId,
      title: snippet.title || '',
      description: snippet.description || '',
      customUrl: snippet.customUrl || '',
      thumbnailUrl: snippet.thumbnails?.high?.url || '',
      subscriberCount: parseInt(statistics.subscriberCount || '0'),
      videoCount: parseInt(statistics.videoCount || '0'),
      viewCount: parseInt(statistics.viewCount || '0'),
      videos,
      fingerprint,
    }
  } catch (error: any) {
    console.error('YouTube API Error:', error)
    throw new Error(`Failed to analyze channel: ${error.message}`)
  }
}

function calculateUploadFrequency(videos: VideoData[]): string {
  if (videos.length < 2) return 'irregular'

  const dates = videos.map((v) => v.publishedAt.getTime()).sort((a, b) => b - a)
  const intervals: number[] = []

  for (let i = 0; i < dates.length - 1; i++) {
    intervals.push(dates[i] - dates[i + 1])
  }

  const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length
  const days = avgInterval / (1000 * 60 * 60 * 24)

  if (days < 1) return 'multiple_per_day'
  if (days < 2) return 'daily'
  if (days < 4) return 'every_2_3_days'
  if (days < 8) return 'weekly'
  if (days < 15) return 'biweekly'
  if (days < 32) return 'monthly'
  return 'irregular'
}
