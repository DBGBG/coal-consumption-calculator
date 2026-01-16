"""
燃煤发电基准煤耗计算程序
主程序入口
"""

def calculate_basic_coal_consumption(electricity_output, coal_calorific_value, efficiency):
    """
    计算基本煤耗
    
    Args:
        electricity_output: 发电量(MWh)
        coal_calorific_value: 煤的发热量(kcal/kg)
        efficiency: 锅炉效率
        
    Returns:
        基本煤耗(g/kWh)
    """
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

def main():
    """
    主函数
    """
    print("=== 燃煤发电基准煤耗计算程序 ===")
    print()
    
    # 年度基准数据
    annual_benchmark = {
        # 自然条件
        'sea_temperature': 19.0,         # 海水温度(℃)
        'local_temperature': 25.0,        # 当地气温(℃)
        
        # 煤种参数
        'coal_calorific_value': 4854.0,   # 热值(kcal/kg)
        'coal_moisture': 8.6,             # 电煤水分(%)
        'coal_ash': 28.54,                # 灰分(%)
        
        # 运行参数
        'electricity_output': 1000.0,     # 发电量(MWh)
        'efficiency': 0.9                 # 锅炉效率
    }
    
    print("年度基准数据:")
    print("自然条件:")
    print(f"  海水温度: {annual_benchmark['sea_temperature']} ℃")
    print(f"  当地气温: {annual_benchmark['local_temperature']} ℃")
    print("煤种参数:")
    print(f"  热值: {annual_benchmark['coal_calorific_value']} kcal/kg")
    print(f"  电煤水分: {annual_benchmark['coal_moisture']} %")
    print(f"  灰分: {annual_benchmark['coal_ash']} %")
    print("运行参数:")
    print(f"  发电量: {annual_benchmark['electricity_output']} MWh")
    print(f"  锅炉效率: {annual_benchmark['efficiency']}")
    print()
    
    # 计算基本煤耗
    print("计算基本煤耗...")
    basic_coal_consumption = calculate_basic_coal_consumption(
        annual_benchmark['electricity_output'],
        annual_benchmark['coal_calorific_value'],
        annual_benchmark['efficiency']
    )
    
    print(f"基本煤耗: {basic_coal_consumption:.2f} g/kWh")
    print()
    
    print("=== 计算完成 ===")

if __name__ == "__main__":
    main()
