#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本功能测试脚本
"""

import sys
import os

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 添加coal_consumption目录到sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'coal_consumption')))

# 设置详细的错误输出
sys.tracebacklimit = 10

def test_basic_functionality():
    """
    测试基本功能
    """
    print("=== 基本功能测试 ===")
    
    # 测试1: 检查模块导入
    print("\n1. 测试模块导入...")
    try:
        from coal_consumption.input_handler import InputHandler
        print("✓ InputHandler 导入成功")
        
        from coal_consumption.coal_consumption import CoalConsumptionCalculator
        print("✓ CoalConsumptionCalculator 导入成功")
        
        from coal_consumption.output_generator import OutputGenerator
        print("✓ OutputGenerator 导入成功")
        
        from coal_consumption.correction_factors import CorrectionFactors
        print("✓ CorrectionFactors 导入成功")
        
        from coal_consumption.utils import load_parameters, validate_numeric
        print("✓ utils 模块导入成功")
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False
    
    # 创建对象
    try:
        input_handler = InputHandler()
        calculator = CoalConsumptionCalculator()
        output_generator = OutputGenerator()
        correction = CorrectionFactors()
        print("\n✓ 所有类实例化成功")
    except Exception as e:
        print(f"✗ 类实例化失败: {e}")
        return False
    
    # 测试2: 获取默认参数
    print("\n2. 测试默认参数加载...")
    try:
        default_params = input_handler.get_default_parameters()
        print(f"✓ 默认参数加载成功，包含 {len(default_params)} 个参数")
        print("关键参数:")
        key_params = ['base_load', 'base_temperature', 'base_pressure', 'coal_calorific_value']
        for param in key_params:
            if param in default_params:
                print(f"  {param}: {default_params[param]}")
    except Exception as e:
        print(f"✗ 默认参数加载失败: {e}")
        return False
    
    # 测试3: 参数验证
    print("\n3. 测试参数验证...")
    try:
        test_params = {
            'base_load': 120,  # 超出范围的负荷率
            'base_temperature': -50,  # 超出范围的温度
            'efficiency': 1.5,  # 超出范围的效率
            'coal_calorific_value': 5000
        }
        validated_params = input_handler.validate_parameters(test_params)
        print(f"✓ 参数验证成功")
        print(f"参数验证后:")
        for param in validated_params:
            print(f"  {param}: {validated_params[param]}")
    except Exception as e:
        print(f"✗ 参数验证失败: {e}")
        return False
    
    # 测试4: 基本煤耗计算
    print("\n4. 测试基本煤耗计算...")
    try:
        basic_coal = calculator.calculate_basic_coal_consumption(
            electricity_output=1000.0,
            coal_calorific_value=4854.0,
            efficiency=0.9
        )
        print(f"✓ 基本煤耗计算成功")
        print(f"基本煤耗: {basic_coal:.2f} g/kWh")
    except Exception as e:
        print(f"✗ 基本煤耗计算失败: {e}")
        return False
    
    # 测试5: 修正因子计算
    print("\n5. 测试修正因子计算...")
    try:
        # 负荷率修正因子
        load_correction = correction.calculate_load_factor_correction(80, 100)
        print(f"✓ 负荷率修正因子计算成功")
        print(f"负荷率修正因子 (80%/100%): {load_correction:.3f}")
        
        # 温度修正因子
        temp_correction = correction.calculate_temperature_correction(30, 25)
        print(f"✓ 温度修正因子计算成功")
        print(f"温度修正因子 (30℃/25℃): {temp_correction:.3f}")
    except Exception as e:
        print(f"✗ 修正因子计算失败: {e}")
        return False
    
    # 测试6: 生成报告
    print("\n6. 测试报告生成...")
    try:
        test_results = {
            'benchmark_coal_consumption': 102.5,
            'basic_coal_consumption': 100.0,
            'correction_factor': 1.025,
            'total_correction_factor': 1.025,
            'load_factor': 1.01,
            'temperature': 1.005,
            'pressure': 1.0,
            'humidity': 1.0,
            'heating': 1.0,
            'steam_parameter': 1.0,
            'fuel': 1.0
        }
        summary = output_generator.generate_summary_report(test_results)
        print(f"✓ 报告生成成功")
        print("报告摘要:")
        print(summary[:200] + "...")
    except Exception as e:
        print(f"✗ 报告生成失败: {e}")
        return False
    
    print("\n=== 所有基本功能测试通过! ===")
    return True

if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
