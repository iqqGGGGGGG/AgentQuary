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
5. answer 字段为正确选项的索引（0-based）

{format_instructions}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "请根据以下内容生成 {count} 道问答题：\n\n---\n{content}\n---"),
])

chain_generate = prompt | llm | parser
