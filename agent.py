from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

#model = ChatAnthropic(model="claude-3-5-sonnet-20240620")
model = ChatOpenAI(model="gpt-4o-mini")

tools = [TavilySearchResults(max_results=2)]

from langgraph.prebuilt import ToolNode

# 创建人工节点
def human_input(query: str) -> str:
    """获取用户输入"""
    return input(f"人工节点: {query}\n请输入您的回答: ")

human_node = ToolNode(
    name="人工节点",
    description="当需要人工干预或额外信息时使用此工具",
    func=human_input
)

# 将人工节点添加到工具列表中
tools.append(human_node)




graph = create_react_agent(model, tools)