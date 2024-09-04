from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

# 创建模型实例
model = ChatOpenAI(model="gpt-4o-mini")

# 创建工具列表
tools = [TavilySearchResults(max_results=2)]

# 创建代理图
graph = create_react_agent(model, tools)

# 使用代理图
response = graph.invoke({"input": "请告诉我关于人工智能的最新发展"})
print(response)
