from typing import Dict, Any, Tuple, List
from correction_factors import CorrectionFactors
from utils import safe_divide, validate_positive, validate_numeric

class CoalConsumptionCalculator:
    """
    煤耗计算核心类
    实现基准煤耗的计算逻辑
    """
    
    def __init__(self):
        self.correction_factors = CorrectionFactors()
    
    def calculate_basic_coal_consumption(self, electricity_output: float, coal_calorific_value: float,
                                        efficiency: float) -> float:
        """
        计算基本煤耗
        
        Args:
            electricity_output: 发电量(MWh)
            coal_calorific_value: 煤的发热量(kcal/kg)
            efficiency: 锅炉效率
            
        Returns:
            基本煤耗(g/kWh)
        """
        # 验证参数有效性
        efficiency = validate_numeric(efficiency, 0.5, 1.0)
        coal_calorific_value = validate_numeric(coal_calorific_value, 1000, 8000)
        
        # 将kcal/kg转换为kJ/kg (1 kcal = 4.1868 kJ)
        coal_calorific_value_kj = coal_calorific_value * 4.1868
        
        if coal_calorific_value_kj <= 0:
            return 0.0
        
        # 基本煤耗计算公式：煤耗 (g/kWh) = 3600 * 1000 / (煤的发热量 * 效率)
        # 3600: 1kWh的能量(kJ)
        # 1000: 转换为g
        coal_consumption_g = (3600 * 1000) / (coal_calorific_value_kj * efficiency)
        
        # 确保结果在合理范围内
        return max(80, min(250, coal_consumption_g))
    
    def calculate_benchmark_coal_consumption(self, params: Dict[str, Any], calculation_settings: Dict[str, Any]) -> Dict[str, float]:
        """
        计算基准煤耗
        
        Args:
            params: 参数字典
            calculation_settings: 计算设置字典
            
        Returns:
            包含各种煤耗指标的字典
        """
        # 获取参数
        electricity_output = params.get('electricity_output', 1000.0)  # 发电量(MWh)
        coal_calorific_value = params.get('coal_calorific_value', 4854.0)  # 煤的发热量(kcal/kg)
        efficiency = params.get('efficiency', 0.9)  # 锅炉效率
        
        # 计算修正因子
        corrections = self.correction_factors.calculate_comprehensive_correction(params, calculation_settings)
        
        # 计算基本煤耗
        basic_coal_consumption = self.calculate_basic_coal_consumption(
            electricity_output, coal_calorific_value, efficiency
        )
        
        # 应用修正因子
        benchmark_coal_consumption = basic_coal_consumption * corrections['comprehensive']
        
        # 计算总系数（不包括供热修正）
        total_factor = 1.0
        for key, value in corrections.items():
            if key not in ['comprehensive', 'heating']:
                total_factor *= value
        
        # 计算其他煤耗指标
        results = {
            'basic_coal_consumption': basic_coal_consumption,
            'benchmark_coal_consumption': benchmark_coal_consumption,
            'correction_factor': corrections['comprehensive'],
            'total_correction_factor': total_factor,
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
        coal_calorific_value = params.get('coal_calorific_value', 4854.0)  # 煤的发热量(kcal/kg)
        efficiency = params.get('efficiency', 0.9)  # 锅炉效率
        
        # 计算纯发电煤耗
        power_only_coal = self.calculate_basic_coal_consumption(
            electricity_output, coal_calorific_value, efficiency
        )
        
        if heating_output == 0:
            return {
                'heating_coal_consumption': 0.0,
                'combined_coal_consumption': power_only_coal,
                'heating_impact': 0.0,
            }
        
        # 将kcal/kg转换为kJ/kg (1 kcal = 4.1868 kJ)
        coal_calorific_value_kj = coal_calorific_value * 4.1868
        
        # 供热煤耗计算 (kg)
        # 1GJ = 1000000kJ
        heating_coal = (heating_output * 1000000) / (coal_calorific_value_kj * efficiency)
        
        # 发电煤耗 (kg)
        power_coal = power_only_coal * electricity_output / 1000  # g/kWh * MWh = kg
        
        # 综合煤耗计算（考虑热电联产的影响）
        # 供热会减少供电煤耗，因为部分热量用于供热
        total_coal = power_coal + heating_coal
        
        # 热电联产的供电煤耗计算
        # 使用热电分摊方法计算综合煤耗
        heat_to_power_ratio = safe_divide(heating_output, electricity_output * 3.6, 0.0)  # 热功率与电功率的比值
        
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
    
    def calculate_coal_consumption_by_operation_mode(self, params: Dict[str, Any], calculation_settings: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """
        计算不同运行工况下的煤耗
        
        Args:
            params: 参数字典
            calculation_settings: 计算设置字典
            
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
                # 峰值工况 - 高负荷
                mode_params['actual_load'] = params.get('base_load', 100) * 1.1
                mode_params['heating_load'] = 0  # 峰值工况不供热
            elif mode == 'low':
                # 低谷工况 - 低负荷
                mode_params['actual_load'] = params.get('base_load', 100) * 0.5
                mode_params['heating_load'] = 0  # 低谷工况不供热
            elif mode == 'heating':
                # 供热工况
                mode_params['actual_load'] = params.get('base_load', 100) * 0.8
                mode_params['heating_load'] = params.get('heating_load', 50) * 1.2
            else:  # normal
                mode_params['actual_load'] = params.get('base_load', 100)
                mode_params['heating_load'] = params.get('heating_load', 0)
            
            # 计算煤耗
            mode_results = self.calculate_benchmark_coal_consumption(mode_params, calculation_settings)
            results[mode] = mode_results
        
        return results
    
    def calculate_annual_coal_consumption(self, monthly_params: List[Dict[str, Any]], calculation_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算年度煤耗
        
        Args:
            monthly_params: 月度参数字典列表
            calculation_settings: 计算设置字典
            
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
            monthly_result = self.calculate_benchmark_coal_consumption(params, calculation_settings)
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
    
    def calculate_coal_consumption_with_heating(self, params: Dict[str, Any], calculation_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算包含供热的综合煤耗
        
        Args:
            params: 参数字典
            calculation_settings: 计算设置字典
            
        Returns:
            综合煤耗计算结果
        """
        # 计算纯发电煤耗
        power_only_params = params.copy()
        power_only_params['heating_output'] = 0
        power_only_params['heating_load'] = 0
        power_only_results = self.calculate_benchmark_coal_consumption(power_only_params, calculation_settings)
        
        # 计算包含供热的煤耗
        heating_results = self.calculate_heating_impact(params)
        
        # 计算供热比例
        denominator = params.get('heating_output', 0) + params.get('electricity_output', 1) * 3.6
        heating_ratio = safe_divide(params.get('heating_output', 0), denominator, 0.0)
        
        # 综合结果
        combined_results = {
            'power_only_coal_consumption': power_only_results['benchmark_coal_consumption'],
            'heating_coal_consumption': heating_results['heating_coal_consumption'],
            'combined_coal_consumption': heating_results['combined_coal_consumption'],
            'heating_impact': heating_results['heating_impact'],
            'heating_ratio': heating_ratio,
        }
        
        return combined_results
    
    def calculate_coal_consumption_sensitivity(self, params: Dict[str, Any], calculation_settings: Dict[str, Any],
                                             variable: str, 
                                             min_value: float, 
                                             max_value: float, 
                                             steps: int = 10) -> List[Tuple[float, float]]:
        """
        计算煤耗对某一参数的敏感性
        
        Args:
            params: 参数字典
            calculation_settings: 计算设置字典
            variable: 变量名称
            min_value: 最小值
            max_value: 最大值
            steps: 步数
            
        Returns:
            (变量值, 煤耗值)的列表
        """
        sensitivity_results = []
        
        if steps < 2:
            steps = 2
        
        # 计算步长
        step_size = safe_divide(max_value - min_value, steps - 1, 0.0)
        
        # 计算不同变量值下的煤耗
        for i in range(steps):
            value = min_value + i * step_size
            test_params = params.copy()
            test_params[variable] = value
            
            # 计算煤耗
            result = self.calculate_benchmark_coal_consumption(test_params, calculation_settings)
            sensitivity_results.append((value, result['benchmark_coal_consumption']))
        
        return sensitivity_results
    
    def calculate_comparison_with_benchmark(self, benchmark_data: Dict[str, float], 
                                          monthly_data: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        计算各月份数据与基准数据的对比
        
        Args:
            benchmark_data: 基准数据字典
            monthly_data: 各月份数据字典，键为月份名称，值为该月份的数据
            
        Returns:
            对比结果字典
        """
        comparison_results = {
            'benchmark': benchmark_data,
            'monthly_comparisons': {}
        }
        
        # 对每个月份进行对比
        for month_name, month_data in monthly_data.items():
            month_comparison = {
                'monthly_data': month_data,
                'comparisons': {}
            }
            
            # 计算各参数与基准的差异和比例
            for param_name in set(benchmark_data.keys()) & set(month_data.keys()):
                benchmark_value = benchmark_data[param_name]
                month_value = month_data[param_name]
                
                # 跳过为0的基准值（避免除以0）
                if benchmark_value == 0:
                    continue
                
                # 计算差异和比例
                difference = month_value - benchmark_value
                ratio = safe_divide(month_value, benchmark_value, 1.0)
                
                month_comparison['comparisons'][param_name] = {
                    'benchmark': benchmark_value,
                    'monthly': month_value,
                    'difference': difference,
                    'ratio': ratio
                }
            
            comparison_results['monthly_comparisons'][month_name] = month_comparison
        
        return comparison_results
    
    def calculate_coal_consumption_for_monthly_data(self, benchmark_data: Dict[str, float], 
                                                  monthly_data: Dict[str, Dict[str, float]],
                                                  calculation_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于基准数据和月份数据计算煤耗
        
        Args:
            benchmark_data: 基准数据字典
            monthly_data: 各月份数据字典
            calculation_settings: 计算设置字典
            
        Returns:
            计算结果字典
        """
        results = {
            'benchmark_coal_consumption': 0.0,
            'monthly_coal_consumption': {}
        }
        
        # 计算基准煤耗
        benchmark_params = {
            'base_load': benchmark_data.get('机组负荷率', 100),
            'base_temperature': benchmark_data.get('当地气温', 25),
            'base_sea_temperature': benchmark_data.get('海水温度', 19),
            'coal_calorific_value': benchmark_data.get('煤种热值', 4854),
            'base_pressure': 16.7,  # 默认值
            'actual_load': benchmark_data.get('机组负荷率', 100),
            'actual_temperature': benchmark_data.get('当地气温', 25),
            'actual_sea_temperature': benchmark_data.get('海水温度', 19),
            'actual_calorific_value': benchmark_data.get('煤种热值', 4854),
            'efficiency': 0.9,
            'electricity_output': benchmark_data.get('发电量', 1000)
        }
        
        benchmark_results = self.calculate_benchmark_coal_consumption(benchmark_params, calculation_settings)
        results['benchmark_coal_consumption'] = benchmark_results['benchmark_coal_consumption']
        
        # 计算各月份的煤耗
        for month_name, month_data in monthly_data.items():
            month_params = {
                'base_load': benchmark_data.get('机组负荷率', 100),
                'base_temperature': benchmark_data.get('当地气温', 25),
                'base_sea_temperature': benchmark_data.get('海水温度', 19),
                'coal_calorific_value': benchmark_data.get('煤种热值', 4854),
                'base_pressure': 16.7,  # 默认值
                'actual_load': month_data.get('机组负荷率', benchmark_data.get('机组负荷率', 100)),
                'actual_temperature': month_data.get('当地气温', benchmark_data.get('当地气温', 25)),
                'actual_sea_temperature': month_data.get('海水温度', benchmark_data.get('海水温度', 19)),
                'actual_calorific_value': month_data.get('煤种热值', benchmark_data.get('煤种热值', 4854)),
                'efficiency': 0.9,
                'electricity_output': month_data.get('发电量', 1000)
            }
            
            month_results = self.calculate_benchmark_coal_consumption(month_params, calculation_settings)
            results['monthly_coal_consumption'][month_name] = month_results['benchmark_coal_consumption']
        
        return results
