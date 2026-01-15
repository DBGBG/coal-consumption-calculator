import math
from typing import Dict, Any

class CorrectionFactors:
    """
    修正因子计算类
    实现各种煤耗修正因子的计算
    """
    
    def calculate_load_factor_correction(self, actual_load: float, base_load: float) -> float:
        """
        计算负荷率修正因子
        
        Args:
            actual_load: 实际负荷率(%)
            base_load: 基准负荷率(%)
            
        Returns:
            负荷率修正因子
        """
        # 修正负荷率修正因子计算
        # 负荷率修正因子应反映不同负荷下的效率变化
        load_ratio = actual_load / base_load
        
        # 负荷率修正模型
        # 负荷率低于70%时，煤耗会显著增加
        # 负荷率高于100%时，煤耗也会增加
        if load_ratio < 0.3:
            correction_factor = 1.5
        elif load_ratio < 0.5:
            correction_factor = 1.3
        elif load_ratio < 0.7:
            correction_factor = 1.15
        elif load_ratio < 1.0:
            correction_factor = 1.0
        elif load_ratio < 1.1:
            correction_factor = 1.05
        else:
            correction_factor = 1.15
        
        return correction_factor
    
    def calculate_temperature_correction(self, actual_temp: float, base_temp: float) -> float:
        """
        计算温度修正因子
        
        Args:
            actual_temp: 实际温度(℃)
            base_temp: 基准温度(℃)
            
        Returns:
            温度修正因子
        """
        # 基于Excel中的线性模型
        # 公式: =1+0.002*(actual_temp - base_temp)
        
        correction_factor = 1 + 0.002 * (actual_temp - base_temp)
        
        return correction_factor
    
    def calculate_pressure_correction(self, actual_pressure: float, base_pressure: float) -> float:
        """
        计算压力修正因子
        
        Args:
            actual_pressure: 实际压力(MPa)
            base_pressure: 基准压力(MPa)
            
        Returns:
            压力修正因子
        """
        # 基于Excel中的公式
        # 公式: =1+2.3*(actual_pressure - base_pressure)/base_pressure
        
        if base_pressure == 0:
            return 1.0
        
        correction_factor = 1 + 2.3 * (actual_pressure - base_pressure) / base_pressure
        
        return correction_factor
    
    def calculate_humidity_correction(self, actual_humidity: float, base_humidity: float) -> float:
        """
        计算湿度修正因子
        
        Args:
            actual_humidity: 实际湿度(%).
            base_humidity: 基准湿度(%).
            
        Returns:
            湿度修正因子
        """
        # 基于Excel中的公式
        # 简化模型
        correction_factor = 1 + 0.0001 * (actual_humidity - base_humidity)
        
        return correction_factor
    
    def calculate_heating_correction(self, heating_load: float, total_load: float) -> float:
        """
        计算供热修正因子
        """
        if total_load == 0:
            return 1.0
        
        # 修正供热修正因子的计算逻辑
        if heating_load == 0:
            return 1.0
        
        # 合理的供热修正因子范围应该在 0.8-1.2 之间
        heating_ratio = heating_load / total_load
        correction_factor = 1.0 - 0.2 * heating_ratio  # 简单的线性修正
        
        return max(0.8, min(1.2, correction_factor))
    
    def calculate_steam_parameter_correction(self, actual_steam_temp: float, actual_steam_pressure: float,
                                           base_steam_temp: float, base_steam_pressure: float) -> float:
        """
        计算蒸汽参数修正因子
        
        Args:
            actual_steam_temp: 实际蒸汽温度(℃)
            actual_steam_pressure: 实际蒸汽压力(MPa)
            base_steam_temp: 基准蒸汽温度(℃)
            base_steam_pressure: 基准蒸汽压力(MPa)
            
        Returns:
            蒸汽参数修正因子
        """
        # 温度修正
        temp_correction = 1 + 0.0001 * (actual_steam_temp - base_steam_temp)
        
        # 压力修正
        if base_steam_pressure == 0:
            pressure_correction = 1.0
        else:
            pressure_correction = 1 + 0.0002 * (actual_steam_pressure - base_steam_pressure)
        
        correction_factor = temp_correction * pressure_correction
        
        return correction_factor
    
    def calculate_fuel_correction(self, actual_calorific_value: float, base_calorific_value: float) -> float:
        """
        计算燃料修正因子
        
        Args:
            actual_calorific_value: 实际燃料发热量(kcal/kg)
            base_calorific_value: 基准燃料发热量(kcal/kg)
            
        Returns:
            燃料修正因子
        """
        if base_calorific_value == 0:
            return 1.0
        
        # 将kcal/kg转换为kJ/kg (1 kcal = 4.1868 kJ)
        actual_calorific_value_kj = actual_calorific_value * 4.1868
        base_calorific_value_kj = base_calorific_value * 4.1868
        
        correction_factor = base_calorific_value_kj / actual_calorific_value_kj
        
        return correction_factor
    
    def calculate_comprehensive_correction(self, params: Dict[str, Any]) -> Dict[str, float]:
        """
        计算综合修正因子
        
        Args:
            params: 参数字典
            
        Returns:
            包含各种修正因子的字典
        """
        corrections = {}
        
        # 负荷率修正
        corrections['load_factor'] = self.calculate_load_factor_correction(
            params.get('actual_load', params.get('base_load', 100)),
            params.get('base_load', 100)
        )
        
        # 温度修正
        corrections['temperature'] = self.calculate_temperature_correction(
            params.get('actual_temperature', params.get('base_temperature', 25)),
            params.get('base_temperature', 25)
        )
        
        # 压力修正
        corrections['pressure'] = self.calculate_pressure_correction(
            params.get('actual_pressure', params.get('base_pressure', 16.7)),
            params.get('base_pressure', 16.7)
        )
        
        # 湿度修正
        corrections['humidity'] = self.calculate_humidity_correction(
            params.get('actual_humidity', params.get('base_humidity', 60)),
            params.get('base_humidity', 60)
        )
        
        # 供热修正
        corrections['heating'] = self.calculate_heating_correction(
            params.get('heating_load', 0),
            params.get('total_load', params.get('base_load', 100))
        )
        
        # 蒸汽参数修正
        corrections['steam_parameter'] = self.calculate_steam_parameter_correction(
            params.get('actual_steam_temp', 540),
            params.get('actual_steam_pressure', params.get('base_pressure', 16.7)),
            params.get('base_steam_temp', 540),
            params.get('base_steam_pressure', params.get('base_pressure', 16.7))
        )
        
        # 燃料修正
        corrections['fuel'] = self.calculate_fuel_correction(
            params.get('actual_calorific_value', params.get('coal_calorific_value', 29306)),
            params.get('coal_calorific_value', 29306)
        )
        
        # 计算综合修正因子
        comprehensive_correction = 1.0
        
        # 对每个修正因子进行合理性检查
        for key, value in corrections.items():
            # 确保修正因子在合理范围内
            if key != 'heating':  # 供热修正因子已经单独处理
                value = max(0.9, min(1.1, value))
            comprehensive_correction *= value
        
        # 确保综合修正因子在合理范围内
        comprehensive_correction = max(0.8, min(1.2, comprehensive_correction))
        
        corrections['comprehensive'] = comprehensive_correction
        
        return corrections
    
    def calculate_exponential_correction(self, value: float, a: float, b: float, c: float) -> float:
        """
        计算指数函数修正因子
        
        Args:
            value: 输入值
            a: 常数项
            b: 系数1
            c: 系数2
            
        Returns:
            指数修正因子
        """
        # 基于Excel中的指数函数模型
        # 公式: =a + b*(1-EXP(-value/c))
        
        correction = a + b * (1 - math.exp(-value / c))
        
        return correction
