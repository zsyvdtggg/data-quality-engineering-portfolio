# 技术设计文档

## 1. 系统架构

本项目实现元数据血缘分析系统，包含三个核心模块：

| 模块 | 文件 | 职责 |
|------|------|------|
| SQL解析器 | lineage_parser.py | 解析SQL语句，提取表级和字段级依赖 |
| 血缘构建器 | lineage_builder.py | 构建血缘关系图，生成可视化 |
| 影响分析器 | impact_analyzer.py | 分析变更影响范围，生成报告 |

## 2. 数据模型

### 2.1 表级血缘数据结构

| 字段 | 类型 | 说明 |
|------|------|------|
| source_table | string | 源表名 |
| target_table | string | 目标表名 |
| layer | string | 数据层（ODS/DWD/DWS/ADS） |

### 2.2 字段级血缘数据结构

| 字段 | 类型 | 说明 |
|------|------|------|
| target_table | string | 目标表名 |
| target_column | string | 目标字段名 |
| source_expression | string | 源表达式 |
| source_tables | string | 依赖的源表 |

## 3. 核心算法

### 3.1 表依赖提取

使用正则表达式匹配以下模式：
- INSERT INTO table_name
- CREATE TABLE table_name
- FROM table_name
- JOIN table_name

### 3.2 字段血缘提取

解析SELECT子句中的字段表达式：
- 简单字段：column_name
- 带别名字段：expression AS alias
- 聚合函数：SUM(column) AS alias

### 3.3 影响分析算法

递归遍历有向图，计算下游依赖链：

def get_downstream(table):
    downstream = []
    for source, target in edges:
        if source == table:
            downstream.append(target)
            downstream.extend(get_downstream(target))
    return downstream

## 4. 输出说明

| 文件 | 格式 | 用途 |
|------|------|------|
| table_lineage.csv | CSV | 表级血缘数据，可用于进一步分析 |
| column_lineage.csv | CSV | 字段级血缘数据 |
| table_lineage.png | PNG | 血缘关系可视化图 |
| impact_analysis_report.txt | TXT | 影响分析报告 |

## 5. 运行环境

- Python 3.9+
- pandas
- networkx
- matplotlib
- sqlparse

## 6. 运行方式

python scripts/lineage_builder.py
