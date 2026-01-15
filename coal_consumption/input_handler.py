import pandas as pd
import openpyxl
from typing import Dict, List, Optional, Any
import os
from utils import load_parameters

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
            'coal_calorific_value': 4854.0,  # 煤的发热量(kcal/kg)
            
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
        }
        
        # 从config.json加载默认参数（已注释，使用硬编码）
        # self.default_parameters = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        从config.json加载配置参数
        
        Returns:
            配置参数字典
        """
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        
        try:
            if os.path.exists(config_path):
                config_data = load_parameters(config_path)
                # 提取default_parameters部分
                if 'default_parameters' in config_data:
                    # 过滤掉_note字段（只保留实际参数）
                    params = {}
                    for key, value in config_data['default_parameters'].items():
                        if not key.endswith('_note'):
                            params[key] = value
                    return params
        except Exception as e:
            print(f"警告: 从config.json加载配置失败，使用默认值: {e}")
        
        # 如果加载失败，返回后备默认参数
        return self.fallback_parameters.copy()
    
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
    
    def load_benchmark_and_monthly_data(self, file_path: str, sheet_name: str = '25年对比') -> Dict[str, Any]:
        """
        从Excel文件加载基准数据和各月份数据
        
        Args:
            file_path: Excel文件路径
            sheet_name: 工作表名称（默认"25年对比"）
            
        Returns:
            包含基准数据和各月份数据的字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel文件不存在: {file_path}")
        
        try:
            # 加载Excel文件
            wb = openpyxl.load_workbook(file_path, data_only=True)
            ws = wb[sheet_name]
            
            # 解析Excel结构
            # 列D: 基准数据
            # 列F-H: 1月数据
            # 列J-L: 2月数据
            # 每一行代表一个影响因素
            
            # 数据结构:
            # {
            #     'benchmark': {
            #         '海水温度': 19,
            #         '当地气温': 25,
            #         ...
            #     },
            #     'months': {
            #         '1月': {
            #             '海水温度': 6.15,
            #             '当地气温': 15,
            #             ...
            #         },
            #         '2月': {
            #             '海水温度': 4.998,
            #             '当地气温': 15,
            #             ...
            #         }
            #     }
            # }
            
            result = {
                'benchmark': {},
                'months': {}
            }
            
            # 影响因素映射
            factor_mapping = {
                4: '海水温度',  # 行4
                5: '当地气温',  # 行5
                6: '煤种热值',  # 行6
                7: '电煤水分',  # 行7
                8: '灰分',      # 行8
                9: '发电量',     # 行9
                11: '机组负荷率', # 行11
                16: '供电基准煤耗', # 行16
                17: '2#机组发电量', # 行17
                19: '2#机组负荷率', # 行19
                22: '2#机组供电基准煤耗' # 行22
            }
            
            # 基准数据列（D列，第4列）
            BENCHMARK_COL = 4
            
            # 月份数据列映射
            month_columns = {
                '1月': {'data': 6, 'factor': 7},  # 1月数据在F列(6)，影响系数在G列(7)
                '2月': {'data': 8, 'factor': 9},  # 2月数据在H列(8)，影响系数在I列(9)
                # 可根据需要添加更多月份
            }
            
            # 读取基准数据
            for row_num, factor_name in factor_mapping.items():
                cell = ws.cell(row=row_num, column=BENCHMARK_COL)
                if cell.value is not None:
                    # 跳过单位行（如发电量的"万KWh"）
                    if isinstance(cell.value, (int, float)):
                        result['benchmark'][factor_name] = cell.value
            
            # 读取各月份数据
            for month, columns in month_columns.items():
                result['months'][month] = {}
                for row_num, factor_name in factor_mapping.items():
                    data_cell = ws.cell(row=row_num, column=columns['data'])
                    if data_cell.value is not None and isinstance(data_cell.value, (int, float)):
                        result['months'][month][factor_name] = data_cell.value
                    
                    # 读取影响煤耗系数
                    factor_cell = ws.cell(row=row_num, column=columns['factor'])
                    if factor_cell.value is not None and isinstance(factor_cell.value, (int, float)):
                        result['months'][month][f'{factor_name}_影响系数'] = factor_cell.value
            
            return result
            
        except Exception as e:
            print(f"从Excel加载基准和月份数据时出错: {e}")
            raise
    
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
