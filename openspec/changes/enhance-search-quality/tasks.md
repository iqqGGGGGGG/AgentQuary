## 1. 后端搜索参数优化

- [x] 1.1 修改 `server/chains/research_chain.py` 的 `ToolAction` 类：将 `max_results` 默认值从 3 改为 10，将 `search_depth` 默认值从 "basic" 改为 "advanced"
- [x] 1.2 修改 `server/chains/research_chain.py` 的 `RESEARCH_SYSTEM_PROMPT`：更新参数调整规则——"结果数量默认 10 条（最大值）"、"搜索深度始终用 advanced"、增加"对冷门/专业主题，如果第一轮搜索结果不够明确，应生成多组不同角度的搜索词分别搜索（如 'Harness Engineering 线束工程' 和 'Harness Engineering automotive wiring harness'），通过多数结果判断正确领域"

## 2. 前端超时优化

- [x] 2.1 修改 `src/services/api.ts` 的 `request` 函数：增加可选 `timeout` 参数（默认 150000）；修改 `generate` 和 `report` 调用传入 `timeout: 300000`

## 3. 验证

- [x] 3.1 运行 `pytest server/tests/ -v` 确认后端测试通过
