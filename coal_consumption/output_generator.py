import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Dict, Any, List, Tuple
import json

class OutputGenerator:
    """
    结果输出类
    负责生成和导出计算结果
    """
    
    def __init__(self):
        pass
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """
        生成摘要报告
        
        Args:
            results: 计算结果字典
            
        Returns:
            摘要报告字符串
        """
        report = "# 煤耗计算结果摘要\n\n"
        
        # 基本信息
        report += "## 基本信息\n"
        report += f"基准煤耗: {results.get('benchmark_coal_consumption', 0):.2f} g/kWh\n"
        report += f"基本煤耗: {results.get('basic_coal_consumption', 0):.2f} g/kWh\n"
        report += f"综合修正因子: {results.get('correction_factor', 1):.4f}\n"
        report += f"总修正因子: {results.get('total_correction_factor', 1):.6f}\n\n"
        
        # 修正因子详情
        report += "## 修正因子详情\n"
        correction_factors = ['load_factor', 'temperature', 'pressure', 'humidity', 'heating', 'steam_parameter', 'fuel']
        for factor in correction_factors:
            if factor in results:
                report += f"{factor}: {results[factor]:.4f}\n"
        
        return report
    
    def generate_detailed_report(self, results: Dict[str, Any]) -> str:
        """
        生成详细报告
        
        Args:
            results: 计算结果字典
            
        Returns:
            详细报告字符串
        """
        report = "# 煤耗计算详细报告\n\n"
        
        # 基本信息
        report += "## 计算结果\n"
        for key, value in results.items():
            if isinstance(value, float):
                report += f"{key}: {value:.4f}\n"
            else:
                report += f"{key}: {value}\n"
        
        return report
    
    def export_to_excel(self, results: Dict[str, Any], file_path: str) -> bool:
        """
        导出结果到Excel文件
        
        Args:
            results: 计算结果字典
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            # 创建DataFrame
            data = []
            for key, value in results.items():
                if isinstance(value, float):
                    data.append({'参数': key, '值': value})
            
            df = pd.DataFrame(data)
            
            # 导出到Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='煤耗计算结果', index=False)
            
            print(f"结果已成功导出到: {file_path}")
            return True
            
        except Exception as e:
            print(f"导出Excel文件时出错: {e}")
            return False
    
    def export_to_csv(self, results: Dict[str, Any], file_path: str) -> bool:
        """
        导出结果到CSV文件
        
        Args:
            results: 计算结果字典
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            # 创建DataFrame
            data = []
            for key, value in results.items():
                if isinstance(value, float):
                    data.append({'参数': key, '值': value})
            
            df = pd.DataFrame(data)
            
            # 导出到CSV
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            print(f"结果已成功导出到: {file_path}")
            return True
            
        except Exception as e:
            print(f"导出CSV文件时出错: {e}")
            return False
    
    def generate_chart(self, results: Dict[str, Any], chart_type: str = 'bar') -> plt.Figure:
        """
        生成结果图表
        
        Args:
            results: 计算结果字典
            chart_type: 图表类型 ('bar', 'pie', 'line')
            
        Returns:
            Matplotlib图表对象
        """
        # 准备数据
        correction_factors = ['load_factor', 'temperature', 'pressure', 'humidity', 'heating', 'steam_parameter', 'fuel']
        factor_names = {
            'load_factor': '负荷率修正',
            'temperature': '温度修正',
            'pressure': '压力修正',
            'humidity': '湿度修正',
            'heating': '供热修正',
            'steam_parameter': '蒸汽参数修正',
            'fuel': '燃料修正'
        }
        
        data = []
        labels = []
        for factor in correction_factors:
            if factor in results:
                data.append(results[factor])
                labels.append(factor_names.get(factor, factor))
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if chart_type == 'bar':
            ax.bar(labels, data)
            ax.set_title('修正因子分析')
            ax.set_ylabel('修正因子值')
            ax.tick_params(axis='x', rotation=45)
        
        elif chart_type == 'pie':
            # 对于饼图，使用相对值
            relative_data = [(value - 1) * 100 for value in data]
            ax.pie(relative_data, labels=labels, autopct='%1.1f%%')
            ax.set_title('修正因子影响分析')
        
        elif chart_type == 'line':
            ax.plot(labels, data, marker='o')
            ax.set_title('修正因子趋势')
            ax.set_ylabel('修正因子值')
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        return fig
    
    def save_chart(self, fig: plt.Figure, file_path: str) -> bool:
        """
        保存图表到文件
        
        Args:
            fig: Matplotlib图表对象
            file_path: 保存文件路径
            
        Returns:
            是否保存成功
        """
        try:
            fig.savefig(file_path)
            print(f"图表已成功保存到: {file_path}")
            return True
        except Exception as e:
            print(f"保存图表时出错: {e}")
            return False
    
    def generate_comparison_report(self, multi_results: Dict[str, Dict[str, float]]) -> str:
        """
        生成多组结果的比较报告
        
        Args:
            multi_results: 多组计算结果
            
        Returns:
            比较报告字符串
        """
        report = "# 煤耗计算比较报告\n\n"
        
        for name, results in multi_results.items():
            report += f"## {name}\n"
            report += f"基准煤耗: {results.get('benchmark_coal_consumption', 0):.2f} g/kWh\n"
            report += f"综合修正因子: {results.get('correction_factor', 1):.4f}\n\n"
        
        return report
    
    def export_comparison_to_excel(self, multi_results: Dict[str, Dict[str, float]], file_path: str) -> bool:
        """
        导出多组结果的比较到Excel文件
        
        Args:
            multi_results: 多组计算结果
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            # 创建比较DataFrame
            data = []
            for name, results in multi_results.items():
                row = {'工况': name}
                for key, value in results.items():
                    if isinstance(value, float):
                        row[key] = value
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # 导出到Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='煤耗比较', index=False)
            
            print(f"比较结果已成功导出到: {file_path}")
            return True
            
        except Exception as e:
            print(f"导出比较结果时出错: {e}")
            return False
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """
        显示计算结果
        
        Args:
            results: 计算结果字典
        """
        print("=== 煤耗计算结果 ===")
        for key, value in results.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
        print("===================")
