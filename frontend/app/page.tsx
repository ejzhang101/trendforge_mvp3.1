'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Sparkles, TrendingUp, Zap } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [channelIdentifier, setChannelIdentifier] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // 检查URL参数中是否有reanalyze
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const reanalyze = params.get('reanalyze');
    if (reanalyze) {
      setChannelIdentifier(reanalyze);
      // 自动触发分析
      setTimeout(() => {
        const form = document.querySelector('form');
        if (form) {
          form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
      }, 500);
    }
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!channelIdentifier.trim()) {
      setError('请输入频道标识符');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Call analyze API
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channelIdentifier: channelIdentifier.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || '分析失败');
      }

      // Redirect to analysis page
      router.push(`/analysis/${data.channelId}`);
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(err.message || '分析失败，请稍后重试');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Sparkles className="w-12 h-12 text-yellow-400" />
            <h1 className="text-5xl font-bold text-white">TrendForge</h1>
          </div>
          <p className="text-xl text-purple-200 mb-2">
            AI 驱动的 YouTube 趋势预测平台
          </p>
          <p className="text-purple-300">
            深度内容分析 · 社交媒体趋势 · 智能推荐
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <TrendingUp className="w-8 h-8 text-purple-400 mb-2" />
            <h3 className="text-white font-semibold mb-1">趋势分析</h3>
            <p className="text-purple-200 text-sm">
              多平台社交媒体趋势收集
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <Zap className="w-8 h-8 text-yellow-400 mb-2" />
            <h3 className="text-white font-semibold mb-1">智能推荐</h3>
            <p className="text-purple-200 text-sm">
              AI 生成个性化内容建议
            </p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <Sparkles className="w-8 h-8 text-pink-400 mb-2" />
            <h3 className="text-white font-semibold mb-1">标题优化</h3>
            <p className="text-purple-200 text-sm">
              自动生成高 CTR 标题
            </p>
          </div>
        </div>

        {/* Search Form */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <label htmlFor="channel" className="block text-white font-semibold mb-2">
                输入 YouTube 频道
              </label>
              <div className="flex gap-2">
                <input
                  id="channel"
                  type="text"
                  value={channelIdentifier}
                  onChange={(e) => setChannelIdentifier(e.target.value)}
                  placeholder="频道 ID、用户名或自定义 URL (例如: UCxxxxxxxxxxxxx 或 @username)"
                  className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      分析中...
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5" />
                      开始分析
                    </>
                  )}
                </button>
              </div>
              {error && (
                <p className="mt-2 text-red-400 text-sm">{error}</p>
              )}
            </div>
          </form>

          <div className="mt-6 pt-6 border-t border-white/10">
            <p className="text-purple-300 text-sm mb-2">支持的格式：</p>
            <ul className="text-purple-200 text-sm space-y-1">
              <li>• 频道 ID: <code className="bg-white/10 px-2 py-1 rounded">UCxxxxxxxxxxxxx</code></li>
              <li>• 用户名: <code className="bg-white/10 px-2 py-1 rounded">@username</code></li>
              <li>• 自定义 URL: <code className="bg-white/10 px-2 py-1 rounded">c/username</code></li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-purple-300 text-sm">
          <p>Powered by AI and love in TRT - MVP3.0</p>
        </div>
      </div>
    </div>
  );
}
