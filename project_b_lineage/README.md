# 项目B：元数据血缘分析

## 项目概述

本项目实现数据仓库环境中的元数据血缘分析功能，能够自动解析ETL脚本中的依赖关系，构建表级和字段级血缘图，并提供变更影响分析能力。

## 业务价值

当上游表结构发生变更时，数据治理工程师需要快速评估影响范围。本系统提供以下能力：

- 自动解析SQL依赖关系
- 可视化展示血缘链路
- 量化评估变更风险
- 输出影响分析报告

## 项目结构
project_b_lineage/
├── docs/
│ ├── business_requirements.md
│ └── technical_design.md
├── sql/
│ ├── 01_ods_orders.sql
│ ├── 02_dwd_orders.sql
│ ├── 03_dws_customer_summary.sql
│ ├── 04_dws_product_summary.sql
│ └── 05_ads_sales_report.sql
├── scripts/
│ ├── lineage_parser.py
│ ├── lineage_builder.py
│ └── impact_analyzer.py
├── output/
│ ├── table_lineage.csv
│ ├── column_lineage.csv
│ ├── table_lineage.png
│ └── impact_analysis_report.txt
└── README.md

text

## 运行方式

```bash
cd project_b_lineage
pip install pandas networkx matplotlib sqlparse
python scripts/lineage_builder.py
输出示例
表级血缘树
text
└── ods_orders (ODS)
    └── dwd_orders (DWD)
        ├── dws_customer_summary (DWS)
        │   └── ads_sales_report (ADS)
        └── dws_product_summary (DWS)
            └── ads_sales_report (ADS)
影响分析报告
变更对象	受影响下游	风险等级	建议
ods_orders	4	MEDIUM	在测试环境验证后执行
dwd_orders	3	LOW	按正常变更流程处理
技术栈
Python 3.9+

pandas：数据处理

networkx：血缘图构建

matplotlib：可视化

sqlparse：SQL解析

核心能力
SQL依赖解析：自动识别INSERT、CREATE、FROM、JOIN等语法

表级血缘：构建完整的数据流转链路

字段级血缘：追踪字段级的依赖关系

影响分析：评估变更风险，输出影响范围

可视化：生成血缘关系图

text

---

## 然后执行推送

```bash
cd Desktop\data_quality_project_A\project_b_lineage

# 添加所有文件
git add .

# 提交
git commit -m "feat: 完成项目B元数据血缘分析"

# 推送到GitHub
git push origin main
