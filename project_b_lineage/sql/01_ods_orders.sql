-- ODS层：订单原始表
-- 数据来源：业务系统订单库
CREATE TABLE ods_orders (
    order_id VARCHAR(32),
    user_id INT,
    product_id INT,
    order_amount DECIMAL(10,2),
    order_status INT,
    create_time TIMESTAMP
);
