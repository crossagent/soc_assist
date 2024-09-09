from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict
from soc_reporter.utils.set_env import item_semantics_db_file_path
from langchain_core.runnables import Runnable,RunnableLambda
from langchain_community.utilities import SQLDatabase
from soc_reporter.utils.db_info import database_url
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from schema.extract_data import ExtractedData
import ast

# def query_player_roleid(_dict):

#     execute_query = QuerySQLDataBaseTool(db=db)

#     sql_str = f"SELECT `RoleID` FROM PlayerLogin_0 where `RoleName` = '{_dict['role_name']}' limit 1;"

#     result_str = execute_query.invoke(sql_str)
    
#     # 使用 ast.literal_eval 将字符串解析为实际的 Python 对象
#     result = ast.literal_eval(result_str)

#     return result[0][0]

# def get_query_player_roleid_chain() -> Runnable[Dict, int]:
#     return RunnableLambda(query_player_roleid)

def fetch_role_id_by_name(role_name : str) -> int:
    # 初始化数据库和LLM模型
    db = SQLDatabase.from_uri(database_url, sample_rows_in_table_info=3)    

    execute_query = QuerySQLDataBaseTool(db=db)

    sql_str = f"SELECT `RoleID` FROM PlayerLogin_0 where `RoleName` = '{role_name}'  ORDER BY `dtEventTime` DESC limit 1;"

    try:
        result_str = execute_query.invoke(sql_str)
        
        print(f"user id query:{result_str}")

        # 使用 ast.literal_eval 将字符串解析为实际的 Python 对象
        result = ast.literal_eval(result_str)
        
        return result[0][0]
    
    except (ValueError, SyntaxError, IndexError) as e:
        # 捕捉可能的解析错误、索引错误或其他异常，并返回 -1
        return -1

def fill_missing_role_ids(extracted_data: ExtractedData):
    # 打印函数名和描述信息
    print("执行函数: fill_missing_role_ids - 函数执行之前的 ExtractedData 内容如下：")
    
    # 打印 ExtractedData 对象的内容
    print(extracted_data.json(indent=2, ensure_ascii=False))

    if extracted_data.characters:
        for character in extracted_data.characters:
            if character.role_name and not character.role_id:
                # 调用API获取角色ID并填充
                character.role_id = fetch_role_id_by_name(character.role_name)
    return extracted_data

if __name__ == "__main__":
    # 示例查询
    #result = get_query_player_roleid_chain().invoke({"role_name":"Tyi_2016"})

    result = fetch_role_id_by_name("gengww006")

    print(f"查询结果ID: {result}")