#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
燃煤发电基准煤耗计算程序
主程序入口
"""

import sys
import os
from typing import Dict, Any, Optional
from .input_handler import InputHandler
from .coal_consumption import CoalConsumptionCalculator
from .output_generator import OutputGenerator

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
        'coal_calorific_value': 29306.0,
        'electricity_output': 1000.0,
        'heating_output': 500.0,
        'efficiency': 0.9,
        '管道效率': 0.98,
    }
    
    # 运行主程序
    app.run(example_params)
    
    # 运行带供热的计算
    print("\n" + "="*50)
    app.run_with_heating(example_params)
    
    # 运行不同工况的计算
    print("\n" + "="*50)
    app.run_operation_modes(example_params)

if __name__ == "__main__":
    main()
