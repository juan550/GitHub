# GitHub Activity Generator

Python скрипт для автоматичного створення активності на GitHub (генерація комітів з випадковими датами).

## Вимоги

- Python 3.6+
- Git встановлений в системі

## Використання

### Базове використання

```bash
python3 github_activity.py
```

Це створить активність за останні 365 днів (1-5 комітів на день).

### Розширене використання

```bash
# Генерувати активність за останні 100 днів
python3 github_activity.py --days 100

# Більше комітів на день (3-8)
python3 github_activity.py --min-commits 3 --max-commits 8

# Генерувати в іншій директорії
python3 github_activity.py --path /path/to/repo

# Комбінований приклад
python3 github_activity.py --days 200 --min-commits 2 --max-commits 6
```

### Параметри

- `--days` - Кількість днів назад для генерації активності (за замовчуванням: 365)
- `--min-commits` - Мінімальна кількість комітів на день (за замовчуванням: 1)
- `--max-commits` - Максимальна кількість комітів на день (за замовчуванням: 5)
- `--path` - Шлях до git репозиторію (за замовчуванням: поточна директорія)

## Публікація на GitHub

Після генерації комітів:

1. **Створіть репозиторій на GitHub** (якщо його немає)

2. **Додайте remote** (замініть URL на свій):
```bash
git remote add origin https://github.com/ваш_username/ваш_репозиторій.git
```

3. **Перевірте поточну гілку**:
```bash
git branch
```

4. **Зробіть push**:
```bash
# Якщо гілка називається 'main'
git push -u origin main

# Або якщо 'master'
git push -u origin master
```

## Важливо

⚠️ **Цей скрипт створює фективну активність**. Використовуйте на свій розсуд. GitHub може виявити неестественну активність.

## Приклади

### Створити активність за останній місяць
```bash
python3 github_activity.py --days 30
```

### Створити активну активність (багато комітів)
```bash
python3 github_activity.py --days 365 --min-commits 5 --max-commits 10
```

### Створити помірну активність
```bash
python3 github_activity.py --days 180 --min-commits 1 --max-commits 3
```
