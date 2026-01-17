"""
燃煤发电基准煤耗计算程序
主程序入口
"""
import math

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

def calculate_monthly_basic_coal_consumption(total_coal_consumption_coefficient, unit_electricity_output):
    """
    计算月度基本煤耗
    Args:
        total_coal_consumption_coefficient: 总煤耗影响系数
        unit_electricity_output: 机组发电量(MWh)
    Returns:
        月度基本煤耗(g/kWh)
    """
    if unit_electricity_output <= 0:
        return 0.0
    
    # 月度基本煤耗计算公式
    monthly_coal_consumption = (
        339 * total_coal_consumption_coefficient + 
        600 * 100 / unit_electricity_output + 
        100 * 100 / unit_electricity_output
    )
    
    # 返回计算结果
    return monthly_coal_consumption
# 1号机供热影响系数计算公式
def calculate_heat_energy_coefficient(heating_days, low_pressure_steam_days, medium_pressure_steam_days, unit_electricity_output, power_supply_benchmark):
    """
    计算供热影响系数
    Args:
        heating_days: 供热影响供暖日(天)
        low_pressure_steam_days: 供热影响低压供汽（日）(天)
        medium_pressure_steam_days: 供热影响中压供汽（日）(天)
        unit_electricity_output: 机组发电量(MWh)
        power_supply_benchmark: 供电基准煤耗(g/kWh)
    Returns:
        供热影响系数
    """
    # 检查关键参数是否为0
    if unit_electricity_output <= 0 or power_supply_benchmark <= 0:
        return 1.0
    
    # 检查供热天数是否为0
    if heating_days <= 0:
        return 1.0
    
    # 计算供热相关参数
    try:
        # 计算分子部分
        heat_energy = (
            medium_pressure_steam_days * 3.257 * heating_days +
            heating_days * heating_days +
            low_pressure_steam_days * 3 * heating_days
        )
        
        # 计算分母部分
        denominator = (
            unit_electricity_output * power_supply_benchmark * 10 +
            heat_energy * 38
        )
        
        # 避免除零错误
        if denominator <= 0:
            return 1.0
        
        # 计算第一部分
        part1 = 1 - (heat_energy * 38 / denominator)
        
        # 计算第二部分，避免除零错误
        part2_1 = 0.0
        part2_2 = 0.0
        part2_3 = 0.0
        
        # 计算第一部分
        if unit_electricity_output > 0 and heating_days > 0:
            part2_1 = 0.256 * heating_days / (unit_electricity_output / heating_days) / 10 / 3.6
        
        # 计算第二部分
        if unit_electricity_output > 0 and heating_days > 0:
            part2_2 = 0.383 * low_pressure_steam_days / (unit_electricity_output / heating_days) / 10 / 3.6
        
        # 计算第三部分
        if unit_electricity_output > 0:
            part2_3 = 0.383 * medium_pressure_steam_days * 3.25 * heating_days / unit_electricity_output / 10 / 3.6
        
        part2 = 1 + part2_1 + part2_2 + part2_3
        
        # 计算总供热影响系数
        heat_energy_coefficient = part1 * part2
        
        # 确保结果在合理范围内
        return max(0.8, min(1.2, heat_energy_coefficient))
    
    except Exception as e:
        # 如果计算过程中出现任何错误，返回默认值1.0
        print(f"计算供热影响系数时出错: {e}")
        return 1.0

def calculate_unit_2_heat_energy_coefficient(heating_days, generation_days, unit_electricity_output, power_supply_benchmark):
    """
    计算2号机组供热影响系数
    Args:
        heating_days: 供热影响供暖日(GJ)
        generation_days: 发电天数(天)
        unit_electricity_output: 机组发电量(MWh)
        power_supply_benchmark: 供电基准煤耗(g/kWh)
    Returns:
        2号机组供热影响系数
    """
    # 检查关键参数是否为0
    if unit_electricity_output <= 0 or power_supply_benchmark <= 0:
        return 1.0
    
    # 检查供热天数和发电天数是否为0
    if heating_days <= 0 or generation_days <= 0:
        return 1.0
    
    # 计算供热影响系数
    try:
        # 计算第一部分的分子和分母
        part1_numerator = heating_days * generation_days * 40
        part1_denominator = (
            heating_days * generation_days * 40 + 
            unit_electricity_output * power_supply_benchmark * 10
        )
        
        # 避免除零错误
        if part1_denominator <= 0:
            return 1.0
        
        # 计算第一部分
        part1 = 1 - (part1_numerator / part1_denominator)
        
        # 计算第二部分的分母
        part2_denominator = unit_electricity_output / generation_days
        
        # 避免除零错误
        if part2_denominator <= 0:
            return 1.0
        
        # 计算第二部分
        part2 = 1 + 0.256 * heating_days / part2_denominator / 10 / 3.6
        
        # 计算总供热影响系数
        heat_energy_coefficient = part1 * part2
        
        # 确保结果在合理范围内
        return max(0.8, min(1.2, heat_energy_coefficient))
    
    except Exception as e:
        # 如果计算过程中出现任何错误，返回默认值1.0
        print(f"计算2号机组供热影响系数时出错: {e}")
        return 1.0

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
        'efficiency': 0.9                 # 锅炉效率
    }
    # 月度实际数据
    mon_benchmark = {
        
        # 1月数据
        '1月': {
            # 自然条件
            'sea_temperature': 6.15,         # 海水温度(℃)
            'local_temperature': 15,        # 当地气温(℃)

            # 煤种参数
            'coal_calorific_value': 5133.9,   # 热值(kcal/kg)
            'coal_moisture': 12,             # 电煤水分(%)

            # 1号机组发电量
            'unit_1_electricity_output': 11839.08,             # 1号机组发电量(MWh)
            # 2号机组发电量
            'unit_2_electricity_output': 19357.404,             # 2号机组发电量(MWh)
            # 1号发电天数
            'unit_1_generation_days': 25.16,                          # 1号发电天数(天)
            # 2号发电天数
            'unit_2_generation_days': 31,                          # 2号发电天数(天)
            # 1号供电基准煤耗
            'unit_1_power_supply_benchmark_coal_consumption': 336.0,  # 1号供电基准煤耗(g/kWh)
            # 2号供电基准煤耗
            'unit_2_power_supply_benchmark_coal_consumption': 339.0,  # 2号供电基准煤耗(g/kWh)

            # 1号供热影响供暖日
            'unit_1_heating_impact_heating_days': 0,                          # 1号供热影响供暖日(GJ)
            # 1号供热影响低压供汽（日）
            'unit_1_heating_impact_low_pressure_steam_days': 0,               # 1号供热影响低压供汽（日）(天)
            # 1号供热影响中压供汽（日）
            'unit_1_heating_impact_medium_pressure_steam_days': 0,             # 1号供热影响中压供汽（日）(天)
            
            # 2号供热影响供暖日
            'unit_2_heating_impact_heating_days': 6807,                          # 2号供热影响供暖日(GJ)
            # 2号供热影响低压供汽（日）
            'unit_2_heating_impact_low_pressure_steam_days': 0,               # 2号供热影响低压供汽（日）(天)
            # 2号供热影响中压供汽（日）
            'unit_2_heating_impact_medium_pressure_steam_days': 0,             # 2号供热影响中压供汽（日）(天)
        },
    }
    # 计算1月份1号机组负荷率(%)
    mon_benchmark['1月']['unit_1_load_factor'] = mon_benchmark['1月']['unit_1_electricity_output'] / mon_benchmark['1月']['unit_1_generation_days'] / 24 / 30
    # 计算1月份2号机组负荷率(%)
    mon_benchmark['1月']['unit_2_load_factor'] = mon_benchmark['1月']['unit_2_electricity_output'] / mon_benchmark['1月']['unit_2_generation_days'] / 24 / 30
    # 计算1月份煤种灰分
    mon_benchmark['1月']['coal_ash'] = annual_benchmark['coal_ash'] - (mon_benchmark['1月']['coal_calorific_value'] - annual_benchmark['coal_calorific_value']) / 37.694

    # 月度影响煤耗系数
    mon_coal_consumption_coefficient = {
        '1月': {
            # 自然条件
            # 海水温度系数
            'sea_temperature_coefficient': (mon_benchmark['1月']['sea_temperature']-annual_benchmark['sea_temperature'])/5*2.7/325.13+1,
            # 当地气温系数
            'local_temperature_coefficient': 1+0.002*(mon_benchmark['1月']['local_temperature']-annual_benchmark['local_temperature']),
            # 电煤水分影响系数
            'coal_moisture_coefficient': 1+2.3*(mon_benchmark['1月']['coal_moisture']-annual_benchmark['coal_moisture'])/mon_benchmark['1月']['coal_calorific_value'],
            # 灰分影响系数
            'coal_ash_coefficient': 1+0.0001*(mon_benchmark['1月']['coal_ash']-annual_benchmark['coal_ash']),
            # 1号机组负荷率影响煤耗
            'unit_1_load_factor_coefficient': 7.254-0.633*(1-math.exp(-mon_benchmark['1月']['unit_1_load_factor']*100/29.822))-5.643*(1-math.exp(-mon_benchmark['1月']['unit_1_load_factor']*100/6.871)),  # 1号机组负荷率影响系数
            # 2号机组负荷率影响煤耗
            'unit_2_load_factor_coefficient': 7.254-0.633*(1-math.exp(-mon_benchmark['1月']['unit_2_load_factor']*100/29.822))-5.643*(1-math.exp(-mon_benchmark['1月']['unit_2_load_factor']*100/6.871)),  # 2号机组负荷率影响系数
            # 1号供热影响系数
            'unit_1_heat_energy_coefficient': calculate_heat_energy_coefficient(
                mon_benchmark['1月']['unit_1_heating_impact_heating_days'],
                mon_benchmark['1月']['unit_1_heating_impact_low_pressure_steam_days'],
                mon_benchmark['1月']['unit_1_heating_impact_medium_pressure_steam_days'],
                mon_benchmark['1月']['unit_1_electricity_output'],
                mon_benchmark['1月']['unit_1_power_supply_benchmark_coal_consumption']
            ),
            # 2号供热影响系数
            'unit_2_heat_energy_coefficient': calculate_unit_2_heat_energy_coefficient(
                mon_benchmark['1月']['unit_2_heating_impact_heating_days'],
                mon_benchmark['1月']['unit_2_generation_days'],
                mon_benchmark['1月']['unit_2_electricity_output'],
                mon_benchmark['1月']['unit_2_power_supply_benchmark_coal_consumption']
            ),
        }
    }

    # 总影响系数
    print("计算总煤耗影响系数...")
    sea_temp_coeff = mon_coal_consumption_coefficient['1月']['sea_temperature_coefficient']
    local_temp_coeff = mon_coal_consumption_coefficient['1月']['local_temperature_coefficient']
    coal_moisture_coeff = mon_coal_consumption_coefficient['1月']['coal_moisture_coefficient']
    coal_ash_coeff = mon_coal_consumption_coefficient['1月']['coal_ash_coefficient']
    unit_1_load_factor_coeff = mon_coal_consumption_coefficient['1月']['unit_1_load_factor_coefficient']
    unit_2_load_factor_coeff = mon_coal_consumption_coefficient['1月']['unit_2_load_factor_coefficient']
    unit_1_heat_energy_coeff = mon_coal_consumption_coefficient['1月']['unit_1_heat_energy_coefficient']
    unit_2_heat_energy_coeff = mon_coal_consumption_coefficient['1月']['unit_2_heat_energy_coefficient']
    
    # 打印每个系数的值
    print("各影响系数值:")
    print(f"1. 海水温度系数: {sea_temp_coeff:.4f}")
    print(f"2. 当地气温系数: {local_temp_coeff:.4f}")
    print(f"3. 电煤水分系数: {coal_moisture_coeff:.4f}")
    print(f"4. 灰分系数: {coal_ash_coeff:.4f}")
    print(f"5. 1号机组负荷率系数: {unit_1_load_factor_coeff:.4f}")
    print(f"6. 2号机组负荷率系数: {unit_2_load_factor_coeff:.4f}")
    print(f"7. 1号供热影响系数: {unit_1_heat_energy_coeff:.4f}")
    print(f"8. 2号供热影响系数: {unit_2_heat_energy_coeff:.4f}")
    
    # 计算1号机组总系数
    unit_1_total_coefficient = (
        sea_temp_coeff * 
        local_temp_coeff * 
        coal_moisture_coeff * 
        coal_ash_coeff * 
        unit_1_load_factor_coeff * 
        unit_1_heat_energy_coeff
    )
    
    # 计算2号机组总系数
    unit_2_total_coefficient = (
        sea_temp_coeff * 
        local_temp_coeff * 
        coal_moisture_coeff * 
        coal_ash_coeff * 
        unit_2_load_factor_coeff * 
        unit_2_heat_energy_coeff
    )
    
    print(f"8. 1号机组总煤耗影响系数: {unit_1_total_coefficient:.4f}")
    print(f"9. 2号机组总煤耗影响系数: {unit_2_total_coefficient:.4f}")
    print()
    
    total_coefficient = {
        '1月': {
            'unit_1_total_coefficient': unit_1_total_coefficient,
            'unit_2_total_coefficient': unit_2_total_coefficient
        }
    }
    print(f"1号机组总煤耗影响系数: {total_coefficient['1月']['unit_1_total_coefficient']}")
    print(f"2号机组总煤耗影响系数: {total_coefficient['1月']['unit_2_total_coefficient']}")
    
    # 计算基本煤耗
    print("计算基本煤耗...")
    electricity_output = annual_benchmark.get('electricity_output', 1000.0)
    basic_coal_consumption = calculate_basic_coal_consumption(
        electricity_output,
        annual_benchmark['coal_calorific_value'],
        annual_benchmark['efficiency']
    )
    
    # 计算月度基本煤耗
    print("计算月度基本煤耗...")
    
    # 1号机组月度基本煤耗计算
    print("1号机组详细计算步骤:")
    unit_1_total_coeff = total_coefficient['1月']['unit_1_total_coefficient']
    unit_1_output = mon_benchmark['1月']['unit_1_electricity_output']
    
    print(f"1. 1号机组总煤耗影响系数: {unit_1_total_coeff:.4f}")
    print(f"2. 1号机组发电量: {unit_1_output:.2f} MWh")
    
    unit_1_term1 = 339 * unit_1_total_coeff
    print(f"3. 339 * 总煤耗影响系数: 339 * {unit_1_total_coeff:.4f} = {unit_1_term1:.2f}")
    
    unit_1_term2 = 600 * 100 / unit_1_output
    print(f"4. 600*100/机组发电量: 600 * 100 / {unit_1_output:.2f} = {unit_1_term2:.2f}")
    
    unit_1_term3 = 100 * 100 / unit_1_output
    print(f"5. 100*100/机组发电量: 100 * 100 / {unit_1_output:.2f} = {unit_1_term3:.2f}")
    
    unit_1_monthly_basic_coal_consumption = unit_1_term1 + unit_1_term2 + unit_1_term3
    print(f"6. 1号机组月度基本煤耗: {unit_1_term1:.2f} + {unit_1_term2:.2f} + {unit_1_term3:.2f} = {unit_1_monthly_basic_coal_consumption:.2f} g/kWh")
    
    # 2号机组月度基本煤耗计算
    print("\n2号机组详细计算步骤:")
    unit_2_total_coeff = total_coefficient['1月']['unit_2_total_coefficient']
    unit_2_output = mon_benchmark['1月']['unit_2_electricity_output']
    
    print(f"1. 2号机组总煤耗影响系数: {unit_2_total_coeff:.4f}")
    print(f"2. 2号机组发电量: {unit_2_output:.2f} MWh")
    
    unit_2_term1 = 339 * unit_2_total_coeff
    print(f"3. 339 * 总煤耗影响系数: 339 * {unit_2_total_coeff:.4f} = {unit_2_term1:.2f}")
    
    # unit_2_term2 = 600 * 100 / unit_2_output
    # print(f"4. 600*100/机组发电量: 600 * 100 / {unit_2_output:.2f} = {unit_2_term2:.2f}")
    
    # unit_2_term3 = 100 * 100 / unit_2_output
    # print(f"5. 100*100/机组发电量: 100 * 100 / {unit_2_output:.2f} = {unit_2_term3:.2f}")
    
    unit_2_monthly_basic_coal_consumption = unit_2_term1 
    print(f"6. 2号机组月度基本煤耗: {unit_2_term1:.2f}  = {unit_2_monthly_basic_coal_consumption:.2f} g/kWh")
    
    print(f"\n基本煤耗: {basic_coal_consumption:.2f} g/kWh")
    print(f"1号机组月度基本煤耗: {unit_1_monthly_basic_coal_consumption:.2f} g/kWh")
    print(f"2号机组月度基本煤耗: {unit_2_monthly_basic_coal_consumption:.2f} g/kWh")
    print()
    print(f"1月1号机组月度基本煤耗: {unit_1_monthly_basic_coal_consumption:.2f} g/kWh")
    print(f"1月2号机组月度基本煤耗: {unit_2_monthly_basic_coal_consumption:.2f} g/kWh")

if __name__ == "__main__":
    main()