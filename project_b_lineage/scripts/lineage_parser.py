"""
SQL血缘解析器
功能：解析SQL语句，提取表级和字段级依赖关系
"""

import re
import sqlparse
from typing import List, Dict, Set, Tuple


class LineageParser:
    """SQL血缘解析器"""
    
    def __init__(self):
        self.source_tables: Set[str] = set()
        self.target_table: str = None
        self.column_lineage: Dict[str, str] = {}
    
    def parse_sql(self, sql: str) -> Dict:
        """
        解析SQL语句，返回依赖关系
        
        Args:
            sql: SQL语句字符串
            
        Returns:
            包含表级和字段级依赖的字典
        """
        self.source_tables.clear()
        self.target_table = None
        self.column_lineage.clear()
        
        # 标准化SQL
        sql = sql.strip()
        parsed = sqlparse.parse(sql)[0]
        
        # 提取目标表
        self._extract_target_table(sql)
        
        # 提取源表
        self._extract_source_tables(sql)
        
        # 提取字段级血缘
        self._extract_column_lineage(sql)
        
        return {
            'target_table': self.target_table,
            'source_tables': list(self.source_tables),
            'column_lineage': self.column_lineage
        }
    
    def _extract_target_table(self, sql: str):
        """提取目标表名"""
        sql_lower = sql.lower()
        
        # 匹配 INSERT INTO table_name
        insert_match = re.search(r'insert\s+into\s+([a-z_]+)', sql_lower)
        if insert_match:
            self.target_table = insert_match.group(1)
            return
        
        # 匹配 CREATE TABLE table_name
        create_match = re.search(r'create\s+table\s+([a-z_]+)', sql_lower)
        if create_match:
            self.target_table = create_match.group(1)
            return
    
    def _extract_source_tables(self, sql: str):
        """提取源表名"""
        sql_lower = sql.lower()
        
        # 找到 FROM 子句
        from_match = re.search(r'from\s+([a-z_]+)', sql_lower)
        if from_match:
            self.source_tables.add(from_match.group(1))
        
        # 找到 JOIN 子句
        join_matches = re.finditer(r'join\s+([a-z_]+)', sql_lower)
        for match in join_matches:
            self.source_tables.add(match.group(1))
    
    def _extract_column_lineage(self, sql: str):
        """提取字段级血缘关系"""
        sql_lower = sql.lower()
        
        # 匹配 SELECT 和 FROM 之间的内容
        select_match = re.search(r'select\s+(.*?)\s+from', sql_lower, re.DOTALL)
        
        if not select_match:
            return
        
        select_clause = select_match.group(1)
        
        # 按逗号分割字段（考虑括号内的逗号）
        columns = self._split_select_columns(select_clause)
        
        for col_expr in columns:
            col_expr = col_expr.strip()
            if not col_expr:
                continue
            
            # 处理 as alias 格式
            as_match = re.search(r'(.+?)\s+as\s+([a-z_]+)$', col_expr)
            if as_match:
                source_expr = as_match.group(1).strip()
                target_col = as_match.group(2).strip()
                self.column_lineage[target_col] = source_expr
                continue
            
            # 处理 function(args) 格式
            func_match = re.search(r'([a-z_]+\(.+?\))\s+([a-z_]+)$', col_expr)
            if func_match:
                source_expr = func_match.group(1).strip()
                target_col = func_match.group(2).strip()
                self.column_lineage[target_col] = source_expr
                continue
            
            # 处理简单字段
            simple_match = re.search(r'^([a-z_]+)$', col_expr)
            if simple_match:
                col_name = simple_match.group(1)
                self.column_lineage[col_name] = col_name
    
    def _split_select_columns(self, select_clause: str) -> List[str]:
        """分割SELECT子句中的字段，正确处理括号内的逗号"""
        columns = []
        current = []
        paren_depth = 0
        
        for char in select_clause:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                columns.append(''.join(current))
                current = []
            else:
                current.append(char)
        
        if current:
            columns.append(''.join(current))
        
        return columns


def parse_sql_file(file_path: str) -> Dict:
    """
    解析SQL文件
    
    Args:
        file_path: SQL文件路径
        
    Returns:
        依赖关系字典
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    parser = LineageParser()
    return parser.parse_sql(sql)


def parse_all_sql_files(sql_dir: str) -> List[Dict]:
    """
    解析目录下所有SQL文件
    
    Args:
        sql_dir: SQL文件目录路径
        
    Returns:
        所有SQL文件的解析结果列表
    """
    import os
    results = []
    
    for filename in sorted(os.listdir(sql_dir)):
        if filename.endswith('.sql'):
            file_path = os.path.join(sql_dir, filename)
            result = parse_sql_file(file_path)
            result['file'] = filename
            results.append(result)
            print(f"解析完成: {filename}")
            print(f"  目标表: {result['target_table']}")
            print(f"  源表: {result['source_tables']}")
            print()
    
    return results


if __name__ == "__main__":
    # 测试解析器
    test_sql = """
    INSERT INTO dwd_orders
    SELECT 
        order_id, 
        user_id, 
        SUM(order_amount) as total_amount
    FROM ods_orders
    WHERE order_status = 1
    """
    
    parser = LineageParser()
    result = parser.parse_sql(test_sql)
    
    print("=" * 50)
    print("SQL血缘解析器测试")
    print("=" * 50)
    print(f"测试SQL: {test_sql}")
    print(f"\n解析结果:")
    print(f"  目标表: {result['target_table']}")
    print(f"  源表: {result['source_tables']}")
    print(f"  字段血缘: {result['column_lineage']}")
