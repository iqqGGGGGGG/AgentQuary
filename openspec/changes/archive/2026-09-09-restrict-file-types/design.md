## Context

Word/PDF 解析存在编码和格式问题，MVP 阶段限制为纯文本格式最可靠。

## Decisions

### Decision 1: 只保留 TXT/MD

**选择**: 移除 PDF 和 Word 支持，只保留 TXT 和 MD

**理由**: 纯文本解析100%可靠，无编码问题

### Decision 2: 移除解析依赖

**选择**: 从 requirements.txt 移除 PyPDF2 和 python-docx

**理由**: 减少不必要的依赖
