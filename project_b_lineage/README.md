# 项目B：元数据血缘分析

## 项目概述

本项目实现数据仓库环境中的元数据血缘分析功能，能够自动解析ETL脚本中的依赖关系，构建表级和字段级血缘图，并提供变更影响分析能力。

## 业务价值

当上游表结构发生变更时，数据治理工程师需要快速评估影响范围。本系统提供以下能力：

- 自动解析SQL依赖关系
- 可视化展示血缘链路
- 量化评估变更风险
- 输出影响分析报告

## 数据模型

本项目模拟数据仓库5层数据模型：

| 表名 | 层级 | 说明 |
|------|------|------|
| ods_orders | ODS | 订单原始数据 |
| dwd_orders | DWD | 订单明细数据 |
| dws_customer_summary | DWS | 客户维度汇总 |
| dws_product_summary | DWS | 商品维度汇总 |
| ads_sales_report | ADS | 销售报表 |

## 数据流转链路
ods_orders (ODS)
↓
dwd_orders (DWD)
↓
├── dws_customer_summary (DWS)
│ ↓
└── dws_product_summary (DWS)
↓
ads_sales_report (ADS)

text

## 项目结构
project_b_lineage/
├── docs/
│ ├── business_requirements.md
│ └── technical_design.md
├── scripts/
│ ├── lineage_parser.py
│ ├── lineage_builder.py
│ ├── impact_analyzer.py
│ └── run_lineage_analysis.py
├── sql/
│ ├── 01_ods_orders.sql
│ ├── 02_dwd_orders.sql
│ ├── 03_dws_customer_summary.sql
│ ├── 04_dws_product_summary.sql
│ └── 05_ads_sales_report.sql
├── output/
│ ├── table_lineage.csv
│ ├── column_lineage.csv
│ ├── table_lineage.png
│ └── impact_analysis_report.txt
└── README.md

text

## 运行方式

### 安装依赖

```bash
pip install pandas networkx matplotlib sqlparse
执行分析
bash
cd project_b_lineage
python scripts/lineage_builder.py
输出说明
表级血缘数据 (table_lineage.csv)
source_table	target_table	layer
ods_orders	dwd_orders	DWD
dwd_orders	dws_customer_summary	DWS
dwd_orders	dws_product_summary	DWS
字段级血缘数据 (column_lineage.csv)
target_table	target_column	source_expression
dwd_orders	order_id	order_id
dws_customer_summary	total_amount	sum(order_amount)
影响分析报告
变更对象	受影响下游	风险等级	建议
ods_orders	4	MEDIUM	在测试环境验证后执行
dwd_orders	3	LOW	按正常变更流程处理
技术栈
组件	技术	用途
解析	sqlparse	SQL语句解析
数据处理	pandas	血缘数据整理
图模型	networkx	血缘关系图构建
可视化	matplotlib	血缘图渲染