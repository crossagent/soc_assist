from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional, Dict, TypedDict

class Character(BaseModel):
    """Information about a game character."""
    role_name: Optional[str] = Field(..., description="The name of the game character")
    role_id: Optional[str] = Field(..., description="the unique role id of game character")

class GameItem(BaseModel):
    """Information about a person."""
    item_name: Optional[str] = Field(..., description="The entity name in the game")
    item_id: Optional[str] = Field(..., description="The entity unique id in the game")  #特别注意这个id，如果玩家不提供，那其实对应similar_names[0]的id，不一定是item_name的id
    similar_names: Optional[str] = Field(..., description="Always keep None")

class BaseBuild(BaseModel):
    """Information about a BaseBuild."""
    building_id: Optional[str] = Field(..., description="The building unique id in the game")
    building_owner_team_name: Optional[str] = Field(..., description="The owner team name")
    building_owner_team_id: Optional[str] = Field(..., description="The owner team unique id in the game")
    team_member_name: Optional[str] = Field(..., description="The owner team member's name")
    team_member_id: Optional[str] = Field(..., description="The owner team member's id")

class ExtractedData(BaseModel):
    """Extracted data about people and their associated items."""
    characters : Optional[List[Character]]
    items :  Optional[List[GameItem]]
    buildings:  Optional[List[BaseModel]]


def populate_data_to_extracted_data(extracted_data: Dict) -> ExtractedData:
    # 如果 extracted_data 为 None，或者某个键为 None，使用空列表代替
    characters_data = extracted_data.get('characters', [])
    items_data = extracted_data.get('items', [])
    buildings_data = extracted_data.get('buildings', [])

    # 创建 Character、GameItem、BaseBuild 对象列表，确保字段为 None 时不会崩溃
    characters = [Character(**char) for char in characters_data] if characters_data else None
    items = [GameItem(**item) for item in items_data] if items_data else None
    buildings = [BaseBuild(**build) for build in buildings_data] if buildings_data else None

    # 创建 ExtractedData 对象
    data = ExtractedData(
        characters=characters,
        items=items,
        buildings=buildings
    )

    return data

# 测试用例
if __name__ == "__main__":
    # 输入数据
    test_input = {
        "characters": [
            {
                "role_name": "zxy01",
                "role_id": None
            }
        ],
        "items": None,
        "buildings": None
    }

    # 期望的输出
    expected_output = ExtractedData(
        characters=[Character(role_name="zxy01", role_id=None)],
        items=None,
        buildings=None
    )

    # 执行函数
    actual_output = populate_data_to_extracted_data(test_input)

    # 输出测试结果
    assert actual_output == expected_output, f"Test failed: {actual_output} != {expected_output}"
    print("Test passed!")