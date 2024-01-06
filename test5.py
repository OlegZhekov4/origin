import sqlite3
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

# Шаг 1: Подключение к базе данных и загрузка данных
conn = sqlite3.connect('testcase.db')
query = "SELECT * FROM source_comparison;"
df = pd.read_sql_query(query, conn)
conn.close()

# Шаг 2: Анализ данных
print(tabulate(df.head(), headers='keys', tablefmt='pretty'))

print("\nСтатистика по типу источника:")
print(tabulate(df.groupby('source_type')['installs'].describe(), headers='keys', tablefmt='pretty'))

# Визуализация данных
sns.boxplot(x='source_type', y='installs', data=df)
plt.show()

# Шаг 3: Проверка гипотезы
paid_group = df[df['source_type'] == 'Paid']['installs']
organic_group = df[df['source_type'] == 'Organic']['installs']

t_statistic, p_value = ttest_ind(paid_group, organic_group)

# Вывод результатов теста
print("\nРезультаты теста:")
table = [["T-статистика", t_statistic],
         ["P-значение", p_value]]
print(tabulate(table, headers=['Метрика', 'Значение'], tablefmt='pretty'))

# Проверка статистической значимости
alpha = 0.05
result = "Гипотеза отвергнута: есть статистически значимые различия." if p_value < alpha else "Гипотеза не отвергнута: нет статистически значимых различий."
print(result)

