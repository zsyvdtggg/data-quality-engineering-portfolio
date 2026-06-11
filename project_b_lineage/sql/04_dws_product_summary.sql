-- DWS层：商品汇总表
-- 依赖源表：dwd_orders
-- 业务逻辑：按商品维度汇总销售数据
INSERT INTO dws_product_summary
SELECT 
    product_id,
    COUNT(*) AS sales_count,
    SUM(order_amount) AS sales_amount
FROM dwd_orders
GROUP BY product_id;