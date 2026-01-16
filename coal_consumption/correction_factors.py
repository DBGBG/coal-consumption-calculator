import math
from typing import Dict, Any
from utils import safe_divide, validate_numeric

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
        # 使用安全除法，避免除以0
        load_ratio = safe_divide(actual_load, base_load, 1.0)
        
        # 负荷率修正模型 - 基于实际发电运行经验
        if load_ratio < 0.3:
            # 低负荷区域，效率显著下降
            correction_factor = 1.4 - 0.6 * load_ratio
        elif load_ratio < 0.5:
            correction_factor = 1.25 - 0.4 * load_ratio
        elif load_ratio < 0.7:
            correction_factor = 1.15 - 0.2 * load_ratio
        elif load_ratio < 1.0:
            correction_factor = 1.0
        elif load_ratio < 1.1:
            # 超额定负荷区域，效率略有下降
            correction_factor = 1.0 + 0.05 * (load_ratio - 1.0)
        else:
            correction_factor = 1.1 + 0.1 * (load_ratio - 1.1)
        
        # 确保修正因子在合理范围内
        return max(0.8, min(1.5, correction_factor))
    
    def calculate_temperature_correction(self, actual_temp: float, base_temp: float) -> float:
        """
        计算温度修正因子
        
        Args:
            actual_temp: 实际温度(℃)
            base_temp: 基准温度(℃)
            
        Returns:
            温度修正因子
        """
        # 温度每变化1℃，煤耗变化约0.2%
        temp_diff = actual_temp - base_temp
        correction_factor = 1 + 0.002 * temp_diff
        
        # 确保修正因子在合理范围内
        return max(0.95, min(1.05, correction_factor))
    
    def calculate_pressure_correction(self, actual_pressure: float, base_pressure: float) -> float:
        """
        计算压力修正因子
        
        Args:
            actual_pressure: 实际压力(MPa)
            base_pressure: 基准压力(MPa)
            
        Returns:
            压力修正因子
        """
        # 压力修正公式 - 基于超临界机组运行经验
        pressure_ratio = safe_divide(actual_pressure, base_pressure, 1.0)
        correction_factor = 1 + 2.3 * (pressure_ratio - 1.0)
        
        # 确保修正因子在合理范围内
        return max(0.98, min(1.02, correction_factor))
    
    def calculate_humidity_correction(self, actual_humidity: float, base_humidity: float) -> float:
        """
        计算湿度修正因子
        
        Args:
            actual_humidity: 实际湿度(%)
            base_humidity: 基准湿度(%)
            
        Returns:
            湿度修正因子
        """
        # 湿度每变化10%，煤耗变化约0.1%
        humidity_diff = actual_humidity - base_humidity
        correction_factor = 1 + 0.0001 * humidity_diff
        
        # 确保修正因子在合理范围内
        return max(0.99, min(1.01, correction_factor))
    
    def calculate_heating_correction(self, heating_load: float, total_load: float) -> float:
        """
        计算供热修正因子
        
        Args:
            heating_load: 供热负荷率(%)
            total_load: 总负荷率(%)
            
        Returns:
            供热修正因子
        """
        if total_load <= 0 or heating_load <= 0:
            return 1.0
        
        # 供热比例
        heating_ratio = safe_divide(heating_load, total_load, 0.0)
        
        # 供热会减少供电煤耗，因为部分热量用于供热而非发电
        correction_factor = 1.0 - 0.3 * heating_ratio
        
        # 确保修正因子在合理范围内
        return max(0.7, min(1.0, correction_factor))
    
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
        # 温度修正 - 温度每变化10℃，煤耗变化约0.5%
        temp_diff = actual_steam_temp - base_steam_temp
        temp_correction = 1 + 0.0005 * temp_diff
        
        # 压力修正
        pressure_ratio = safe_divide(actual_steam_pressure, base_steam_pressure, 1.0)
        pressure_correction = 1 + 0.002 * (pressure_ratio - 1.0)
        
        # 综合蒸汽参数修正因子
        correction_factor = temp_correction * pressure_correction
        
        # 确保修正因子在合理范围内
        return max(0.97, min(1.03, correction_factor))
    
    def calculate_fuel_correction(self, actual_calorific_value: float, base_calorific_value: float) -> float:
        """
        计算燃料修正因子
        
        Args:
            actual_calorific_value: 实际燃料发热量(kcal/kg)
            base_calorific_value: 基准燃料发热量(kcal/kg)
            
        Returns:
            燃料修正因子
        """
        # 发热量越高，煤耗越低
        correction_factor = safe_divide(base_calorific_value, actual_calorific_value, 1.0)
        
        # 确保修正因子在合理范围内
        return max(0.8, min(1.2, correction_factor))
    
    def calculate_sea_temperature_correction(self, actual_sea_temp: float, base_sea_temp: float) -> float:
        """
        计算海水温度修正因子
        
        Args:
            actual_sea_temp: 实际海水温度(℃)
            base_sea_temp: 基准海水温度(℃)
            
        Returns:
            海水温度修正因子
        """
        # 海水温度每变化1℃，煤耗变化约0.15%
        sea_temp_diff = actual_sea_temp - base_sea_temp
        correction_factor = 1 + 0.0015 * sea_temp_diff
        
        # 确保修正因子在合理范围内
        return max(0.98, min(1.02, correction_factor))
    
    def calculate_comprehensive_correction(self, params: Dict[str, Any], calculation_settings: Dict[str, Any]) -> Dict[str, float]:
        """
        计算综合修正因子
        
        Args:
            params: 参数字典
            calculation_settings: 计算设置字典
            
        Returns:
            包含各种修正因子的字典
        """
        corrections = {
            'load_factor': 1.0,
            'temperature': 1.0,
            'pressure': 1.0,
            'humidity': 1.0,
            'heating': 1.0,
            'steam_parameter': 1.0,
            'fuel': 1.0,
            'sea_temperature': 1.0
        }
        
        # 根据计算设置决定是否启用各种修正因子
        if calculation_settings.get('enable_temperature_correction', True):
            corrections['temperature'] = self.calculate_temperature_correction(
                params.get('actual_temperature', params.get('base_temperature', 25)),
                params.get('base_temperature', 25)
            )
        
        if calculation_settings.get('enable_pressure_correction', True):
            corrections['pressure'] = self.calculate_pressure_correction(
                params.get('actual_pressure', params.get('base_pressure', 16.7)),
                params.get('base_pressure', 16.7)
            )
        
        if calculation_settings.get('enable_humidity_correction', True):
            corrections['humidity'] = self.calculate_humidity_correction(
                params.get('actual_humidity', params.get('base_humidity', 60)),
                params.get('base_humidity', 60)
            )
        
        if calculation_settings.get('enable_heating_correction', True):
            corrections['heating'] = self.calculate_heating_correction(
                params.get('heating_load', 0),
                params.get('total_load', params.get('base_load', 100))
            )
        
        if calculation_settings.get('enable_steam_parameter_correction', True):
            corrections['steam_parameter'] = self.calculate_steam_parameter_correction(
                params.get('actual_steam_temp', 540),
                params.get('actual_steam_pressure', params.get('base_pressure', 16.7)),
                params.get('base_steam_temp', 540),
                params.get('base_steam_pressure', params.get('base_pressure', 16.7))
            )
        
        if calculation_settings.get('enable_fuel_correction', True):
            corrections['fuel'] = self.calculate_fuel_correction(
                params.get('actual_calorific_value', params.get('coal_calorific_value', 4854)),
                params.get('coal_calorific_value', 4854)
            )
        
        # 海水温度修正
        if calculation_settings.get('enable_sea_temperature_correction', False) and 'base_sea_temperature' in params:
            corrections['sea_temperature'] = self.calculate_sea_temperature_correction(
                params.get('actual_sea_temperature', params.get('base_sea_temperature', 19)),
                params.get('base_sea_temperature', 19)
            )
        
        # 负荷率修正总是启用
        corrections['load_factor'] = self.calculate_load_factor_correction(
            params.get('actual_load', params.get('base_load', 100)),
            params.get('base_load', 100)
        )
        
        # 计算综合修正因子
        comprehensive_correction = 1.0
        for key, value in corrections.items():
            if key != 'comprehensive':  # 避免重复计算
                comprehensive_correction *= value
        
        # 确保综合修正因子在合理范围内
        comprehensive_correction = max(0.7, min(1.3, comprehensive_correction))
        
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
        try:
            # 使用安全除法
            value_div_c = safe_divide(value, c, 0.0)
            correction = a + b * (1 - math.exp(-value_div_c))
            return correction
        except OverflowError:
            # 处理指数计算溢出
            return a + b
        except Exception:
            # 处理其他可能的错误
            return a + b
