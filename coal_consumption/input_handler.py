import pandas as pd
import openpyxl
from typing import Dict, List, Optional, Any
import os

class InputHandler:
    """
    数据输入处理类
    负责处理用户输入的数据和从Excel文件导入的数据
    """
    
    def __init__(self):
        # 默认参数值
        self.default_parameters = {
            # 基本参数
            'base_load': 100.0,  # 机组负荷率(%)
            'base_temperature': 25.0,  # 当地气温(℃)
            'base_sea_temperature': 19.0,  # 海水温度(℃)
            'base_pressure': 16.7,  # 基准压力(MPa)
            'base_humidity': 60.0,  # 基准湿度(%)
            'coal_calorific_value': 20317.0,  # 煤的发热量(kJ/kg) - 4854 kcal/kg * 4.1868
            
            # 煤质参数
            'coal_moisture': 8.6,  # 电煤水分(%)
            'coal_ash': 28.54,  # 灰分(%)
            
            # 供热参数
            'heating_time': 24.0,  # 供热时间(h)
            'heating_load': 50.0,  # 供热负荷率(%)
            
            # 工况参数
            'operation_mode': 'normal',  # 运行工况
            'time_period': 'annual',  # 时间周期
            
            # 其他参数
            'efficiency': 0.9,  # 锅炉效率
            '管道效率': 0.98,  # 管道效率
        }
    
    def get_user_input(self, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取用户输入的参数
        
        Args:
            parameters: 可选的参数字典，如果提供则使用这些参数
            
        Returns:
            完整的参数字典
        """
        if parameters is None:
            parameters = {}
        
        # 合并默认参数和用户输入参数
        input_params = self.default_parameters.copy()
        input_params.update(parameters)
        
        return input_params
    
    def load_from_excel(self, file_path: str, sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """
        从Excel文件加载参数
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称
            
        Returns:
            参数字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel文件不存在: {file_path}")
        
        try:
            # 加载Excel文件
            wb = openpyxl.load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            
            # 读取参数
            params = {}
            
            # 假设参数存储在A列和B列
            for row in range(1, ws.max_row + 1):
                key_cell = ws.cell(row=row, column=1)
                value_cell = ws.cell(row=row, column=2)
                
                if key_cell.value and value_cell.value:
                    params[key_cell.value] = value_cell.value
            
            # 合并默认参数
            input_params = self.default_parameters.copy()
            input_params.update(params)
            
            return input_params
            
        except Exception as e:
            print(f"从Excel加载参数时出错: {e}")
            return self.default_parameters
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证参数的有效性
        
        Args:
            parameters: 参数字典
            
        Returns:
            验证后的参数字典
        """
        # 验证负荷率
        if 'base_load' in parameters:
            parameters['base_load'] = max(0, min(100, parameters['base_load']))
        
        # 验证温度
        if 'base_temperature' in parameters:
            parameters['base_temperature'] = max(-40, min(80, parameters['base_temperature']))
        
        # 验证压力
        if 'base_pressure' in parameters:
            parameters['base_pressure'] = max(0, parameters['base_pressure'])
        
        # 验证湿度
        if 'base_humidity' in parameters:
            parameters['base_humidity'] = max(0, min(100, parameters['base_humidity']))
        
        # 验证效率
        if 'efficiency' in parameters:
            parameters['efficiency'] = max(0, min(1, parameters['efficiency']))
        
        if '管道效率' in parameters:
            parameters['管道效率'] = max(0, min(1, parameters['管道效率']))
        
        return parameters
    
    def get_parameters_for_calculation(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取用于计算的参数
        
        Args:
            user_input: 用户输入的参数
            
        Returns:
            用于计算的参数字典
        """
        # 验证参数
        validated_params = self.validate_parameters(user_input)
        
        # 添加计算所需的衍生参数
        calculation_params = validated_params.copy()
        
        # 计算一些衍生参数
        calculation_params['heat_value_MJ'] = calculation_params['coal_calorific_value'] / 1000.0
        
        return calculation_params
