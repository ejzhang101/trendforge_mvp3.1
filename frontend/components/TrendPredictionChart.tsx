import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, AreaChart, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Minus, AlertCircle, Target, Zap } from 'lucide-react';

interface Prediction {
  date: string;
  predicted_score: number;
  lower_bound: number;
  upper_bound: number;
  confidence_range: number;
}

interface TrendPrediction {
  keyword: string;
  predictions: Prediction[];
  trend_direction: 'rising' | 'falling' | 'stable';
  trend_strength: number;
  confidence: number;
  peak_day: number | null;
  peak_score: number;
  summary: string;
  model_accuracy?: {
    mae: number;
    rmse: number;
    mape: number;
  };
}

interface Props {
  prediction: TrendPrediction;
  showAccuracy?: boolean;
}

export default function TrendPredictionChart({ prediction, showAccuracy = false }: Props) {
  // Prepare chart data
  const chartData = prediction.predictions.map((p, idx) => ({
    day: `第${idx + 1}天`,
    date: new Date(p.date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
    predicted: p.predicted_score,
    lower: p.lower_bound,
    upper: p.upper_bound,
  }));

  // Trend direction icon and color
  const getTrendIcon = () => {
    switch (prediction.trend_direction) {
      case 'rising':
        return <TrendingUp className="w-5 h-5 text-green-400" />;
      case 'falling':
        return <TrendingDown className="w-5 h-5 text-red-400" />;
      default:
        return <Minus className="w-5 h-5 text-gray-400" />;
    }
  };

  const getTrendColor = () => {
    switch (prediction.trend_direction) {
      case 'rising':
        return '#10b981'; // green-500
      case 'falling':
        return '#ef4444'; // red-500
      default:
        return '#6b7280'; // gray-500
    }
  };

  const getTrendText = () => {
    switch (prediction.trend_direction) {
      case 'rising':
        return '上升趋势';
      case 'falling':
        return '下降趋势';
      default:
        return '稳定';
    }
  };

  // Confidence level
  const getConfidenceLevel = () => {
    if (prediction.confidence >= 80) return { text: '高', color: 'text-green-400' };
    if (prediction.confidence >= 60) return { text: '中', color: 'text-yellow-400' };
    return { text: '低', color: 'text-red-400' };
  };

  const confidenceLevel = getConfidenceLevel();

  return (
    <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 border border-white/10">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-600/20 rounded-lg">
            {getTrendIcon()}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">
              {prediction.keyword} - 7天趋势预测
            </h3>
            <p className="text-sm text-purple-300">
              {getTrendText()} • 强度: {prediction.trend_strength.toFixed(0)}
            </p>
          </div>
        </div>
        
        {/* Confidence Badge */}
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-xs text-purple-300">预测置信度</div>
            <div className={`text-2xl font-bold ${confidenceLevel.color}`}>
              {prediction.confidence.toFixed(0)}%
            </div>
            <div className="text-xs text-purple-400">{confidenceLevel.text}置信度</div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="mb-6">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={getTrendColor()} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={getTrendColor()} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="day" 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
                color: '#fff'
              }}
              formatter={(value: number) => [value.toFixed(1), '预测分数']}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="line"
            />
            
            {/* Confidence interval (area) */}
            <Area
              type="monotone"
              dataKey="upper"
              stroke="none"
              fill="#6366f1"
              fillOpacity={0.1}
              name="置信区间上限"
            />
            <Area
              type="monotone"
              dataKey="lower"
              stroke="none"
              fill="#6366f1"
              fillOpacity={0.1}
              name="置信区间下限"
            />
            
            {/* Predicted line */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke={getTrendColor()}
              strokeWidth={3}
              dot={{ fill: getTrendColor(), r: 4 }}
              activeDot={{ r: 6 }}
              name="预测分数"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Peak Info */}
      {prediction.peak_day && (
        <div className="bg-yellow-600/10 border border-yellow-600/30 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-3">
            <Target className="w-5 h-5 text-yellow-400" />
            <div className="flex-1">
              <div className="text-yellow-300 font-semibold">预计峰值</div>
              <div className="text-white text-sm">
                第{prediction.peak_day}天达到峰值 ({prediction.peak_score.toFixed(1)}分)
              </div>
            </div>
            <Zap className="w-6 h-6 text-yellow-400" />
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="bg-white/5 rounded-lg p-4 mb-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
          <p className="text-purple-200 text-sm italic">
            {prediction.summary}
          </p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="bg-white/5 rounded-lg p-3">
          <div className="text-purple-300 text-xs mb-1">趋势方向</div>
          <div className="text-white font-semibold flex items-center gap-2">
            {getTrendIcon()}
            {getTrendText()}
          </div>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="text-purple-300 text-xs mb-1">趋势强度</div>
          <div className="text-white font-semibold">
            {prediction.trend_strength.toFixed(0)}/100
          </div>
        </div>
        <div className="bg-white/5 rounded-lg p-3">
          <div className="text-purple-300 text-xs mb-1">预测置信度</div>
          <div className={`font-semibold ${confidenceLevel.color}`}>
            {prediction.confidence.toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Model Accuracy (Optional) */}
      {showAccuracy && prediction.model_accuracy && (
        <div className="border-t border-white/10 pt-4 mt-4">
          <div className="text-purple-300 text-sm font-semibold mb-3">模型准确度指标</div>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-white/5 rounded p-2">
              <div className="text-purple-400 text-xs">MAE</div>
              <div className="text-white text-sm font-mono">
                {prediction.model_accuracy.mae.toFixed(2)}
              </div>
            </div>
            <div className="bg-white/5 rounded p-2">
              <div className="text-purple-400 text-xs">RMSE</div>
              <div className="text-white text-sm font-mono">
                {prediction.model_accuracy.rmse.toFixed(2)}
              </div>
            </div>
            <div className="bg-white/5 rounded p-2">
              <div className="text-purple-400 text-xs">MAPE</div>
              <div className="text-white text-sm font-mono">
                {prediction.model_accuracy.mape.toFixed(1)}%
              </div>
            </div>
          </div>
          <p className="text-purple-400 text-xs mt-2 italic">
            💡 指标越低表示模型越准确
          </p>
        </div>
      )}

      {/* Daily Predictions Table */}
      <details className="mt-4">
        <summary className="text-purple-300 text-sm font-semibold cursor-pointer hover:text-purple-200">
          查看每日详细预测 ▼
        </summary>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="text-left text-purple-300 py-2 px-3">日期</th>
                <th className="text-right text-purple-300 py-2 px-3">预测分数</th>
                <th className="text-right text-purple-300 py-2 px-3">置信区间</th>
              </tr>
            </thead>
            <tbody>
              {prediction.predictions.map((pred, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-white/5">
                  <td className="text-white py-2 px-3">
                    第{idx + 1}天 ({new Date(pred.date).toLocaleDateString('zh-CN')})
                  </td>
                  <td className="text-white text-right py-2 px-3 font-mono">
                    {pred.predicted_score.toFixed(1)}
                  </td>
                  <td className="text-purple-300 text-right py-2 px-3 font-mono text-xs">
                    {pred.lower_bound.toFixed(1)} - {pred.upper_bound.toFixed(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
