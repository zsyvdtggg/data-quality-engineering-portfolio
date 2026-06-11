# 数据治理工程师作品集

## 项目简介

本项目模拟企业级数据治理场景，包含两个完整的实践项目，展示数据质量管理和元数据管理的核心能力。

- **项目A**：数据质量检核与修复
- **项目B**：元数据血缘分析

---

## 项目A：数据质量检核与修复

### 业务场景

财务部门基于出租车行程数据计算月度收入，要求数据满足六条质量规则。本项目的目标是对原始数据进行质量检核，识别问题并执行修复。

### 数据说明

| 字段名 | 类型 | 业务含义 | 质量要求 |
|--------|------|----------|----------|
| VendorID | 数值 | 供应商编号 | 不能为空 |
| pickup_datetime | 时间戳 | 上车时间 | 不能为空 |
| dropoff_datetime | 时间戳 | 下车时间 | 晚于上车时间 |
| passenger_count | 整数 | 乘客数 | 1-6人 |
| trip_distance | 浮点数 | 行程距离 | 大于0 |
| fare_amount | 浮点数 | 车费金额 | 大于等于0 |
| payment_type | 整数 | 支付类型 | 1,2,3,4,5之一 |

### 质量规则与修复策略

| 规则 | 检核逻辑 | 违反行数 | 修复策略 |
|------|----------|----------|----------|
| VendorID非空 | 缺失值检测 | 31 | 众数填充 |
| pickup_datetime非空 | 缺失值检测 | 15 | 删除记录 |
| trip_distance大于0 | 异常值检测 | 20 | 中位数填充 |
| fare_amount非负 | 异常值检测 | 10 | 取绝对值 |
| passenger_count在1-6之间 | 范围检测 | 12 | 截断处理 |
| payment_type在枚举值内 | 枚举检测 | 6 | 众数填充 |

### 治理成果

| 指标 | 数值 |
|------|------|
| 原始数据行数 | 2005 |
| 清洗后行数 | 1985 |
| 处理行数 | 20 |
| 数据质量通过率 | 99.0% |

### 产出物

- `quality_report.html` - 质量检核报告
- `nyc_taxi_clean.csv` - 清洗后数据

### 运行方式

```bash
python data_quality_engine.py
项目B：元数据血缘分析
业务场景
数据仓库包含ODS、DWD、DWS、ADS五张表，需要分析上游表变更对下游表的影响范围，支持变更影响评估。

数据流转链路
text
ods_orders (ODS)
    ↓
dwd_orders (DWD)
    ↓
    ├── dws_customer_summary (DWS)
    └── dws_product_summary (DWS)
              ↓
         ads_sales_report (ADS)
影响分析结果
变更对象	受影响下游	风险等级	建议
ods_orders	4	MEDIUM	在测试环境验证后执行
dwd_orders	3	LOW	按正常变更流程处理
产出物
table_lineage.csv - 表级血缘数据

column_lineage.csv - 字段级血缘数据

table_lineage.png - 血缘关系图

impact_analysis_report.txt - 影响分析报告

运行方式
bash
cd project_b_lineage
pip install pandas networkx matplotlib sqlparse
python scripts/lineage_builder.py
项目结构
text
data-quality-engineering-portfolio/
│
├── README.md                          # 项目说明
├── requirements.txt                   # 依赖清单
│
├── data_quality_engine.py             # 项目A：质量检核引擎
├── nyc_taxi_dirty.csv                 # 项目A：原始脏数据
├── nyc_taxi_clean.csv                 # 项目A：清洗后数据
├── quality_report.html                # 项目A：质量报告
│
└── project_b_lineage/                 # 项目B：血缘分析
    ├── README.md
    ├── docs/
    │   ├── business_requirements.md
    │   └── technical_design.md
    ├── scripts/
    │   ├── lineage_parser.py
    │   ├── lineage_builder.py
    │   ├── impact_analyzer.py
    │   └── run_lineage_analysis.py
    ├── sql/
    │   ├── 01_ods_orders.sql
    │   ├── 02_dwd_orders.sql
    │   ├── 03_dws_customer_summary.sql
    │   ├── 04_dws_product_summary.sql
    │   └── 05_ads_sales_report.sql
    └── output/
        ├── table_lineage.csv
        ├── column_lineage.csv
        ├── table_lineage.png
        └── impact_analysis_report.txt
技术栈
领域	技术	用途
数据处理	Python, Pandas, NumPy	数据清洗、转换
数据质量	规则检核引擎	质量检核与修复
元数据管理	sqlparse, networkx	SQL解析、血缘分析
可视化	Matplotlib, Seaborn	血缘图、质量报告
版本控制	Git, GitHub	代码管理
核心能力总结
能力维度	项目A	项目B
数据标准定义	是	是
质量规则制定	是	否
数据质量检核	是	否
数据清洗修复	是	否
SQL解析	否	是
血缘关系构建	否	是
影响分析	否	是
可视化报告	是	是
运行环境
Python 3.9+

pip

安装依赖
bash
pip install pandas numpy matplotlib seaborn sqlparse networkx
联系方式
GitHub: github.com/zsyvdtggg

目标岗位：数据治理工程师（实习）
