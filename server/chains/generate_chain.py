from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.schemas import QuizOutputSchema
from .llm import llm

parser = JsonOutputParser(pydantic_object=QuizOutputSchema)

system_prompt = """你是一个专业的知识出题助手。你的任务是根据用户提供的内容，生成一组用于学习和记忆的问答题。

规则：
1. 题目围绕内容中的核心知识点，难度从简单到深入
2. 题型随机混合使用：
   - single_choice: 单选题，必须有恰好4个选项
   - true_false: 判断题，必须有恰好2个选项 ["正确", "错误"]
3. 每道题必须附带简明讲解(explanation)，50字以内
4. 避免重复题目、避免选项明显错误、避免题目与内容无关
5. 不得生成"排除题目"中已有的题目，即使只是措辞轻微变化也应换一个知识点或考查角度
5. answer 字段为正确选项的索引（0-based）
6. 所有题目、选项、讲解(explanation)必须使用中文输出。专业术语可保留英文原文并附中文解释（如 "线束工程(Harness Engineering)"）
7. 如果参考内容与用户输入的主题领域明显不一致（如用户问AI概念但参考内容全是机械工程），应以用户输入的领域为准生成题目，忽略不相关的参考内容

{format_instructions}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "请根据以下内容生成 {count} 道问答题：\n\n---\n{content}\n---\n\n排除题目（不得重复）：\n{excluded_questions}"),
])

chain_generate = prompt | llm | parser
