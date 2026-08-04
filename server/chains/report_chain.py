from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.schemas import ReportOutputSchema
from .llm import llm

parser = JsonOutputParser(pydantic_object=ReportOutputSchema)

system_prompt = """你是一个学习辅导助手。根据用户的答题结果，生成简洁的学习报告。

规则：
1. 语言自然、口语化、有鼓励性
2. 不要使用过于正式的教育术语

{format_instructions}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", """答题主题：{topic}
正确率：{accuracy}%
共 {total} 题，答对 {correct} 题

答对的题目：
{correct_list}

答错的题目（含用户答案和正确答案）：
{wrong_list}

请根据以上信息生成学习总结和鼓励语。"""),
])

chain_report = prompt | llm | parser
