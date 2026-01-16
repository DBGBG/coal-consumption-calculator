import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Dict, Any, List, Tuple

class OutputGenerator:
    """
    结果输出类
    负责生成和导出计算结果
    """
    
    def __init__(self):
        # 设置中文字体，避免图表中的中文显示问题
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文显示
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
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
        factor_names = {
            'load_factor': '负荷率修正',
            'temperature': '温度修正',
            'pressure': '压力修正',
            'humidity': '湿度修正',
            'heating': '供热修正',
            'steam_parameter': '蒸汽参数修正',
            'fuel': '燃料修正',
            'sea_temperature': '海水温度修正'
        }
        
        for key, display_name in factor_names.items():
            if key in results:
                report += f"{display_name}: {results[key]:.4f}\n"
        
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
                
                # 设置列宽
                worksheet = writer.sheets['煤耗计算结果']
                worksheet.column_dimensions['A'].width = 30
                worksheet.column_dimensions['B'].width = 20
            
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
        correction_factors = ['load_factor', 'temperature', 'pressure', 'humidity', 'heating', 'steam_parameter', 'fuel', 'sea_temperature']
        factor_names = {
            'load_factor': '负荷率修正',
            'temperature': '温度修正',
            'pressure': '压力修正',
            'humidity': '湿度修正',
            'heating': '供热修正',
            'steam_parameter': '蒸汽参数修正',
            'fuel': '燃料修正',
            'sea_temperature': '海水温度修正'
        }
        
        data = []
        labels = []
        for factor in correction_factors:
            if factor in results:
                data.append(results[factor])
                labels.append(factor_names.get(factor, factor))
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if chart_type == 'bar':
            bars = ax.bar(labels, data)
            ax.set_title('修正因子分析', fontsize=16)
            ax.set_ylabel('修正因子值', fontsize=12)
            ax.tick_params(axis='x', rotation=45, labelsize=10)
            ax.tick_params(axis='y', labelsize=10)
            
            # 添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, 
                        f'{height:.3f}', 
                        ha='center', va='bottom', fontsize=9)
        
        elif chart_type == 'pie':
            # 对于饼图，使用修正因子的绝对值变化（确保非负）
            relative_data = [abs(value - 1) * 100 for value in data]
            colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6','#ff6666']
            wedges, texts, autotexts = ax.pie(relative_data, labels=labels, autopct='%1.1f%%',
                                              colors=colors, startangle=90)
            ax.set_title('修正因子影响分析', fontsize=16)
            
            # 设置文本大小
            for text in texts:
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_fontsize(9)
        
        elif chart_type == 'line':
            ax.plot(labels, data, marker='o', linewidth=2, markersize=8)
            ax.set_title('修正因子趋势', fontsize=16)
            ax.set_ylabel('修正因子值', fontsize=12)
            ax.tick_params(axis='x', rotation=45, labelsize=10)
            ax.tick_params(axis='y', labelsize=10)
            ax.grid(True, linestyle='--', alpha=0.7)
        
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
            fig.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close(fig)  # 关闭图表，释放内存
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
        
        operation_mode_names = {
            'normal': '正常工况',
            'peak': '峰值工况',
            'low': '低谷工况',
            'heating': '供热工况'
        }
        
        for name, results in multi_results.items():
            display_name = operation_mode_names.get(name, name)
            report += f"## {display_name}\n"
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
                
                # 设置列宽
                worksheet = writer.sheets['煤耗比较']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"比较结果已成功导出到: {file_path}")
            return True
            
        except Exception as e:
            print(f"导出比较结果时出错: {e}")
            return False
    
    def export_benchmark_comparison(self, comparison_results: Dict[str, Any], file_path: str) -> bool:
        """
        导出基准数据与月份数据的对比结果
        
        Args:
            comparison_results: 对比结果字典
            file_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 基准数据
                benchmark_data = comparison_results.get('benchmark', {})
                benchmark_df = pd.DataFrame(list(benchmark_data.items()), columns=['参数', '基准值'])
                benchmark_df.to_excel(writer, sheet_name='基准数据', index=False)
                
                # 月份数据对比
                monthly_comparisons = comparison_results.get('monthly_comparisons', {})
                
                for month_name, month_data in monthly_comparisons.items():
                    comparisons = month_data.get('comparisons', {})
                    
                    if not comparisons:
                        continue
                    
                    # 准备数据
                    data = []
                    for param_name, param_data in comparisons.items():
                        row = {
                            '参数': param_name,
                            '基准值': param_data.get('benchmark', 0),
                            '当月值': param_data.get('monthly', 0),
                            '差异': param_data.get('difference', 0),
                            '比例': param_data.get('ratio', 0)
                        }
                        data.append(row)
                    
                    df = pd.DataFrame(data)
                    df.to_excel(writer, sheet_name=f'{month_name}对比', index=False)
            
            print(f"基准与月份数据对比结果已成功导出到: {file_path}")
            return True
            
        except Exception as e:
            print(f"导出基准与月份数据对比结果时出错: {e}")
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
    
    def save_results_to_file(self, report: str, file_path: str) -> bool:
        """
        将报告保存到文件
        
        Args:
            report: 报告字符串
            file_path: 保存文件路径
            
        Returns:
            是否保存成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已成功保存到: {file_path}")
            return True
        except Exception as e:
            print(f"保存报告时出错: {e}")
            return False
