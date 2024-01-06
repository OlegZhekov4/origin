# Импорт необходимых библиотек
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
# from scipy import stats

# Задаем seed для воспроизводимости результатов
np.random.seed(42)


# Функция для генерации данных
def generate_data(players, conversion_rate):
    return np.random.choice(players, size=int(len(players) * conversion_rate), replace=False)


# Функция для расчета доверительного интервала и размера эффекта
def calculate_ci_and_effect_size(data, total_players):
    # Рассчитываем доверительный интервал для доли
    ci = sm.stats.proportion_confint(len(data), total_players)
    # Рассчитываем размер эффекта как разницу между средними значениями и контрольной долей
    effect_size = np.mean(data) - conversion_rate_control
    return ci, effect_size


# 1. Оптимальный дизайн эксперимента
total_players = 500
experiment_days = 14
new_players_per_day = 100

# Создаем массив игроков и перемешиваем его
players = np.arange(total_players)
np.random.shuffle(players)

# Разделяем игроков на контрольную и экспериментальные группы
control_group, experimental_group = np.array_split(players, 2)

# 2. Рассчитываем продолжительность эксперимента
total_new_players = new_players_per_day * experiment_days

# 3. Создаем набор данных для контрольной группы и рассчитываем доверительный интервал
conversion_rate_control = 0.1
payments_control = generate_data(control_group, conversion_rate_control)
ci_control, _ = calculate_ci_and_effect_size(payments_control, total_players)

# 4. Создаем данные для экспериментальных групп и оцениваем результаты
conversion_rate_experiment_better = 0.11
conversion_rate_experiment_worse = 0.09
conversion_rate_experiment_no_effect = 0.1

# Генерируем данные для каждой экспериментальной группы
experimental_groups = {
    'Лучше': generate_data(experimental_group, conversion_rate_experiment_better),
    'Хуже': generate_data(experimental_group, conversion_rate_experiment_worse),
    'Без эффекта': generate_data(experimental_group, conversion_rate_experiment_no_effect)
}

# Оцениваем результаты с использованием доверительного интервала и размера эффекта
results = {key: calculate_ci_and_effect_size(data, total_players) for key, data in experimental_groups.items()}

# 5. Частотный и Байесовский подход
z_stat, p_value = sm.stats.proportions_ztest([len(experimental_groups['Лучше']), len(payments_control)],
                                             [total_players, total_players])

# Байесовский тест с использованием Z-теста для доли
bayesian_result = sm.stats.proportions_ztest([len(experimental_groups['Лучше']), len(payments_control)],
                                             [total_players, total_players], prop_var=0.25, alternative='two-sided')

# Вывод результатов
print(f"\nЧастотный подход (Z-тест): Z-статистика={z_stat}, P-значение={p_value}")
print(f"\nБайесовский подход (Z-тест для доли): Z-статистика={bayesian_result[0]}, P-значение={bayesian_result[1]}")

# Визуализация результатов
labels = ['Контроль'] + list(experimental_groups.keys())
conversion_rates = [len(payments_control) / total_players] + [np.mean(data) / total_players for data in
                                                              experimental_groups.values()]

plt.bar(labels, conversion_rates)
plt.ylabel('Коэффициент Конверсии')
plt.title('Коэффициенты Конверсии в Различных Группах')
plt.show()
