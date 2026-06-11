-- DWS层：客户汇总表
-- 依赖源表：dwd_orders
-- 业务逻辑：按客户维度汇总订单金额和订单数量
INSERT INTO dws_customer_summary
SELECT 
    user_id,
    COUNT(*) AS order_count,
    SUM(order_amount) AS total_amount,
    AVG(order_amount) AS avg_amount
FROM dwd_orders
GROUP BY user_id;