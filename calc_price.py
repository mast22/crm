perf_price = [3500, 8000, 10000, 12000, 15000, 50000] # цены исполнителей
essay_type = 'Дипломная'

# ======================= А Л Г О Р И Т М

k1 = [0.25, 0.25, 0.275, 0.3, 0.3, 0.3, 0.3, 0.35] # коэффициенты постоянные
k2 = [0.1, 0.125, 0.15, 0.15, 0.175, 0.2, 0.25, 0.3]

if essay_type == "Дипломная" or essay_type == "Магистерская":
    i = len(perf_price)
    while i > 0:
        i -= 1
        if perf_price[i] < 4000:
            del perf_price[i]

def mean(n_num):
    """Вычисление медианы"""

    n = len(n_num)
    n_num.sort()

    if n % 2 == 0:
        median1 = n_num[n//2]
        median2 = n_num[n//2 - 1]
        median = (median1 + median2)/2
    else:
        median = n_num[n//2]
    return median

mean_price = mean(perf_price)

print('Медианная цена исполнителей: ', mean_price, ' руб.')

# Расчёт минимальной и рекомендуемой цены:

matrix_price = []

for i in range(len(k1)):
    for x in range(mean_price, mean_price*10):
        if x >= (x * 0.075) + (mean_price * 1.045) + (x * k2[i] * 1.045) + (x * k1[i]):
            matrix_price.append(round(x/500)*500)
            break

print('Минимальная цена для клиента: ', matrix_price[0], ' руб.')
print('Рекомендуемая цена для клиента: ', matrix_price[3], ' руб.')


# Ввод фактической цены и обработка некорректных значений:

fact_price = int(input("Введите фактическую цену: "))

if fact_price < matrix_price[0]:
    print('Ошибка: Фактическая цена ниже минимальной')
    fact_price = int(input("Введите фактическую цену: "))
elif fact_price > matrix_price[0]*9:
    print('Ошибка при вводе цены')
    fact_price = int(input("Введите фактическую цену: "))

# Расчёт комиссии Менеджера:

for i in range(len(matrix_price)):
    if i == len(matrix_price)-1 or ( fact_price >= matrix_price[i] and fact_price < matrix_price[i + 1] ):
        commission = k2[i]
        break

print('Комиссия менеджера: ', commission*100, '% = ', fact_price*commission, ' руб.')