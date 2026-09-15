## Purpose

提升题目质量、图片相关性和用户体验。

## Requirements

### Requirement: 用户意图理解
系统 SHALL 准确理解用户的隐含意图。

#### Scenario: 年级/难度限定
- **WHEN** 用户输入"小学六年级英语学习"
- **THEN** 系统生成六年级难度的英语单词/语法题目，而非泛泛的英语知识

#### Scenario: 场景限定
- **WHEN** 用户输入"考研政治重点"
- **THEN** 系统生成考研政治高频考点题目

### Requirement: 智能图片决策
系统 SHALL 用 LLM 判断每道题是否需要图片，并生成精准的图片 prompt。

#### Scenario: 需要图片的题目
- **WHEN** 题目涉及具体物体、场景、生物等可视化内容
- **THEN** LLM 判断 needs_image=true，并生成精准的英文图片描述

#### Scenario: 不需要图片的题目
- **WHEN** 题目涉及抽象概念、定义判断、逻辑推理
- **THEN** LLM 判断 needs_image=false，不生成图片

### Requirement: 图片展示优化
系统 SHALL 增大图片展示尺寸，支持点击放大查看。

#### Scenario: 图片展示
- **WHEN** 题目有配图
- **THEN** 图片高度增大到480px，点击可全屏查看

### Requirement: 避免图片细节题
系统 SHALL 避免出需要仔细辨认图片细节的题目。

#### Scenario: 图片题避免细节
- **WHEN** 题目有配图
- **THEN** 题目不依赖图片中的小字、细微差别等细节
