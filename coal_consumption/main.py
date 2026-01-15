#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
燃煤发电基准煤耗计算程序
主程序入口
"""

import sys
import os
from typing import Dict, Any, Optional

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 将coal_consumption目录添加到Python路径，以便直接导入模块
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from input_handler import InputHandler
from coal_consumption import CoalConsumptionCalculator
from output_generator import OutputGenerator

class MainApplication:
    """
    主应用程序类
    """
    
    def __init__(self):
        self.input_handler = InputHandler()
        self.calculator = CoalConsumptionCalculator()
        self.output_generator = OutputGenerator()
    
    def run(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        运行主程序
        
        Args:
            parameters: 可选的参数字典
            
        Returns:
            计算结果字典
        """
        print("=== 燃煤发电基准煤耗计算程序 ===")
        print()
        
        # 获取输入参数
        print("1. 加载计算参数...")
        input_params = self.input_handler.get_user_input(parameters)
        calculation_params = self.input_handler.get_parameters_for_calculation(input_params)
        
        print("参数加载完成!")
        print(f"基准负荷率: {calculation_params['base_load']}%")
        print(f"基准温度: {calculation_params['base_temperature']}℃")
        print(f"基准压力: {calculation_params['base_pressure']}MPa")
        print()
        
        # 计算基准煤耗
        print("2. 计算基准煤耗...")
        results = self.calculator.calculate_benchmark_coal_consumption(calculation_params)
        
        print("计算完成!")
        print()
        
        # 生成报告
        print("3. 生成计算报告...")
        summary_report = self.output_generator.generate_summary_report(results)
        print(summary_report)
        print()
        
        # 导出结果
        print("4. 导出计算结果...")
        
        # 导出到Excel
        excel_path = "煤耗计算结果.xlsx"
        self.output_generator.export_to_excel(results, excel_path)
        
        # 导出到CSV
        csv_path = "煤耗计算结果.csv"
        self.output_generator.export_to_csv(results, csv_path)
        
        print()
        print("=== 计算完成 ===")
        print(f"结果已导出到: {excel_path} 和 {csv_path}")
        
        return results
    
    def run_with_heating(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        运行带供热影响的计算
        
        Args:
            parameters: 可选的参数字典
            
        Returns:
            计算结果字典
        """
        print("=== 带供热影响的煤耗计算 ===")
        print()
        
        # 获取输入参数
        input_params = self.input_handler.get_user_input(parameters)
        calculation_params = self.input_handler.get_parameters_for_calculation(input_params)
        
        # 计算带供热的煤耗
        results = self.calculator.calculate_coal_consumption_with_heating(calculation_params)
        
        # 生成报告
        print("计算结果:")
        print(f"纯发电煤耗: {results.get('power_only_coal_consumption', 0):.2f} g/kWh")
        print(f"综合煤耗: {results.get('combined_coal_consumption', 0):.2f} g/kWh")
        print(f"供热影响: {results.get('heating_impact', 0):.2f} g/kWh")
        print(f"供热比例: {results.get('heating_ratio', 0):.2f}")
        
        return results
    
    def run_operation_modes(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, float]]:
        """
        运行不同工况的计算
        
        Args:
            parameters: 可选的参数字典
            
        Returns:
            不同工况的计算结果
        """
        print("=== 不同运行工况煤耗计算 ===")
        print()
        
        # 获取输入参数
        input_params = self.input_handler.get_user_input(parameters)
        calculation_params = self.input_handler.get_parameters_for_calculation(input_params)
        
        # 计算不同工况的煤耗
        results = self.calculator.calculate_coal_consumption_by_operation_mode(calculation_params)
        
        # 生成比较报告
        comparison_report = self.output_generator.generate_comparison_report(results)
        print(comparison_report)
        
        # 导出比较结果
        comparison_path = "不同工况煤耗比较.xlsx"
        self.output_generator.export_comparison_to_excel(results, comparison_path)
        
        return results
    
    def run_benchmark_comparison(self, excel_file: str = "外部因素对煤耗的计算表1222.xlsx") -> Dict[str, Any]:
        """
        运行基准数据与月份数据的对比
        
        Args:
            excel_file: Excel文件路径
            
        Returns:
            对比结果字典
        """
        print("=== 基准数据与月份数据对比 ===")
        print()
        
        # 确保使用正确的文件路径 - 相对于项目根目录
        excel_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), excel_file)
        
        # 加载基准和月份数据
        print("1. 加载基准和月份数据...")
        data = self.input_handler.load_benchmark_and_monthly_data(excel_file_path)
        
        print("数据加载完成!")
        print(f"基准数据项数: {len(data['benchmark'])}")
        print(f"月份数量: {len(data['months'])}")
        print()
        
        # 计算参数对比
        print("2. 计算参数对比...")
        comparison_results = self.calculator.calculate_comparison_with_benchmark(
            data['benchmark'], data['months']
        )
        
        print("参数对比完成!")
        print()
        
        # 计算煤耗对比
        print("3. 计算煤耗对比...")
        coal_consumption_results = self.calculator.calculate_coal_consumption_for_monthly_data(
            data['benchmark'], data['months']
        )
        
        print("煤耗对比完成!")
        print()
        
        # 生成对比报告
        print("4. 生成对比报告...")
        
        # 打印基准煤耗
        print(f"基准煤耗: {coal_consumption_results['benchmark_coal_consumption']:.2f} g/kWh")
        print()
        
        # 打印各月份煤耗
        print("各月份煤耗对比:")
        for month, coal_consumption in coal_consumption_results['monthly_coal_consumption'].items():
            print(f"{month}: {coal_consumption:.2f} g/kWh")
        
        print()
        
        # 打印参数对比详情
        print("参数对比详情:")
        for month, month_data in comparison_results['monthly_comparisons'].items():
            print(f"\n{month}:")
            for param, comp_data in month_data['comparisons'].items():
                diff = comp_data['difference']
                ratio = comp_data['ratio']
                
                # 检查是否有影响煤耗系数
                if f'{param}_影响系数' in data['months'][month]:
                    factor = data['months'][month][f'{param}_影响系数']
                    print(f"  {param}: 基准={comp_data['benchmark']:.2f}, 当月={comp_data['monthly']:.2f}, 差异={diff:.2f}, 比例={ratio:.4f}, 影响系数={factor:.6f}")
                else:
                    print(f"  {param}: 基准={comp_data['benchmark']:.2f}, 当月={comp_data['monthly']:.2f}, 差异={diff:.2f}, 比例={ratio:.4f}")
        
        print()
        
        # 导出对比结果
        print("5. 导出对比结果...")
        
        # 合并结果
        combined_results = {
            'comparison_results': comparison_results,
            'coal_consumption_results': coal_consumption_results
        }
        
        # 导出到Excel
        comparison_path = "基准与月份数据对比.xlsx"
        self.output_generator.export_comparison_to_excel(combined_results, comparison_path)
        
        print()
        print("=== 对比完成 ===")
        print(f"结果已导出到: {comparison_path}")
        
        return combined_results

def main():
    """
    主函数
    """
    app = MainApplication()
    
    # 示例参数
    example_params = {
        'base_load': 100.0,
        'base_temperature': 25.0,
        'base_pressure': 16.7,
        'base_humidity': 60.0,
        'coal_calorific_value': 4854.0,
        'electricity_output': 1000.0,
        'heating_output': 500.0,
        'efficiency': 0.9,
    }
    
    # 运行主程序
    app.run(example_params)
    
    # 运行带供热的计算
    print("\n" + "="*50)
    app.run_with_heating(example_params)
    
    # 运行不同工况的计算
    print("\n" + "="*50)
    app.run_operation_modes(example_params)
    
    # 运行基准数据与月份数据对比
    print("\n" + "="*50)
    app.run_benchmark_comparison()

if __name__ == "__main__":
    main()
