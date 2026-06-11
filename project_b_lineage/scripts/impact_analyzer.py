"""
影响分析器
功能：基于血缘关系分析上游表变更对下游的影响范围
"""

import pandas as pd
import networkx as nx
from typing import List, Dict, Set, Tuple


class ImpactAnalyzer:
    """影响分析器"""
    
    def __init__(self, table_graph: nx.DiGraph, table_lineage_df: pd.DataFrame):
        """
        初始化影响分析器
        
        Args:
            table_graph: 表级血缘有向图
            table_lineage_df: 表级血缘DataFrame
        """
        self.table_graph = table_graph
        self.table_lineage_df = table_lineage_df
        
    def analyze_upstream_change(self, target_table: str) -> Dict:
        """
        分析上游表变更对下游表的影响
        
        Args:
            target_table: 变更的目标表名
            
        Returns:
            影响分析结果字典
        """
        affected_downstream = self._get_all_downstream(target_table)
        
        # 按层级分组
        downstream_by_layer = self._group_by_layer(affected_downstream)
        
        # 获取直接依赖
        direct_downstream = self._get_direct_downstream(target_table)
        
        # 评估风险等级
        risk_level = self._assess_risk(len(affected_downstream), len(direct_downstream))
        
        return {
            'changed_table': target_table,
            'affected_count': len(affected_downstream),
            'affected_tables': affected_downstream,
            'affected_by_layer': downstream_by_layer,
            'direct_downstream': direct_downstream,
            'risk_level': risk_level,
            'recommendation': self._get_recommendation(risk_level)
        }
    
    def analyze_column_change(self, table_name: str, column_name: str, 
                               column_lineage_df: pd.DataFrame) -> Dict:
        """
        分析字段变更的影响
        
        Args:
            table_name: 表名
            column_name: 字段名
            column_lineage_df: 字段级血缘DataFrame
            
        Returns:
            字段影响分析结果
        """
        affected_columns = []
        
        # 查找依赖该字段的下游字段
        for _, row in column_lineage_df.iterrows():
            source_tables = row['source_tables'].split(', ')
            if table_name in source_tables:
                # 检查source_expression是否包含该字段
                if column_name in row['source_expression']:
                    affected_columns.append({
                        'target_table': row['target_table'],
                        'target_column': row['target_column'],
                        'source_expression': row['source_expression']
                    })
        
        # 评估风险
        risk_level = 'HIGH' if len(affected_columns) > 5 else 'MEDIUM' if len(affected_columns) > 0 else 'LOW'
        
        return {
            'changed_table': table_name,
            'changed_column': column_name,
            'affected_count': len(affected_columns),
            'affected_columns': affected_columns,
            'risk_level': risk_level,
            'recommendation': self._get_column_recommendation(risk_level)
        }
    
    def _get_all_downstream(self, table_name: str) -> List[str]:
        """递归获取所有下游表"""
        downstream = []
        for source, target in self.table_graph.edges():
            if source == table_name:
                downstream.append(target)
                downstream.extend(self._get_all_downstream(target))
        return list(set(downstream))
    
    def _get_direct_downstream(self, table_name: str) -> List[str]:
        """获取直接下游表"""
        direct = []
        for source, target in self.table_graph.edges():
            if source == table_name:
                direct.append(target)
        return direct
    
    def _group_by_layer(self, tables: List[str]) -> Dict[str, List[str]]:
        """按数据层分组"""
        groups = {
            'ODS': [],
            'DWD': [],
            'DWS': [],
            'ADS': [],
            '其他': []
        }
        
        for table in tables:
            if table.startswith('ods'):
                groups['ODS'].append(table)
            elif table.startswith('dwd'):
                groups['DWD'].append(table)
            elif table.startswith('dws'):
                groups['DWS'].append(table)
            elif table.startswith('ads'):
                groups['ADS'].append(table)
            else:
                groups['其他'].append(table)
        
        # 移除空组
        return {k: v for k, v in groups.items() if v}
    
    def _assess_risk(self, total_affected: int, direct_affected: int) -> str:
        """评估风险等级"""
        if total_affected > 10 or direct_affected > 5:
            return 'HIGH'
        elif total_affected > 3 or direct_affected > 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_recommendation(self, risk_level: str) -> str:
        """根据风险等级获取建议"""
        recommendations = {
            'HIGH': '建议在变更前进行充分测试，通知所有下游数据使用者，并在非业务高峰期执行',
            'MEDIUM': '建议在测试环境验证后执行，通知直接下游相关方',
            'LOW': '影响范围可控，可按正常变更流程处理'
        }
        return recommendations.get(risk_level, '请评估变更影响后执行')
    
    def _get_column_recommendation(self, risk_level: str) -> str:
        """根据字段变更风险等级获取建议"""
        recommendations = {
            'HIGH': '建议审查所有依赖该字段的ETL任务，可能需要修改多个下游脚本',
            'MEDIUM': '建议检查下游字段的依赖逻辑，确认变更后的兼容性',
            'LOW': '变更影响范围较小，可直接执行'
        }
        return recommendations.get(risk_level, '请评估字段变更影响')
    
    def generate_impact_report(self, column_lineage_df: pd.DataFrame = None) -> str:
        """
        生成完整的影响分析报告
        
        Args:
            column_lineage_df: 字段级血缘DataFrame（可选）
            
        Returns:
            报告文本
        """
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("数据治理影响分析报告")
        report_lines.append("=" * 70)
        report_lines.append("")
        
        # 分析每个表变更的影响
        for node in self.table_graph.nodes():
            result = self.analyze_upstream_change(node)
            if result['affected_count'] > 0:
                report_lines.append(f"【变更对象】: {node}")
                report_lines.append(f"  受影响下游表数量: {result['affected_count']}")
                report_lines.append(f"  直接下游表: {', '.join(result['direct_downstream']) if result['direct_downstream'] else '无'}")
                report_lines.append(f"  风险等级: {result['risk_level']}")
                report_lines.append(f"  建议: {result['recommendation']}")
                report_lines.append("")
        
        # 字段级影响分析（如果有数据）
        if column_lineage_df is not None and len(column_lineage_df) > 0:
            report_lines.append("-" * 70)
            report_lines.append("字段级影响分析")
            report_lines.append("-" * 70)
            report_lines.append("")
            
            # 分析每个表的关键字段
            for table in self.table_graph.nodes():
                table_cols = column_lineage_df[column_lineage_df['source_tables'].str.contains(table, na=False)]
                if len(table_cols) > 0:
                    report_lines.append(f"表 {table} 的字段被以下下游使用:")
                    for _, row in table_cols.iterrows():
                        report_lines.append(f"  - {row['target_table']}.{row['target_column']} ← {row['source_expression']}")
                    report_lines.append("")
        
        return "\n".join(report_lines)


def run_impact_analysis(table_graph: nx.DiGraph, table_lineage_df: pd.DataFrame, 
                         column_lineage_df: pd.DataFrame = None):
    """运行影响分析并输出报告"""
    analyzer = ImpactAnalyzer(table_graph, table_lineage_df)
    
    # 生成报告
    report = analyzer.generate_impact_report(column_lineage_df)
    print(report)
    
    # 保存报告
    with open('output/impact_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n影响分析报告已保存: output/impact_analysis_report.txt")
    
    return analyzer


if __name__ == "__main__":
    print("影响分析器模块")
    print("请通过 lineage_builder.py 调用此模块")