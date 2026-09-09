## Purpose

限制知识库上传文件格式为 TXT 和 MD，确保解析100%可靠。

## Requirements

### Requirement: 文件格式限制
系统 SHALL 只接受 TXT 和 MD 格式的文件。

#### Scenario: 上传 TXT 文件
- **WHEN** 用户上传 .txt 文件
- **THEN** 系统正常解析并存储

#### Scenario: 上传 MD 文件
- **WHEN** 用户上传 .md 文件
- **THEN** 系统正常解析并存储

#### Scenario: 上传 PDF/Word 文件
- **WHEN** 用户尝试上传 .pdf 或 .docx 文件
- **THEN** 前端不显示这些格式，后端返回"不支持的文件格式"
