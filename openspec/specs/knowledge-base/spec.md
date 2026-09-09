# knowledge-base Specification

## Purpose
实现用户自主上传文档、建立知识库的能力。用户可以上传 PDF、Word、TXT、MD 等格式的文档，系统自动解析并存储，用户可以基于知识库中的文档生成问答题目。

## Requirements

### Requirement: 文档上传
系统 SHALL 支持用户上传 PDF、Word、TXT、MD 格式的文档。

#### Scenario: 上传 PDF 文档
- **WHEN** 用户选择一个 PDF 文件上传
- **THEN** 系统接收文件，解析 PDF 内容，提取文本并存储

#### Scenario: 上传 Word 文档
- **WHEN** 用户选择一个 .docx 文件上传
- **THEN** 系统接收文件，解析 Word 内容，提取文本并存储

#### Scenario: 上传文本文件
- **WHEN** 用户选择一个 .txt 或 .md 文件上传
- **THEN** 系统接收文件，直接读取文本内容并存储

#### Scenario: 文件格式不支持
- **WHEN** 用户上传不支持的文件格式（如图片、视频）
- **THEN** 系统返回错误提示"不支持的文件格式"

#### Scenario: 文件过大
- **WHEN** 用户上传超过 10MB 的文件
- **THEN** 系统返回错误提示"文件不能超过10MB"

### Requirement: 文档解析
系统 SHALL 自动解析上传文档中的文本内容。

#### Scenario: PDF 文本提取
- **WHEN** 系统接收到 PDF 文件
- **THEN** 提取所有页面的文本内容，合并为完整文本

#### Scenario: Word 文本提取
- **WHEN** 系统接收到 Word 文件
- **THEN** 提取所有段落的文本内容，合并为完整文本

#### Scenario: 解析失败
- **WHEN** 文档解析失败（如文件损坏、加密）
- **THEN** 系统返回错误提示"文档解析失败，请检查文件是否正常"

### Requirement: 知识库管理
系统 SHALL 提供知识库管理功能，用户可以查看和删除已上传的文档。

#### Scenario: 查看知识库列表
- **WHEN** 用户进入知识库页面
- **THEN** 展示所有已上传的文档列表，包含文件名、上传时间、文档类型、字数

#### Scenario: 删除文档
- **WHEN** 用户选择删除一个文档
- **THEN** 系统删除文件和数据库记录，从知识库中移除

#### Scenario: 查看文档内容
- **WHEN** 用户点击一个文档
- **THEN** 展示文档的解析后文本内容预览

### Requirement: 基于文档生成题目
系统 SHALL 支持从知识库选择文档作为题目来源。

#### Scenario: 选择文档生成题目
- **WHEN** 用户从知识库选择一个文档并点击"生成题目"
- **THEN** 系统使用该文档的文本内容作为输入，调用题目生成接口

#### Scenario: 文档内容过短
- **WHEN** 选择的文档解析后文本少于 50 字
- **THEN** 系统返回提示"文档内容过少，无法生成有效题目"

### Requirement: 文件存储
系统 SHALL 将上传的文件存储在服务器本地。

#### Scenario: 文件存储路径
- **WHEN** 用户上传文件
- **THEN** 文件保存到 `server/uploads/{user_id}/{timestamp}_{filename}`

#### Scenario: 文件名安全处理
- **WHEN** 用户上传包含特殊字符的文件名
- **THEN** 系统对文件名进行安全处理，去除特殊字符
