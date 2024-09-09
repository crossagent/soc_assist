# 数据库连接参数
db_username = "soc_tlog"
db_password = "cmuc5$NaQ&w$"
db_host = "sh-cdb-n7kbtprg.sql.tencentcdb.com"
db_port = 63596
db_name = "tlog-20240731"  # 替换为你的数据库名称

# 创建数据库URL
database_url = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"