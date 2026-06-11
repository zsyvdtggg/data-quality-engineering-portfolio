-- ADS层：销售报表
-- 依赖源表：dws_customer_summary, dws_product_summary
-- 业务逻辑：关联客户和商品汇总数据
INSERT INTO ads_sales_report
SELECT 
    c.user_id,
    c.order_count,
    c.total_amount,
    p.product_id,
    p.sales_count
FROM dws_customer_summary c
CROSS JOIN dws_product_summary p;