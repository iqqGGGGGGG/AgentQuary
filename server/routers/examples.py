from fastapi import APIRouter
from models.schemas import ExampleTopic

router = APIRouter(prefix="/api", tags=["examples"])

EXAMPLES = [
    ExampleTopic(id=1, title="十分钟搞懂三国人物关系", category="历史", description="人物关系一网打尽"),
    ExampleTopic(id=2, title="太阳系的八大行星", category="科学", description="基础天文速览"),
    ExampleTopic(id=3, title="常见心理学效应", category="心理", description="看完更懂自己"),
    ExampleTopic(id=4, title="从种子到一杯咖啡", category="生活", description="咖啡入门必修"),
    ExampleTopic(id=5, title="认识中国传统节日", category="文化", description="传统习俗知多少"),
    ExampleTopic(id=6, title="人工智能基础概念", category="科技", description="AI入门不迷路"),
    ExampleTopic(id=7, title="测试你的动漫常识", category="娱乐", description="二次元冷知识"),
    ExampleTopic(id=8, title="学习职场沟通技巧", category="职场", description="说话也有方法论"),
    ExampleTopic(id=9, title="挑战世界历史冷知识", category="历史", description="看看你知道几个"),
    ExampleTopic(id=10, title="生活中的法律常识", category="法律", description="实用法律小百科"),
]


@router.get("/examples")
async def get_examples():
    return {"examples": EXAMPLES}
