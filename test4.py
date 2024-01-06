import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


# Шаг 1: Загрузка данных из базы данных
def load_data_from_db():
    conn = sqlite3.connect('testcase.db')

    # Загрузка данных из таблицы costs
    costs_df = pd.read_sql_query("SELECT * FROM costs", conn)

    # Загрузка данных из таблицы revenue
    revenue_df = pd.read_sql_query("SELECT * FROM revenue", conn)

    # Закрываем соединение с базой данных
    conn.close()

    return costs_df, revenue_df


# Шаг 2: Анализ данных и проверка гипотезы
def analyze_data(costs_df, revenue_df):
    # Объединение данных по campaign_id и Install_Dates
    merged_df = pd.merge(costs_df, revenue_df, on=['campaign_id', 'Install_Dates'])

    # Расчет ROAS 60 дня
    merged_df['ROAS_60'] = merged_df['60d_LTV'] / merged_df['spends']

    # Проверка гипотезы: зависимость между COST и ROAS_60
    correlation = merged_df['spends'].corr(merged_df['ROAS_60'])
    print(f"Корреляция между COST и ROAS_60: {correlation}")

    # Визуализация зависимости
    plt.scatter(merged_df['spends'], merged_df['ROAS_60'])
    plt.xlabel('COST')
    plt.ylabel('ROAS_60')
    plt.title('Зависимость между COST и ROAS_60')
    plt.show()

    return merged_df


# Шаг 3: Оптимизация суточного бюджета для максимизации прибыли
def optimize_budget(merged_df):
    # Расчет прибыли для каждой рекламной кампании
    merged_df['profit'] = merged_df['60d_LTV'] - merged_df['spends']

    # Группировка данных по campaign_id для оптимизации суточного бюджета
    grouped_df = merged_df.groupby('campaign_id').agg({'spends': 'sum', 'profit': 'sum'}).reset_index()

    # Расчет суточного бюджета и суммы на увеличение/уменьшение бюджета
    grouped_df['daily_budget'] = grouped_df['profit'] / grouped_df['spends']
    grouped_df['budget_change_amount'] = abs(grouped_df['profit']).round(2)

    # Вывод результатов
    print(grouped_df[['campaign_id', 'daily_budget', 'budget_change_amount']])

    return grouped_df


# Шаг 4: Заключение о коррекции бюджета рекламных кампаний
def make_budget_adjustments(grouped_df):
    # Заключение о коррекции бюджета
    grouped_df['Recommendation'] = grouped_df['daily_budget'].apply(
        lambda x: 'Увеличить бюджет' if x > 0 else (
            'Уменьшить бюджет или остановить' if x < 0 else 'Бюджет можно оставить без изменений')
    )

    # Создаем DataFrame из нужных столбцов
    recommendations_df = grouped_df[['campaign_id', 'Recommendation', 'budget_change_amount']]

    # Записываем рекомендации в базу данных
    conn = sqlite3.connect('recommendations.db')
    recommendations_df.to_sql('recommendation_id', conn, index=False, if_exists='replace')
    conn.close()

    # Вывод рекомендаций в виде таблицы
    print("\nРекомендации по коррекции бюджета:")
    print(recommendations_df)


# Основная часть программы
costs_df, revenue_df = load_data_from_db()
merged_df = analyze_data(costs_df, revenue_df)
grouped_df = optimize_budget(merged_df)
make_budget_adjustments(grouped_df)
