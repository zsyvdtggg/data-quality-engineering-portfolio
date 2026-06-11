"""
血缘关系构建器
功能：基于SQL解析结果构建表级和字段级血缘图
"""

import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Set
from lineage_parser import parse_all_sql_files
from impact_analyzer import ImpactAnalyzer, run_impact_analysis


class LineageBuilder:
    """血缘关系构建器"""
    
    def __init__(self, sql_dir: str = 'sql'):
        self.sql_dir = sql_dir
        self.parsed_results = []
        self.table_graph = nx.DiGraph()  # 有向图，方向：源表 -> 目标表
        self.column_lineage_list = []
        
    def load_and_parse(self):
        """加载并解析所有SQL文件"""
        print("正在解析SQL文件...")
        self.parsed_results = parse_all_sql_files(self.sql_dir)
        return self.parsed_results
    
    def build_table_lineage(self) -> pd.DataFrame:
        """构建表级血缘关系DataFrame"""
        lineage_records = []
        
        for result in self.parsed_results:
            target = result['target_table']
            if not target:
                continue
                
            for source in result['source_tables']:
                lineage_records.append({
                    'source_table': source,
                    'target_table': target,
                    'layer': self._get_layer(target)
                })
                # 添加有向边
                self.table_graph.add_edge(source, target)
        
        self.table_lineage_df = pd.DataFrame(lineage_records)
        return self.table_lineage_df
    
    def build_column_lineage(self) -> pd.DataFrame:
        """构建字段级血缘关系DataFrame"""
        records = []
        
        for result in self.parsed_results:
            target_table = result['target_table']
            if not target_table:
                continue
            
            for target_col, source_expr in result['column_lineage'].items():
                records.append({
                    'target_table': target_table,
                    'target_column': target_col,
                    'source_expression': source_expr,
                    'source_tables': ', '.join(result['source_tables'])
                })
                self.column_lineage_list.append(records[-1])
        
        self.column_lineage_df = pd.DataFrame(records)
        return self.column_lineage_df
    
    def _get_layer(self, table_name: str) -> str:
        """根据表名判断数据层"""
        table_lower = table_name.lower()
        if table_lower.startswith('ods'):
            return 'ODS (操作数据存储层)'
        elif table_lower.startswith('dwd'):
            return 'DWD (明细数据层)'
        elif table_lower.startswith('dws'):
            return 'DWS (汇总数据层)'
        elif table_lower.startswith('ads'):
            return 'ADS (应用数据层)'
        else:
            return '其他'
    
    def visualize_table_lineage(self, output_path: str = 'output/table_lineage.png'):
        """可视化表级血缘关系"""
        import os
        os.makedirs('output', exist_ok=True)
        
        plt.figure(figsize=(14, 10))
        
        # 使用层次布局
        pos = nx.spring_layout(self.table_graph, k=2, seed=42)
        
        # 绘制节点和边
        nx.draw_networkx_nodes(self.table_graph, pos, node_size=3000, 
                                node_color='lightblue', edgecolors='darkblue')
        nx.draw_networkx_edges(self.table_graph, pos, edge_color='gray', 
                                arrows=True, arrowsize=20, arrowstyle='->')
        nx.draw_networkx_labels(self.table_graph, pos, font_size=10, font_weight='bold')
        
        plt.title('Table Lineage Graph', fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"表级血缘图已保存: {output_path}")
    
    def get_downstream_tables(self, table_name: str) -> List[str]:
        """获取指定表的所有下游表"""
        downstream = []
        for source, target in self.table_graph.edges():
            if source == table_name:
                downstream.append(target)
                # 递归获取下游的下游
                downstream.extend(self.get_downstream_tables(target))
        return list(set(downstream))
    
    def get_upstream_tables(self, table_name: str) -> List[str]:
        """获取指定表的所有上游表"""
        upstream = []
        for source, target in self.table_graph.edges():
            if target == table_name:
                upstream.append(source)
                upstream.extend(self.get_upstream_tables(source))
        return list(set(upstream))
    
    def generate_summary(self) -> Dict:
        """生成血缘分析摘要"""
        summary = {
            'total_tables': len(self.table_graph.nodes()),
            'total_dependencies': len(self.table_graph.edges()),
            'table_lineage_records': len(self.table_lineage_df) if hasattr(self, 'table_lineage_df') else 0,
            'column_lineage_records': len(self.column_lineage_df) if hasattr(self, 'column_lineage_df') else 0,
            'tables_by_layer': {}
        }
        
        for node in self.table_graph.nodes():
            layer = self._get_layer(node)
            if layer not in summary['tables_by_layer']:
                summary['tables_by_layer'][layer] = []
            summary['tables_by_layer'][layer].append(node)
        
        return summary
    
    def print_lineage_tree(self):
        """打印血缘树结构"""
        print("\n" + "=" * 60)
        print("表级血缘树")
        print("=" * 60)
        
        # 找到根节点（没有上游的表）
        all_nodes = set(self.table_graph.nodes())
        nodes_with_upstream = set()
        for source, target in self.table_graph.edges():
            nodes_with_upstream.add(target)
        
        root_nodes = all_nodes - nodes_with_upstream
        
        def print_tree(node, level=0, prefix="", is_last=True):
            indent = "    " * level
            connector = "└── " if is_last else "├── "
            print(f"{indent}{connector}{node} ({self._get_layer(node)})")
            
            children = [target for source, target in self.table_graph.edges() if source == node]
            for i, child in enumerate(children):
                print_tree(child, level + 1, prefix + ("    " if is_last else "│   "), i == len(children) - 1)
        
        for root in root_nodes:
            print_tree(root)
            print()
    
    def run(self):
        """执行完整的血缘分析流程"""
        print("=" * 60)
        print("血缘关系分析系统")
        print("=" * 60)
        
        # 1. 解析SQL
        self.load_and_parse()
        
        # 2. 构建表级血缘
        table_df = self.build_table_lineage()
        print("\n表级血缘关系:")
        print(table_df.to_string(index=False))
        
        # 3. 构建字段级血缘
        column_df = self.build_column_lineage()
        print("\n字段级血缘关系:")
        if len(column_df) > 0:
            print(column_df.to_string(index=False))
        else:
            print("无字段级血缘关系（SQL中未检测到字段映射）")
        
        # 4. 打印血缘树
        self.print_lineage_tree()
        
        # 5. 生成摘要
        summary = self.generate_summary()
        print("\n" + "=" * 60)
        print("血缘分析摘要")
        print("=" * 60)
        print(f"总表数量: {summary['total_tables']}")
        print(f"总依赖关系: {summary['total_dependencies']}")
        print(f"表级血缘记录: {summary['table_lineage_records']}")
        print(f"字段级血缘记录: {summary['column_lineage_records']}")
        
        print("\n按数据层分布:")
        for layer, tables in summary['tables_by_layer'].items():
            print(f"  {layer}: {', '.join(tables)}")
        
        # 6. 保存结果到CSV
        os.makedirs('output', exist_ok=True)
        table_df.to_csv('output/table_lineage.csv', index=False)
        if len(column_df) > 0:
            column_df.to_csv('output/column_lineage.csv', index=False)
        
        print("\n输出文件:")
        print("  output/table_lineage.csv - 表级血缘数据")
        if len(column_df) > 0:
            print("  output/column_lineage.csv - 字段级血缘数据")
        
        # 7. 生成可视化图表
        self.visualize_table_lineage()
        
        # 8. 运行影响分析
        print("\n" + "=" * 60)
        print("影响分析")
        print("=" * 60)
        analyzer = ImpactAnalyzer(self.table_graph, self.table_lineage_df)
        impact_report = analyzer.generate_impact_report(self.column_lineage_df if hasattr(self, 'column_lineage_df') else None)
        print(impact_report)
        
        # 保存影响分析报告
        with open('output/impact_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(impact_report)
        print("\n影响分析报告已保存: output/impact_analysis_report.txt")
        
        return summary


if __name__ == "__main__":
    builder = LineageBuilder(sql_dir='sql')
    builder.run()
