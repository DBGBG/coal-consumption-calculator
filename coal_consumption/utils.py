import json
import os
from typing import Dict, Any, List, Optional, Union


def load_parameters(file_path: str) -> Dict[str, Any]:
    """
    从JSON文件加载参数
    
    Args:
        file_path: 文件路径
        
    Returns:
        参数字典
    """
    if not os.path.exists(file_path):
        print(f"警告: 配置文件 {file_path} 不存在")
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError as e:
        print(f"错误: 配置文件 {file_path} 格式错误 - {e}")
        return {}
    except Exception as e:
        print(f"错误: 加载配置文件 {file_path} 时出错 - {e}")
        return {}


def save_parameters(params: Dict[str, Any], file_path: str) -> None:
    """
    保存参数到JSON文件
    
    Args:
        params: 参数字典
        file_path: 文件路径
    """
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(params, f, ensure_ascii=False, indent=2)
        print(f"参数已成功保存到 {file_path}")
    except Exception as e:
        print(f"错误: 保存参数到 {file_path} 时出错 - {e}")


def validate_numeric(value: Any, min_value: Optional[float] = None, max_value: Optional[float] = None) -> float:
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


def validate_positive(value: Any) -> float:
    """
    验证并返回正数
    
    Args:
        value: 输入值
        
    Returns:
        验证后的正数
    """
    try:
        num_value = float(value)
        return max(0.0001, num_value)  # 确保值为正数
    except (ValueError, TypeError):
        return 1.0


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


def extract_parameters_without_notes(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    从参数字典中提取实际参数，去除带有_note后缀的字段
    
    Args:
        data: 包含参数和备注的字典
        
    Returns:
        只包含实际参数的字典
    """
    params = {}
    for key, value in data.items():
        if not key.endswith('_note'):
            params[key] = value
    return params


def get_project_root() -> str:
    """
    获取项目根目录路径
    
    Returns:
        项目根目录路径
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def get_config_path() -> str:
    """
    获取配置文件路径
    
    Returns:
        配置文件路径
    """
    return os.path.join(get_project_root(), 'config.json')


def load_config() -> Dict[str, Any]:
    """
    加载配置文件
    
    Returns:
        配置字典
    """
    config_path = get_config_path()
    return load_parameters(config_path)


def get_default_parameters() -> Dict[str, Any]:
    """
    获取默认参数
    
    Returns:
        默认参数字典
    """
    config = load_config()
    default_params = config.get('default_parameters', {})
    return extract_parameters_without_notes(default_params)


def get_calculation_settings() -> Dict[str, Any]:
    """
    获取计算设置
    
    Returns:
        计算设置字典
    """
    config = load_config()
    return config.get('calculation_settings', {})


def get_output_settings() -> Dict[str, Any]:
    """
    获取输出设置
    
    Returns:
        输出设置字典
    """
    config = load_config()
    return config.get('output_settings', {})


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 当分母为0时的默认值
        
    Returns:
        除法结果
    """
    if denominator == 0:
        return default
    return numerator / denominator
