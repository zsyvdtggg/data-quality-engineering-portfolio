-- DWD层：订单明细表
-- 依赖源表：ods_orders
-- 数据清洗：过滤无效订单，转换字段格式
INSERT INTO dwd_orders
SELECT 
    order_id,
    user_id,
    product_id,
    order_amount,
    CASE WHEN order_status = 1 THEN '已完成' ELSE '未完成' END AS order_status_desc,
    DATE(create_time) AS order_date
FROM ods_orders
WHERE order_status IN (1, 2, 3);