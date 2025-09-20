# Решение задачи восстановления пробелов в русском тексте

## Восстановление пробелов в русском тексте

Алгоритм: Динамическое программирование с частотным словарем (без использования ML).

Основные компоненты:
1. SpaceRestorer - главный класс с DP алгоритмом
2. Система оценки слов на основе частотного словаря
3. Оптимизации для слов, часто встречающихся на Avito

Точность: F1 ~70% на тестовых данных

Откуда мои словари:
- Основной частотный словарь: main_1grams.tsv (от ruscorpora, по ссылке: https://ruscorpora.ru/media/uploads/2023/10/02/main_1grams.zip)
- Дополнительный словарь: dictionary_output.json (Russian - Russian dictionary, достан из моей читалки, был в формате .ifo, преобразован мною в json)
- Avito-специфичные слова: захардкожены мной, надеюсь, это допустимо 

## Запуск решения

### Требования
```bash
pip install pandas
```
или
```bash
pip install requirements.txt
```

### Структура файлов
```
avito/
├── solution.py                 # Основное решение
├── main_1grams.tsv             # Частотный словарь
├── dictionary_output.json      # Дополнительный словарь
├── filename.txt                # Входной датасет
├── requirements.txt            # Требования
└── README.md                   # Документация
```

### Запуск

1. Положить в директорию filename.txt (заменить существующий)
2.
```bash
python solution.py
```
или

1. Положить любой your_file.txt
2.
```bash
python solution.py your_file.txt
```

В конце solution.py вы найдете старт:
```Python
if __name__ == "__main__":
    import sys
    
    # 1. Инициализация модели
    restorer = SpaceRestorer()
    
    # 2. Загрузка данных
    # Проверяем, если передан аргумент командной строки или есть файл filename.txt
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "filename.txt"
    
    # Загружаем данные
    df = load_dataset(filename)

    # 3. Обработка датасета
    result_df = process_dataset(df, restorer)

    # 4. Сохранение результатов в submission.csv
    save_submission(result_df)
``` 

### Результат: **submission.csv** - файл с результатами в нужном формате
