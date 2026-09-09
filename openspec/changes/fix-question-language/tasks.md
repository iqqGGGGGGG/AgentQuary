## 1. 修改题目生成 prompt

- [x] 1.1 修改 `server/chains/generate_chain.py` 的 `system_prompt`：在规则列表中增加"所有题目、选项、讲解(explanation)必须使用中文输出，专业术语可保留英文原文并附中文解释"，运行 `pytest server/tests/test_generate.py -v` 确认测试通过

## 2. 修改研究阶段 prompt

- [x] 2.1 修改 `server/chains/research_chain.py` 的 `RESEARCH_SYSTEM_PROMPT`：在参数调整规则中增加"当用户输入包含中文时，搜索 query 应包含中文关键词（如 'Harness Engineering 线束工程'），优先搜索中文来源"，运行 `pytest server/tests/test_research.py -v` 确认测试通过

## 3. 验证

- [x] 3.1 运行 `pytest server/tests/ -v` 确认所有测试通过
- [ ] 3.2 启动后端，输入 "Harness Engineering 是什么？"，验证生成的题目为中文
