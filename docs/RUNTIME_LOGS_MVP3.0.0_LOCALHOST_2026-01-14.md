# Runtime Logs Snapshot — MVP 3.0.0 (localhost)

**日期**: 2026-01-14  
**环境**: localhost（Frontend :3000, Backend :8000）  
**日志来源**: `/tmp/backend_mvp3.log`, `/tmp/frontend_mvp3.log`

---

## Backend snapshot (tail)

```
✅ Using Enhanced Social Media Collector (MVP 3.0)
✅ Using Predictive Recommendation Engine (MVP 3.0 with Prophet)
✅ Prophet Prediction Engine loaded (MVP 3.0)
✅ Redis cache connected
✅ Twitter API initialized (fast-fail mode)
✅ SerpAPI collector initialized
✅ Backtest Analyzer loaded (MVP 2.0)
...
   ✅ High-confidence predictions (75.0%+): 5/5
INFO:     127.0.0.1:60966 - "POST /api/v3/predict-trends HTTP/1.1" 200 OK
```

---

## Frontend snapshot (tail)

```
GET /analysis/UCcIvNGMBSQWwo1v3n-ZRBCw 200 in 1057ms
✓ Compiled /api/analysis/[channelId] in 108ms (842 modules)
...
🔄 Refreshing stored trend predictions... {
  channelId: 'UCcIvNGMBSQWwo1v3n-ZRBCw',
  storedAlgoVersion: null,
  targetAlgoVersion: '2026-01-14-75plus',
  storedMinConfidence: 9,
  targetMinConfidence: 75,
  keywords: [
    'actually traderlifestyle daytradingforbeginners',
    'actually traderlifestyle daytradingforbeginners',
    'actually traderlifestyle daytradingforbeginners',
    'actually traderlifestyle daytradingforbeginners',
    'profitable trader daytradingforbeginners'
  ]
}
✅ Refreshed predictions saved { trendPredictionsCount: 5, emergingTrendsCount: 0 }
```

---

## Notes

- 本 snapshot 用于证明：
  - 后端 Prophet 预测流程可用，且能输出 ≥75% 的高置信度预测（筛选/阈值日志可见）
  - 前端在读取旧数据时，会自动触发 refresh 并写回 DB（解决“55% 仍显示”的缓存问题）

