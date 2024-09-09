import os
import json
from soc_reporter.utils.set_env import log_db_schema_file_path
from langchain_community.utilities import SQLDatabase
from soc_reporter.utils.db_info import database_url

def get_table_schema(db, table_name, column_whitelist):
    query = f"DESCRIBE {table_name};"
    result = db.run(query)

    # 将字符串解析为Python对象
    if isinstance(result, str):
        try:
            result = eval(result)
        except Exception as e:
            raise ValueError("Failed to parse result into Python objects: ", e)

    # 构建 CREATE TABLE 语句
    schema_lines = []
    for line in result:
        field_name = line[0]  # 字段名
        field_type = line[1]  # 数据类型

        # 仅当字段在白名单中时，才将其添加到schema中
        for col_info in column_whitelist:
            if field_name == col_info["name"]:
                col_comment = col_info.get("comment", "")
                schema_line = f"`{field_name}` {field_type}"
                if col_comment:
                    schema_line += f" COMMENT '{col_comment}'"
                schema_lines.append(schema_line)

    # 拼接整个CREATE TABLE语句
    schema = f"\nCREATE TABLE `{table_name}` (\n\t" + ",\n\t".join(schema_lines) + "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8;"

    return schema


def get_table_example(db, table_name, column_whitelist):
    """
    获取表的示例数据，并根据白名单过滤所需列。

    Args:
        db: 数据库对象，提供数据查询的接口。
        table_name (str): 表名。
        limit_num (int): 要获取的行数。
        column_whitelist (list): 包含白名单列的字典列表。

    Returns:
        str: 构建的示例数据字符串。
    """
    # 获取白名单列名
    whitelist_columns = [col["name"] for col in column_whitelist]
    columns_str = ", ".join(whitelist_columns)

    # 组织查询语句，使用白名单中的列
    query = f"SELECT {columns_str} FROM {table_name} LIMIT 3;"
    result = db.run(query)

    if not result:
        return "No data available."

    # 构建示例数据的表头
    example_lines = ["\t".join(whitelist_columns)]

    # 构建示例数据行
    for row in result:
        if isinstance(row, dict):
            filtered_row = [str(row[col]) for col in whitelist_columns]
            example_lines.append("\t".join(filtered_row))

    # 返回格式化的示例数据
    example_data = "/*\n" + f"3 rows from {table_name} table:\n" + "\n".join(example_lines) + "\n*/"
    
    return example_data

def save_tables_info_as_json(tables_info, file_path):
    """
    将多个表的白名单列信息保存为 JSON 文件。如果文件夹不存在，则创建文件夹。

    Args:
        db: 数据库对象，提供上下文信息的接口。
        tables_info (list): 包含表名和对应白名单列及注释的字典列表。
        file_path (str): JSON 文件路径。
    """
    # 初始化数据库和LLM模型
    db = SQLDatabase.from_uri(database_url, sample_rows_in_table_info=3)   

    table_info_dict = {}

    for table in tables_info:
        table_name = table["table_name"]
        column_whitelist = table["column_whitelist"]

        # 直接调用 get_table_schema 传入白名单列
        schema_info = get_table_schema(db, table_name, column_whitelist)
        exapmles = get_table_example(db, table_name, column_whitelist)

        # 构建 JSON 对象
        table_info_dict[table_name] = {
            "schema": schema_info,
            "example": exapmles  # 这里我们暂时忽略 example 的内容
        }

    # 检查文件夹是否存在，如果不存在，则创建文件夹
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 将字典保存为 JSON 文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(table_info_dict, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    tables_info = [
        {
            "table_name": "BattleLogInOut_0",
            "column_whitelist": [
                {"name": "GameSvrId"},
                {"name": "dtEventTime", "comment": "Event timestamp, records the time the event occurred"},
                {"name": "iZoneAreaID", "comment": "Zone Area ID, identifies the in-game zone or area"},
                {"name": "RoleID", "comment": "Role ID, uniquely identifies the player's role"},
                {"name": "BattleSrvId", "comment": "Battle server ID, identifies the server where the battle takes place"},
                {"name": "Map", "comment": "Map, identifies the in-game map id"},
                {"name": "team_number", "comment": "Team number, represents the number of players in the team"},
                {"name": "location", "comment": "Location, represents the player's coordinates in the game"},
                {"name": "BattleTeamId", "comment": "Battle team ID, the ID corresponding to the team the player is in. Returns 0 if no team"},
                {"name": "BattleLoginTime", "comment": "Battle login time, the time the player logged into the battle"},
                {"name": "BattleLogoutTime", "comment": "Battle logout time, the time the player logged out of the battle"},
                {"name": "BattleLogDuration", "comment": "Battle log duration, records the duration from login to logout in the battle"}
            ]
        },
        {
            "table_name": "BattleItem_0",
            "column_whitelist": [
                {"name": "dtEventTime", "comment": "Event timestamp, records the time the event occurred"},
                {"name": "BattleSrvId", "comment": "Battle server ID, identifies the server where the battle takes place"},
                {"name": "RoleID", "comment": "Role ID, uniquely identifies the player's role"},
                {"name": "BattleTeamId", "comment": "Battle team ID, the ID corresponding to the team the player is in. Returns 0 if no team"},
                {"name": "BattleItemId", "comment": "item unique id"},
                {"name": "BattleItemPosition"},
                {"name": "BattleItemChangeType"},
                {"name": "BattleItemChangeSource", "comment": "indicate the source of item change in string"},
                {"name": "BattleItemChangeSourceId", "comment": "the entity template id of source type"},
                {"name": "BattleItemDelta", "comment": "the numbers of item change"},
                {"name": "BattleItemBefore"},
                {"name": "BattleItemAfter"}
            ]
        },
        {
            "table_name": "Gather_0",
            "column_whitelist": [
                {"name": "dtEventTime", "comment": "time when gather event"},
                {"name": "BattleSrvId", "comment": "Battle server ID, identifies the server where the battle takes place"},
                {"name": "RoleID"},
                {"name": "location"},
                {"name": "GatherItem", "comment": "id of item"},
                {"name": "GatherItemNumber"},
                {"name": "GatherSource"},
                {"name": "GatherTool"}
            ]
        },
                {
            "table_name": "PlayerLogin_0",
            "column_whitelist": [
                {"name": "dtEventTime", "comment": "Event timestamp, records the time the event occurred"},
                {"name": "RoleID"},
                {"name": "RoleName"},
            ]
        }
    ]

    save_tables_info_as_json(tables_info, log_db_schema_file_path)