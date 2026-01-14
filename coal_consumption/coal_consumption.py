import math
from typing import Dict, Any, Tuple, List
from .correction_factors import CorrectionFactors

class CoalConsumptionCalculator:
    """
    煤耗计算核心类
    实现基准煤耗的计算逻辑
    """
    
    def __init__(self):
        self.correction_factors = CorrectionFactors()
    
    def calculate_basic_coal_consumption(self, electricity_output: float, coal_calorific_value: float,
                                        efficiency: float, pipeline_efficiency: float) -> float:
        """
        计算基本煤耗
        
        Args:
            electricity_output: 发电量(MWh)
            coal_calorific_value: 煤的发热量(kJ/kg)
            efficiency: 锅炉效率
            pipeline_efficiency: 管道效率
            
        Returns:
            基本煤耗(g/kWh)
        """
        if electricity_output == 0:
            return 0.0
        
        # 修正基本煤耗计算公式
        # 正确公式：煤耗 (g/kWh) = 3600 * 1000 / (煤的发热量 * 效率 * 管道效率)
        # 3600: 1kWh的能量(kJ)
        # 1000: 转换为g
        coal_consumption_g = (3600 * 1000) / (coal_calorific_value * efficiency * pipeline_efficiency)
        
        return coal_consumption_g
    
    def calculate_benchmark_coal_consumption(self, params: Dict[str, Any]) -> Dict[str, float]:
        """
        计算基准煤耗
        
        Args:
            params: 参数字典
            
        Returns:
            包含各种煤耗指标的字典
        """
        # 获取参数
        electricity_output = params.get('electricity_output', 1000.0)  # 发电量(MWh)
        coal_calorific_value = params.get('coal_calorific_value', 29306.0)  # 煤的发热量(kJ/kg)
        efficiency = params.get('efficiency', 0.9)  # 锅炉效率
        pipeline_efficiency = params.get('管道效率', 0.98)  # 管道效率
        
        # 计算修正因子
        corrections = self.correction_factors.calculate_comprehensive_correction(params)
        
        # 计算基本煤耗
        basic_coal_consumption = self.calculate_basic_coal_consumption(
            electricity_output, coal_calorific_value, efficiency, pipeline_efficiency
        )
        
        # 应用修正因子
        benchmark_coal_consumption = basic_coal_consumption * corrections['comprehensive']
        
        # 计算其他煤耗指标
        results = {
            'basic_coal_consumption': basic_coal_consumption,
            'benchmark_coal_consumption': benchmark_coal_consumption,
            'correction_factor': corrections['comprehensive'],
        }
        
        # 添加详细的修正因子
        results.update(corrections)
        
        return results
    
    def calculate_heating_impact(self, params: Dict[str, Any]) -> Dict[str, float]:
        """
        计算供热对煤耗的影响
        
        Args:
            params: 参数字典
            
        Returns:
            供热影响计算结果
        """
        # 获取参数
        electricity_output = params.get('electricity_output', 1000.0)  # 发电量(MWh)
        heating_output = params.get('heating_output', 500.0)  # 供热量(GJ)
        coal_calorific_value = params.get('coal_calorific_value', 29306.0)  # 煤的发热量(kJ/kg)
        efficiency = params.get('efficiency', 0.9)  # 锅炉效率
        pipeline_efficiency = params.get('管道效率', 0.98)  # 管道效率
        
        # 计算纯发电煤耗
        power_only_coal = self.calculate_basic_coal_consumption(
            electricity_output, coal_calorific_value, efficiency, pipeline_efficiency
        )
        
        if heating_output == 0:
            return {
                'heating_coal_consumption': 0.0,
                'combined_coal_consumption': power_only_coal,
                'heating_impact': 0.0,
            }
        
        # 供热煤耗计算 (kg)
        # 1GJ = 1000000kJ
        heating_coal = (heating_output * 1000000) / (coal_calorific_value * efficiency)
        
        # 发电煤耗 (kg)
        power_coal = power_only_coal * electricity_output / 1000  # g/kWh * MWh = kg
        
        # 综合煤耗计算（考虑热电联产的影响）
        # 供热会减少供电煤耗，因为部分热量用于供热
        total_coal = power_coal + heating_coal
        
        # 热电联产的供电煤耗计算
        # 供热会分摊部分煤耗，所以供电煤耗应该降低
        # 这里使用合理的热电分摊方法
        heat_to_power_ratio = heating_output / (electricity_output * 3.6)  # 热功率与电功率的比值
        
        # 基于热电比的煤耗修正
        combined_coal_consumption = power_only_coal * (1 - 0.4 * heat_to_power_ratio)
        
        # 确保结果在合理范围内
        combined_coal_consumption = max(80, min(200, combined_coal_consumption))
        
        results = {
            'heating_coal_consumption': heating_coal,
            'combined_coal_consumption': combined_coal_consumption,
            'heating_impact': combined_coal_consumption - power_only_coal,
        }
        
        return results
    
    def calculate_coal_consumption_by_operation_mode(self, params: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        计算不同运行工况下的煤耗
        
        Args:
            params: 参数字典
            
        Returns:
            不同工况下的煤耗计算结果
        """
        operation_modes = ['normal', 'peak', 'low', 'heating']
        results = {}
        
        for mode in operation_modes:
            mode_params = params.copy()
            mode_params['operation_mode'] = mode
            
            # 根据工况调整参数
            if mode == 'peak':
                mode_params['actual_load'] = params.get('base_load', 100) * 1.1
            elif mode == 'low':
                mode_params['actual_load'] = params.get('base_load', 100) * 0.5  # 降低到50%负荷
                mode_params['heating_load'] = 0  # 低谷工况不供热
            elif mode == 'heating':
                mode_params['actual_load'] = params.get('base_load', 100) * 0.8  # 供热时负荷率
                mode_params['heating_load'] = params.get('heating_load', 50) * 1.2
            
            # 计算煤耗
            mode_results = self.calculate_benchmark_coal_consumption(mode_params)
            results[mode] = mode_results
        
        return results
    
    def calculate_annual_coal_consumption(self, monthly_params: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算年度煤耗
        
        Args:
            monthly_params: 月度参数字典列表
            
        Returns:
            年度煤耗计算结果
        """
        annual_results = {
            'monthly_results': [],
            'annual_electricity_output': 0.0,
            'annual_coal_consumption': 0.0,
            'annual_benchmark_coal_consumption': 0.0,
        }
        
        total_electricity = 0.0
        total_coal = 0.0
        
        for i, params in enumerate(monthly_params):
            # 计算月度煤耗
            monthly_result = self.calculate_benchmark_coal_consumption(params)
            annual_results['monthly_results'].append(monthly_result)
            
            # 累计发电量和煤耗
            electricity = params.get('electricity_output', 0.0)
            total_electricity += electricity
            total_coal += monthly_result['benchmark_coal_consumption'] * electricity / 1000
        
        # 计算年度煤耗指标
        if total_electricity > 0:
            annual_benchmark_coal_consumption = (total_coal * 1000) / total_electricity
        else:
            annual_benchmark_coal_consumption = 0.0
        
        annual_results['annual_electricity_output'] = total_electricity
        annual_results['annual_coal_consumption'] = total_coal
        annual_results['annual_benchmark_coal_consumption'] = annual_benchmark_coal_consumption
        
        return annual_results
    
    def calculate_coal_consumption_with_heating(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算包含供热的综合煤耗
        
        Args:
            params: 参数字典
            
        Returns:
            综合煤耗计算结果
        """
        # 计算纯发电煤耗
        power_only_params = params.copy()
        power_only_params['heating_output'] = 0
        power_only_results = self.calculate_benchmark_coal_consumption(power_only_params)
        
        # 计算包含供热的煤耗
        heating_results = self.calculate_heating_impact(params)
        
        # 综合结果
        combined_results = {
            'power_only_coal_consumption': power_only_results['benchmark_coal_consumption'],
            'heating_coal_consumption': heating_results['heating_coal_consumption'],
            'combined_coal_consumption': heating_results['combined_coal_consumption'],
            'heating_impact': heating_results['heating_impact'],
            'heating_ratio': params.get('heating_output', 0) / (params.get('heating_output', 0) + params.get('electricity_output', 1)),
        }
        
        return combined_results
    
    def calculate_coal_consumption_sensitivity(self, params: Dict[str, Any], 
                                             variable: str, 
                                             min_value: float, 
                                             max_value: float, 
                                             steps: int = 10) -> List[Tuple[float, float]]:
        """
        计算煤耗对某一参数的敏感性
        
        Args:
            params: 参数字典
            variable: 变量名称
            min_value: 最小值
            max_value: 最大值
            steps: 步数
            
        Returns:
            (变量值, 煤耗值)的列表
        """
        sensitivity_results = []
        
        # 计算步长
        step_size = (max_value - min_value) / (steps - 1)
        
        # 计算不同变量值下的煤耗
        for i in range(steps):
            value = min_value + i * step_size
            test_params = params.copy()
            test_params[variable] = value
            
            # 计算煤耗
            result = self.calculate_benchmark_coal_consumption(test_params)
            sensitivity_results.append((value, result['benchmark_coal_consumption']))
        
        return sensitivity_results
