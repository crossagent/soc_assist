from langchain_community.utilities import SQLDatabase
from soc_reporter.utils.db_info import database_url
from typing import List
from soc_reporter.utils.set_env import log_db_schema_file_path
import json
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

db = SQLDatabase.from_uri(database_url)

toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(model="gpt-4o"))
from langchain_core.tools import tool

@tool
def db_list_tables_tool() -> List[str]:
    """
    List all tables in the database.
    Read JSON data from a file.
    """
    with open(log_db_schema_file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)

        # 提取表名
        table_names = list(json_data.keys())
        return table_names

@tool
def db_get_schema_tool(table_name: str) -> str:
    """
    Get the schema and example of a single table in the database.
    
    Args:
        table_name (str): 表名。
    
    Returns:
        str: 表的 schema 和 example 信息。
    """
    # 从 JSON 文件加载数据
    with open(log_db_schema_file_path, "r", encoding="utf-8") as f:
        table_info_dict = json.load(f)
    
    # 获取指定表名的 schema 和 example 信息
    if table_name in table_info_dict:
        schema = table_info_dict[table_name]['schema']
        example = table_info_dict[table_name]['example']
        combined_info = f"{schema}\n\n{example}"
        return combined_info
    else:
        return f"Table '{table_name}' not found in the JSON data."

@tool
def db_query_tool(query: str) -> str:
    """
    Execute a SQL query against the database and get back the result.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    result = db.run_no_throw(query)
    if not result:
        return "Error: Query failed. Please rewrite your query and try again."
    return result