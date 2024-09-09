from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict
from soc_reporter.utils.set_env import item_semantics_db_file_path
from langchain_core.runnables import RunnableLambda
from schema.extract_data import ExtractedData, Character, GameItem

# # 搜索相似内容
# def search_similar(_dict):
#     return _search_similar(_dict["query"], _dict["top_k"])


# def _search_similar(query: str, top_k: int = 5):
#     embeddings = OpenAIEmbeddings()
#     vector_db = FAISS.load_local(item_semantics_db_file_path, embeddings, allow_dangerous_deserialization=True)
    
#     # 执行相似性搜索
#     results = vector_db.similarity_search(query, k=top_k)
    
#     # 返回匹配的道具ID和名称的pair
#     return [(result.metadata['item_id'], result.page_content) for result in results]

# def get_item_semantics_chain():
#     return RunnableLambda(search_similar)

def fetch_item_id_by_name(item_name: str, top_k: int = 5) -> str:
    embeddings = OpenAIEmbeddings()
    vector_db = FAISS.load_local(item_semantics_db_file_path, embeddings, allow_dangerous_deserialization=True)
    
    # 执行相似性搜索
    results = vector_db.similarity_search(item_name, k=top_k)
    
    # 返回匹配的道具ID和名称的pair
    return [(result.metadata['item_id'], result.page_content) for result in results]

# 处理 ExtractedData 中 GameItem 的函数
def fill_missing_item_ids(extracted_data: ExtractedData):
    if extracted_data.items:
        for item in extracted_data.items:
            if item.item_name and not item.item_id:
                # 调用 API 获取匹配的 item_id 列表
                possible_items = fetch_item_id_by_name(item.item_name)
                
                if possible_items:
                    # 使用第一个匹配的结果作为 item_id
                    item.item_id = possible_items[0][0]  # 取第一个匹配的 item_id
                    
                    # 将其他的 name 用逗号拼接，并存入 similar_names
                    similar_names_list = [name for _, name in possible_items[0:]]
                    item.similar_names = ", ".join(similar_names_list) if similar_names_list else None
    return extracted_data


if __name__ == "__main__":
    # # 示例查询
    # query = "树木"  # 替换为你想查询的道具名称
    # result = get_item_semantics_chain().invoke({"query":query, "top_k":1})

    # # 打印查询结果，显示道具ID和名称
    # for item_id, item_name in result:
    #     print(f"查询结果ID: {item_id}, 名称: {item_name}")

    # 示例数据
    data = ExtractedData(
        characters=[
            Character(role_name="Warrior", role_id="role123"),
            Character(role_name="Mage", role_id="role456")
        ],
        items=[
            GameItem(item_name="Sword", item_id=None, similar_names=None),
            GameItem(item_name="Shield", item_id=None, similar_names=None),
            GameItem(item_name="Bow", item_id="item999", similar_names=None)  # 已有ID
        ],
        buildings=None
    )

    # 调用函数处理
    updated_data = fill_missing_item_ids(data)

    # 输出结果
    print(updated_data.json(indent=2, ensure_ascii=False))
