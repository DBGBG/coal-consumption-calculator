"""
工具函数模块
"""

import json
from typing import Dict, Any, List


def save_parameters(params: Dict[str, Any], file_path: str) -> None:
    """
    保存参数到JSON文件
    
    Args:
        params: 参数字典
        file_path: 文件路径
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(params, f, ensure_ascii=False, indent=2)


def load_parameters(file_path: str) -> Dict[str, Any]:
    """
    从JSON文件加载参数
    
    Args:
        file_path: 文件路径
        
    Returns:
        参数字典
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_numeric(value: Any, min_value: float = None, max_value: float = None) -> float:
    """
    验证数值参数
    
    Args:
        value: 输入值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        验证后的数值
    """
    try:
        num_value = float(value)
        
        if min_value is not None:
            num_value = max(min_value, num_value)
        
        if max_value is not None:
            num_value = min(max_value, num_value)
        
        return num_value
    except (ValueError, TypeError):
        return 0.0


def format_number(value: float, decimals: int = 2) -> str:
    """
    格式化数字
    
    Args:
        value: 数值
        decimals: 小数位数
        
    Returns:
        格式化后的字符串
    """
    return f"{value:.{decimals}f}"


def calculate_average(values: List[float]) -> float:
    """
    计算平均值
    
    Args:
        values: 数值列表
        
    Returns:
        平均值
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def calculate_standard_deviation(values: List[float]) -> float:
    """
    计算标准差
    
    Args:
        values: 数值列表
        
    Returns:
        标准差
    """
    if len(values) <= 1:
        return 0.0
    
    mean = calculate_average(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5
