import React, { useState } from 'react';
import { 
  Sparkles, Send, FileText, TrendingUp, Target, 
  Clock, Eye, ThumbsUp, MessageCircle, Share2,
  CheckCircle, AlertCircle, Lightbulb, Zap
} from 'lucide-react';

interface ScriptGeneratorProps {
  channelAnalysis: any;
  recommendations: any[];
}

export default function ScriptGenerator({ channelAnalysis, recommendations }: ScriptGeneratorProps) {
  const [userPrompt, setUserPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [scripts, setScripts] = useState<any[]>([]);
  const [selectedScript, setSelectedScript] = useState<any>(null);

  const handleGenerate = async () => {
    if (!userPrompt.trim()) {
      alert('请输入产品/服务描述');
      return;
    }

    setIsGenerating(true);

    try {
      // 调用后端API（通过前端API路由代理）
      let backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_SERVICE_URL || 'http://localhost:8000';
      
      // Ensure URL has protocol (fix for Railway URLs without https://)
      if (backendBaseUrl && !backendBaseUrl.startsWith('http://') && !backendBaseUrl.startsWith('https://')) {
        backendBaseUrl = `https://${backendBaseUrl}`;
      }
      
      const response = await fetch(`${backendBaseUrl}/api/v3/generate-scripts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_prompt: userPrompt,
          channel_analysis: {
            topics: channelAnalysis.topics || [],
            content_style: channelAnalysis.contentStyle || channelAnalysis.content_style || {},
            target_audience: channelAnalysis.targetAudience || channelAnalysis.target_audience || {},
            high_performers: channelAnalysis.highPerformers || channelAnalysis.high_performers || {},
            total_videos_analyzed: channelAnalysis.videosAnalyzed || channelAnalysis.total_videos_analyzed || 0
          },
          recommendations: recommendations.map((rec: any) => ({
            keyword: rec.keyword,
            match_score: rec.matchScore || rec.match_score || 70,
            viral_potential: rec.viralPotential || rec.viral_potential || 50,
            performance_score: rec.performanceScore || rec.performance_score || 65,
            relevance_score: rec.relevanceScore || rec.relevance_score || 75,
            opportunity_score: rec.opportunityScore || rec.opportunity_score || 60,
            content_angle: rec.contentAngle || rec.content_angle || '',
            suggested_format: rec.suggestedFormat || rec.suggested_format || '8-12分钟综合内容',
            urgency: rec.urgency || 'medium'
          })),
          count: 3
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API 错误:', response.status, errorText);
        throw new Error(`生成失败 (${response.status}): ${errorText || '未知错误'}`);
      }

      const data = await response.json();
      
      if (data.success) {
        setScripts(data.scripts);
        if (data.scripts.length > 0) {
          setSelectedScript(data.scripts[0]); // 默认选择第一个
        }
      } else {
        throw new Error(data.error || data.detail || '生成失败，请重试');
      }
    } catch (error: any) {
      console.error('生成脚本失败:', error);
      const errorMessage = error.message || '生成失败，请检查网络连接或后端服务是否正常运行';
      alert(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const getPerformanceTierInfo = (tier: string) => {
    const tiers = {
      excellent: { text: '优秀', color: 'text-green-400', bg: 'bg-green-500/20' },
      good: { text: '良好', color: 'text-blue-400', bg: 'bg-blue-500/20' },
      moderate: { text: '中等', color: 'text-yellow-400', bg: 'bg-yellow-500/20' },
      average: { text: '一般', color: 'text-gray-400', bg: 'bg-gray-500/20' }
    };
    return tiers[tier as keyof typeof tiers] || tiers.average;
  };

  const formatNumber = (num: number) => {
    if (num >= 10000) {
      return `${(num / 10000).toFixed(1)}万`;
    }
    return num.toLocaleString();
  };

  if (scripts.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        {/* 简洁对话框 */}
        <div className="w-full max-w-2xl">
          <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 border border-slate-700/50 shadow-2xl">
            {/* 标题区 - 简洁 */}
            <div className="mb-6">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Sparkles className="w-5 h-5 text-blue-400" />
                </div>
                <h2 className="text-2xl font-bold text-white">AI 智能脚本生成</h2>
              </div>
              <p className="text-slate-400 text-sm ml-12">
                输入产品描述，生成高转化视频脚本
              </p>
            </div>

            {/* 输入区 - 紧凑 */}
            <div className="space-y-4">
              <div>
                <label className="block text-slate-300 text-sm mb-2">
                  产品/服务描述
                </label>
                <textarea
                  value={userPrompt}
                  onChange={(e) => setUserPrompt(e.target.value)}
                  placeholder="例如：我们是B端电商企业，主要向企业客户销售电子产品（如办公设备、智能硬件），目标客户是中小企业的采购部门，产品优势是批量采购优惠、企业级服务支持、快速交付"
                  className="w-full h-24 bg-slate-900/50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 text-sm resize-none focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20 transition-all"
                  disabled={isGenerating}
                />
                <p className="text-slate-500 text-xs mt-1.5">
                  描述越详细，生成的脚本越精准
                </p>
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating || !userPrompt.trim()}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 disabled:from-slate-700 disabled:to-slate-700 text-white font-medium rounded-lg transition-all disabled:cursor-not-allowed text-sm"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    生成脚本
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 简洁头部 */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-700/50">
        <div>
          <h3 className="text-lg font-semibold text-white">已生成 {scripts.length} 个脚本方案</h3>
          <p className="text-slate-400 text-xs mt-0.5 truncate max-w-md">{userPrompt}</p>
        </div>
        <button
          onClick={() => {
            setScripts([]);
            setSelectedScript(null);
          }}
          className="px-3 py-1.5 text-sm bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-lg transition-all"
        >
          重新生成
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        {/* 脚本列表 - 简洁卡片 */}
        <div className="space-y-3">
          {scripts.map((script, index) => {
            const tierInfo = getPerformanceTierInfo(script.predicted_performance.expected_performance_tier);
            const isSelected = selectedScript?.id === script.id;
            
            return (
              <div
                key={script.id}
                onClick={() => setSelectedScript(script)}
                className={`bg-slate-800/50 rounded-lg p-4 border cursor-pointer transition-all ${
                  isSelected 
                    ? 'border-blue-500/50 bg-slate-800/70 shadow-lg shadow-blue-500/10' 
                    : 'border-slate-700/50 hover:border-slate-600 hover:bg-slate-800/60'
                }`}
              >
                {/* 标题和标签 - 简洁 */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded text-xs font-medium">
                        #{index + 1}
                      </span>
                      <span className={`px-2 py-0.5 ${tierInfo.bg} ${tierInfo.color} rounded text-xs`}>
                        {tierInfo.text}
                      </span>
                    </div>
                    <h4 className="text-white font-semibold text-sm mb-1 line-clamp-1">{script.title}</h4>
                    <p className="text-slate-400 text-xs truncate">
                      {script.keyword} • {script.script.duration}
                    </p>
                  </div>
                  {isSelected && (
                    <CheckCircle className="w-5 h-5 text-blue-400 flex-shrink-0 ml-2" />
                  )}
                </div>

                {/* 预测数据 - 紧凑 */}
                <div className="flex items-center gap-4 mb-2 pt-2 border-t border-slate-700/50">
                  <div className="flex items-center gap-1.5">
                    <Eye className="w-3.5 h-3.5 text-blue-400" />
                    <div>
                      <div className="text-white font-medium text-sm">
                        {formatNumber(script.predicted_performance.predicted_views)}
                      </div>
                      <div className="text-slate-500 text-xs">播放</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1.5">
                    <ThumbsUp className="w-3.5 h-3.5 text-green-400" />
                    <div>
                      <div className="text-white font-medium text-sm">
                        {formatNumber(script.predicted_performance.predicted_engagement.likes)}
                      </div>
                      <div className="text-slate-500 text-xs">点赞</div>
                    </div>
                  </div>
                </div>

                {/* 推荐理由简述 - 简洁 */}
                <p className="text-slate-400 text-xs line-clamp-1">
                  {script.reasoning.summary.split('；')[0]}
                </p>
              </div>
            );
          })}
        </div>

        {/* 脚本详情 - 简洁对话框 */}
        <div className="lg:sticky lg:top-4 h-fit">
          {selectedScript ? (
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl border border-slate-700/50 shadow-xl overflow-hidden">
              {/* 头部 - 简洁 */}
              <div className="bg-slate-800/50 p-4 border-b border-slate-700/50">
                <h3 className="text-lg font-semibold text-white mb-1.5 line-clamp-2">{selectedScript.title}</h3>
                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span>{selectedScript.script.duration}</span>
                  <span>•</span>
                  <span className="truncate">{selectedScript.keyword}</span>
                  <span className={`px-1.5 py-0.5 rounded text-xs ${getPerformanceTierInfo(selectedScript.predicted_performance.expected_performance_tier).bg} ${getPerformanceTierInfo(selectedScript.predicted_performance.expected_performance_tier).color}`}>
                    {getPerformanceTierInfo(selectedScript.predicted_performance.expected_performance_tier).text}
                  </span>
                </div>
              </div>

              {/* 内容区 - 可滚动，简洁 */}
              <div className="p-4 max-h-[calc(100vh-250px)] overflow-y-auto space-y-4">
                {/* 预测表现 - 紧凑 */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50">
                    <div className="flex items-center gap-1.5 mb-1">
                      <Eye className="w-4 h-4 text-blue-400" />
                      <span className="text-slate-400 text-xs">播放量</span>
                    </div>
                    <div className="text-lg font-semibold text-white mb-0.5">
                      {formatNumber(selectedScript.predicted_performance.predicted_views)}
                    </div>
                    <div className="text-slate-500 text-xs">
                      {formatNumber(selectedScript.predicted_performance.predicted_views_range.min)}-{formatNumber(selectedScript.predicted_performance.predicted_views_range.max)}
                    </div>
                  </div>

                  <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50">
                    <div className="flex items-center gap-1.5 mb-1">
                      <ThumbsUp className="w-4 h-4 text-green-400" />
                      <span className="text-slate-400 text-xs">互动率</span>
                    </div>
                    <div className="text-lg font-semibold text-white mb-0.5">
                      {(selectedScript.predicted_performance.predicted_engagement.rate * 100).toFixed(1)}%
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <span>💬 {formatNumber(selectedScript.predicted_performance.predicted_engagement.comments)}</span>
                      <span>↗️ {formatNumber(selectedScript.predicted_performance.predicted_engagement.shares)}</span>
                    </div>
                  </div>
                </div>

                {/* 脚本结构 - 简洁 */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-2 flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-slate-400" />
                    结构
                  </h4>
                  <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50 text-slate-300 text-xs">
                    {selectedScript.script.structure}
                  </div>
                </div>

                {/* Hook - 简洁 */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-2 flex items-center gap-1.5">
                    <Zap className="w-4 h-4 text-yellow-400" />
                    开场 Hook
                  </h4>
                  <div className="bg-slate-900/50 rounded-lg p-3 border border-yellow-500/20">
                    <p className="text-white text-sm mb-2 leading-relaxed">{selectedScript.script.hook.content}</p>
                    <div className="text-slate-400 text-xs space-y-0.5">
                      <div>{selectedScript.script.hook.duration}</div>
                      <div>{selectedScript.script.hook.visual_suggestion}</div>
                    </div>
                  </div>
                </div>

                {/* 主体内容 - 简洁 */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-2">主体内容</h4>
                  <div className="space-y-2">
                    {selectedScript.script.main_content.sections.map((section: any, idx: number) => (
                      <div key={idx} className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50">
                        <div className="flex items-start gap-2.5">
                          <span className="flex-shrink-0 w-5 h-5 rounded bg-blue-500/20 text-blue-400 text-xs flex items-center justify-center font-medium">
                            {idx + 1}
                          </span>
                          <div className="flex-1 min-w-0">
                            <h5 className="text-white font-medium text-sm mb-1">{section.title}</h5>
                            <p className="text-slate-400 text-xs mb-1.5 leading-relaxed">{section.content}</p>
                            <div className="flex items-center gap-1.5 text-xs text-slate-500">
                              <Clock className="w-3 h-3" />
                              <span>{section.duration}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* CTA - 简洁 */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-2 flex items-center gap-1.5">
                    <Target className="w-4 h-4 text-green-400" />
                    行动号召
                  </h4>
                  <div className="bg-slate-900/50 rounded-lg p-3 border border-green-500/20">
                    <p className="text-white text-sm mb-1.5 leading-relaxed">{selectedScript.script.cta.content}</p>
                    <div className="text-slate-400 text-xs">
                      {selectedScript.script.cta.duration}
                    </div>
                  </div>
                </div>

                {/* 关键要点 - 简洁 */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-2 flex items-center gap-1.5">
                    <Lightbulb className="w-4 h-4 text-yellow-400" />
                    关键要点
                  </h4>
                  <div className="space-y-1.5">
                    {selectedScript.script.key_points.map((point: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-2 text-slate-300 text-xs">
                        <CheckCircle className="w-3.5 h-3.5 text-green-400 flex-shrink-0 mt-0.5" />
                        <span className="leading-relaxed">{point}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 推荐理由 - 简洁 */}
                <div>
                  <h4 className="text-white font-medium text-sm mb-2">推荐理由</h4>
                  <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50 space-y-2">
                    <p className="text-slate-300 text-xs leading-relaxed">
                      {selectedScript.reasoning.summary}
                    </p>
                    <div className="pt-2 border-t border-slate-700/50">
                      <div className="text-slate-400 text-xs font-medium mb-1.5">优化建议：</div>
                      {selectedScript.reasoning.tips.map((tip: string, idx: number) => (
                        <div key={idx} className="flex items-start gap-1.5 text-slate-400 text-xs mb-1">
                          <span className="text-slate-500">•</span>
                          <span>{tip}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* 底部操作 - 简洁 */}
              <div className="p-3 border-t border-slate-700/50 bg-slate-800/30">
                <button 
                  onClick={() => {
                    const scriptText = `
标题：${selectedScript.title}

${selectedScript.script.structure}

开场 Hook：
${selectedScript.script.hook.content}
⏱️ ${selectedScript.script.hook.duration}
🎨 ${selectedScript.script.hook.visual_suggestion}

主体内容：
${selectedScript.script.main_content.sections.map((s: any, i: number) => `
${i + 1}. ${s.title}
   ${s.content}
   ⏱️ ${s.duration}
`).join('\n')}

行动号召 (CTA)：
${selectedScript.script.cta.content}
⏱️ ${selectedScript.script.cta.duration}

关键要点：
${selectedScript.script.key_points.map((p: string) => `• ${p}`).join('\n')}
`;
                    navigator.clipboard.writeText(scriptText);
                    alert('脚本已复制到剪贴板！');
                  }}
                  className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2 text-sm"
                >
                  <FileText className="w-4 h-4" />
                  复制脚本
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-slate-800/30 rounded-xl p-8 text-center border border-slate-700/50">
              <FileText className="w-12 h-12 text-slate-500 mx-auto mb-3 opacity-50" />
              <p className="text-slate-400 text-sm">点击左侧脚本查看详情</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
