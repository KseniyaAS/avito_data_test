#!/usr/bin/env python3
import pandas as pd
import json
import time
import math
from typing import List


class SpaceRestorer:
    """
    Основной класс для восстановления пробелов в русском тексте
    
    Использует алгоритм динамического программирования для поиска
    оптимальной сегментации текста на слова на основе частотного словаря.

    word_freq (Dict[str, int]): Словарь частотности слов
    """
    
    def __init__(self, min_word_length: int = 1, max_word_length: int = 25):
        """
        Инициализация восстановителя пробелов
        
        Args:
            min_word_length: Минимальная длина слова
            max_word_length: Максимальная длина слова для DP
        """
        self.word_freq = {}
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        
        self._load_dictionaries()
    
    def _load_dictionaries(self) -> None:
        """
        Загружает частотные словари из доступных источников
        """
        # 1. Загрузка словарей (описано в README)
        self._load_main_frequency_dict()
        self._load_json_dict()

        # 2. Добавление Avito-специфичных слов
        self._add_avito_words()
        
    
    def _load_main_frequency_dict(self) -> None:
        """Загружает основной частотный словарь из main_1grams.tsv"""
        with open('main_1grams.tsv', 'r', encoding='utf-8') as f:
            loaded_count = 0
            for line_num, line in enumerate(f):
                # Ограничиваем загрузку для ускорения инициализации
                if line_num >= 1000000:
                    break
                
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    word = parts[0].lower().strip()
                    
                    # Фильтрация: только русские буквы и разумная длина
                    if (word.isalpha() and 
                        len(word) >= self.min_word_length and 
                        len(word) <= 20 and
                        self._is_cyrillic_word(word)):
                        
                        try:
                            freq = int(parts[1])
                            self.word_freq[word] = freq
                            loaded_count += 1
                        except ValueError:
                            continue

    
    
    def _load_json_dict(self) -> None:
        """Загружает JSON словарь"""
        with open('dictionary_output.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            loaded_count = 0
            
            # Обрабатываем разные форматы JSON
            if isinstance(data, dict):
                for word, freq in data.items():
                    word = word.lower().strip()
                    if (word.isalpha() and 
                        len(word) >= 2 and 
                        self._is_cyrillic_word(word)):
                        
                        try:
                            freq_val = int(freq) if isinstance(freq, (int, str)) else 100
                            if word not in self.word_freq:
                                self.word_freq[word] = freq_val
                                loaded_count += 1
                        except ValueError:
                            pass
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        word = item.lower().strip()
                        if (word.isalpha() and 
                            len(word) >= 2 and 
                            self._is_cyrillic_word(word)):
                            
                            if word not in self.word_freq:
                                self.word_freq[word] = 100
                                loaded_count += 1
                
    
    def _add_avito_words(self) -> None:
        """
        Добавляет специфичные для Avito слова с высокими частотами
        
        Включает:
        - Действия пользователей (куплю, продам, сдаю...)
        - Популярные бренды техники
        - Недвижимость и транспорт
        - Предлоги и служебные слова
        - Числа и измерения
        """
        avito_words = {
            # Основные действия пользователей Avito
            'куплю': 60000, 'продам': 55000, 'сдаю': 50000, 'сниму': 45000, 
            'ищу': 70000, 'отдам': 40000, 'обменяю': 35000, 'меняю': 30000,
            'покупаю': 25000, 'продаю': 20000, 'сдам': 30000, 'сниму': 25000,
            
            # Популярные бренды техники
            'айфон': 45000, 'iphone': 40000, 'samsung': 30000, 'xiaomi': 25000,
            'huawei': 20000, 'nokia': 15000, 'lg': 18000, 'sony': 16000,
            'macbook': 20000, 'asus': 15000, 'lenovo': 12000, 'hp': 10000,
            'dell': 8000, 'acer': 7000, 'msi': 6000,
            
            # Автомобильные бренды
            'тойота': 15000, 'toyota': 12000, 'бмв': 10000, 'bmw': 8000,
            'мерседес': 8000, 'mercedes': 6000, 'ауди': 7000, 'audi': 5000,
            'фольксваген': 6000, 'volkswagen': 4000, 'киа': 8000, 'kia': 6000,
            'хендай': 7000, 'hyundai': 5000, 'ниссан': 6000, 'nissan': 4000,
            
            # Недвижимость - все падежи
            'квартиру': 60000, 'квартира': 55000, 'квартире': 50000, 'квартиры': 45000,
            'квартирой': 35000, 'квартир': 40000, 'квартирах': 25000,
            'комнату': 55000, 'комната': 50000, 'комнате': 45000, 'комнаты': 40000,
            'комнатой': 30000, 'комнат': 35000, 'комнатах': 20000,
            'дом': 45000, 'дома': 40000, 'доме': 35000, 'домом': 25000, 'домов': 30000,
            'студию': 25000, 'студия': 20000, 'студии': 18000,
            
            # Транспорт
            'машину': 50000, 'машина': 45000, 'машине': 40000, 'машины': 35000,
            'машиной': 25000, 'машин': 30000, 'авто': 35000, 'автомобиль': 30000,
            'мотоцикл': 15000, 'скутер': 8000, 'велосипед': 12000,
            
            # География
            'москве': 40000, 'москва': 35000, 'московской': 25000, 'подмосковье': 30000,
            'спб': 20000, 'питер': 15000, 'санкт': 12000, 'петербург': 10000,
            'екатеринбург': 8000, 'новосибирск': 7000, 'казань': 6000,
            
            # Состояние товаров
            'новый': 40000, 'новая': 35000, 'новое': 30000, 'новые': 25000,
            'хорошем': 30000, 'хорошее': 25000, 'хороший': 20000, 'хорошая': 18000,
            'отличном': 25000, 'отличное': 20000, 'отличный': 15000, 'отличная': 12000,
            'идеальном': 15000, 'идеальное': 12000, 'рабочем': 18000, 'рабочее': 15000,
            
            # Высокочастотные предлоги и служебные слова
            'в': 120000, 'на': 110000, 'с': 100000, 'для': 80000, 'от': 70000,
            'до': 60000, 'по': 55000, 'за': 50000, 'под': 40000, 'над': 25000,
            'без': 35000, 'через': 30000, 'при': 25000, 'про': 20000,
            'или': 45000, 'и': 150000, 'а': 80000, 'но': 40000, 'что': 60000,
            
            # Цены и условия
            'недорого': 30000, 'дешево': 25000, 'дорого': 15000, 'бесплатно': 20000,
            'срочно': 25000, 'торг': 18000, 'торга': 12000, 'цена': 25000,
            'рублей': 20000, 'тысяч': 18000, 'миллион': 8000, 'доставка': 22000,
            
            # Мебель и быт
            'диван': 35000, 'кресло': 18000, 'стол': 15000, 'кровать': 22000, 
            'шкаф': 18000, 'комод': 10000, 'тумба': 8000, 'полка': 7000,
            'холодильник': 18000, 'стиральная': 15000, 'посудомоечная': 8000,
            'микроволновка': 7000, 'телевизор': 20000, 'компьютер': 15000,
            
            # Часто используемые числа
            '1': 15000, '2': 14000, '3': 13000, '4': 12000, '5': 11000,
            '6': 10000, '7': 9000, '8': 8000, '9': 7000, '10': 12000,
            '11': 8000, '12': 7000, '13': 6000, '14': 9000, '15': 6000,
            '16': 7000, '17': 5000, '18': 5000, '19': 4000, '20': 8000,
            '30': 6000, '40': 5000, '50': 5000, '100': 4000,
            
            # Модели и характеристики
            'про': 18000, 'плюс': 12000, 'макс': 8000, 'мини': 6000,
            'стандарт': 5000, 'премиум': 4000, 'базовый': 3000,
            
            # Популярные сокращения
            'тел': 12000, 'руб': 10000, 'тыс': 8000, 'шт': 6000,
            'кв': 8000, 'м': 15000, 'см': 6000, 'км': 5000, 'г': 12000,
        }
        
        # Добавляем слова, устанавливая высокую частоту
        added_count = 0
        for word, freq in avito_words.items():
            if word not in self.word_freq or self.word_freq[word] < freq:
                self.word_freq[word] = freq
                added_count += 1


    def looks_like_russian_word(self, word: str) -> bool:
        """
        Проверяет, похожа ли строка на русское слово
        
        Args:
            word: Потенциальное слово
            
        Returns:
            True, если похоже на русское слово
        """
        if len(word) < 2:
            return False
        
        # Только кириллица
        if not all(c.isalpha() and ord(c) >= 1040 for c in word.lower()):
            return False
        
        # Проверяем на разумное соотношение гласных и согласных
        vowels = set('аеёиоуыэюя')
        consonants = set('бвгджзйклмнпрстфхцчшщ')
        
        vowel_count = sum(1 for c in word.lower() if c in vowels)
        consonant_count = sum(1 for c in word.lower() if c in consonants)
        
        # Должно быть хотя бы по одной гласной и согласной
        if vowel_count == 0 or consonant_count == 0:
            return False
        
        # Не должно быть слишком много согласных подряд
        consonant_streak = 0
        for c in word.lower():
            if c in consonants:
                consonant_streak += 1
                if consonant_streak > 4:  # Максимум 4 согласных подряд
                    return False
            else:
                consonant_streak = 0
        
        return True
    
    def _is_cyrillic_word(self, word: str) -> bool:
        """Проверяет, содержит ли слово кириллические символы"""
        return any(char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for char in word.lower())
    
    def _get_ending_bonus(self, word: str) -> float:
        """
        Дает бонус за правдоподобные русские окончания
        
        Args:
            word: Слово для анализа
            
        Returns:
            Бонус (больше = лучше)
        """
        if len(word) < 3:
            return 0.0
        
        # Популярные окончания русских слов
        good_endings = {
            # Существительные
            'ом': 2.0, 'ой': 2.0, 'ий': 2.0, 'ая': 2.0, 'ое': 2.0, 'ые': 2.0,
            'ам': 1.5, 'ах': 1.5, 'ми': 1.5, 'ов': 1.5, 'ев': 1.5, 'ей': 1.5,
            'ку': 1.8, 'ту': 1.8, 'ну': 1.8, 'ру': 1.8, 'лю': 1.8, 'шу': 1.8,
            'ие': 1.5, 'ее': 1.5, 'ём': 1.5, 'их': 1.5, 'им': 1.5, 'ую': 1.5,
            # Глаголы
            'ть': 3.0, 'ся': 2.5, 'ет': 2.0, 'ит': 2.0, 'ат': 2.0, 'ят': 2.0,
            'ем': 1.8, 'им': 1.8, 'ют': 1.8, 'ут': 1.8, 'ал': 1.5, 'ил': 1.5,
            # Прилагательные
            'ый': 2.0, 'ая': 2.0, 'ое': 2.0, 'ые': 2.0, 'ых': 1.5, 'ым': 1.5,
            'ому': 1.8, 'ему': 1.8, 'ую': 1.8, 'юю': 1.8,
        }
        
        for ending, bonus in good_endings.items():
            if word.endswith(ending):
                return bonus
        
        return 0.0
    
    def get_word_score(self, word: str) -> float:
        """
        Вычисляет оценку качества слова для алгоритма сегментации
        
        Факторы оценки:
        1. Частота в словаре (основной фактор)
        2. Длина слова (штраф за очень короткие)
        3. Наличие кириллицы (бонус)
        4. Смешанные языки (штраф)
        5. Паттерны (числа, специальные символы)
        
        Args:
            word: Слово для оценки
            
        Returns:
            float: Оценка качества слова (больше = лучше)
        """
        if not word:
            return 0.0
        
        word_lower = word.lower().strip()
        
        # 1. Базовая частота из словаря
        base_freq = self.word_freq.get(word_lower, 0)
        if base_freq > 0:
            # Логарифмическое сжатие для больших частот
            score = min(1000.0, float(base_freq))
        else:
            # Штраф для неизвестных слов, но не нулевой
            score = 1.0
        
        # 2. Штрафы/бонусы за длину слова
        word_len = len(word)
        if word_len == 1:
            score *= 0.01  # Очень сильный штраф за однобуквенные слова
        elif word_len == 2:
            score *= 0.1   # Сильный штраф за двубуквенные
        elif word_len == 3:
            score *= 0.5   # Умеренный штраф за трёхбуквенные
        elif word_len >= 6:
            score *= 1.3   # Бонус за длинные слова
        
        # 3. Языковые особенности
        has_cyrillic = any(c in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя' for c in word_lower)
        has_latin = any(c in 'abcdefghijklmnopqrstuvwxyz' for c in word_lower)
        has_digits = any(c.isdigit() for c in word_lower)
        
        # Бонус за кириллицу (основной язык)
        if has_cyrillic:
            score *= 1.2
        
        # Штраф за смешанные языки в коротких словах
        if has_cyrillic and has_latin and word_len < 6:
            score *= 0.3
        
        # Особая обработка чисел
        if has_digits:
            if word.isdigit():
                # Чистые числа получают умеренную оценку
                score = max(score, 100.0)
            else:
                # Смешанные буквы-цифры (модели техники и т.д.)
                score *= 0.8
        
        # 4. Специальные паттерны
        # Популярные окончания
        if word_lower.endswith(('ость', 'ение', 'ание', 'ция', 'сть')):
            score *= 1.1
        
        # Популярные префиксы
        if word_lower.startswith(('пре', 'про', 'под', 'над', 'сверх')):
            score *= 1.05
        
        # 5. Нормализация
        # Ограничиваем максимальную оценку для стабильности
        score = min(score, 10000.0)
        
        return score
    
    def dynamic_programming_segmentation(self, text: str) -> List[int]:
        """
        Кардинально переработанная DP сегментация - приоритет длинным словам
        
        Алгоритм находит оптимальное разбиение текста на слова, максимизируя
        суммарную оценку всех слов с особым приоритетом длинным известным словам.
        
        Args:
            text: Входной текст без пробелов
            
        Returns:
            List[int]: Список позиций, где должны быть пробелы
        """
        if not text:
            return []
        
        n = len(text)
        # dp[i] = лучший счет для текста до позиции i
        dp = [-float('inf')] * (n + 1)
        # parent[i] = начало последнего слова, заканчивающегося в позиции i
        parent = [-1] * (n + 1)
        dp[0] = 0.0
        
        for i in range(1, n + 1):
            best_score = -float('inf')
            best_start = -1
            
            # Проверяем все возможные слова, заканчивающиеся в позиции i
            # Сначала проверяем длинные слова, потом короткие
            max_len = min(20, i)  # Ограничиваем максимальную длину слова
            
            for start in range(max(0, i - max_len), i):
                word = text[start:i]
                word_len = len(word)
                word_lower = word.lower()
                
                # Вычисляем оценку слова
                if word_lower in self.word_freq:
                    # Известное слово
                    freq = self.word_freq[word_lower]
                    base_score = math.log(freq + 1)
                    
                    # КРИТИЧНО: Массивные бонусы за длинные известные слова
                    if word_len >= 7:
                        length_bonus = 25.0 + (word_len - 7) * 3.0  # 25+ баллов за слова 7+ символов
                    elif word_len == 6:
                        length_bonus = 20.0  # 20 баллов за 6-символьные слова
                    elif word_len == 5:
                        length_bonus = 15.0  # 15 баллов за 5-символьные слова
                    elif word_len == 4:
                        length_bonus = 10.0  # 10 баллов за 4-символьные слова
                    elif word_len == 3:
                        length_bonus = 5.0   # 5 баллов за 3-символьные слова
                    elif word_len == 2:
                        length_bonus = 0.0   # 0 баллов за 2-символьные слова
                    else:  # word_len == 1
                        length_bonus = -30.0  # ОГРОМНЫЙ штраф за одиночные символы
                    
                    word_score = base_score + length_bonus
                    
                elif word_len >= 3 and self.looks_like_russian_word(word):
                    # Неизвестное, но правдоподобное слово
                    base_score = 8.0 + self._get_ending_bonus(word)
                    
                    # Бонус за длину для неизвестных слов
                    if word_len >= 7:
                        length_bonus = 8.0 + (word_len - 7) * 1.5
                    elif word_len == 6:
                        length_bonus = 6.0
                    elif word_len == 5:
                        length_bonus = 4.0
                    elif word_len == 4:
                        length_bonus = 2.0
                    else:  # word_len == 3
                        length_bonus = 0.0
                    
                    # Штраф за слишком длинные неизвестные слова
                    if word_len > 12:
                        length_bonus -= (word_len - 12) * 2.0
                    
                    word_score = base_score + length_bonus
                    
                else:
                    # Неправдоподобное слово или короткое
                    if word_len == 1:
                        word_score = -35.0  # ОГРОМНЫЙ штраф за одиночные символы
                    elif word_len == 2:
                        word_score = -25.0  # Очень большой штраф за 2-символьные неизвестные
                    else:
                        word_score = -15.0 - word_len * 3.0  # Растущий штраф
                
                # Общий счет = счет предыдущей позиции + счет текущего слова
                total_score = dp[start] + word_score
                
                if total_score > best_score:
                    best_score = total_score
                    best_start = start
            
            # Устанавливаем лучший результат
            if best_start != -1:
                dp[i] = best_score
                parent[i] = best_start
            else:
                # Fallback: одиночный символ с огромным штрафом
                dp[i] = dp[i-1] - 40.0
                parent[i] = i - 1
        
        # Восстанавливаем сегментацию
        positions = []
        i = n
        
        while parent[i] != -1:
            start_pos = parent[i]
            if start_pos > 0:  # Не добавляем позицию в начале текста
                positions.append(start_pos)
            i = start_pos
        
        return sorted(positions)
    
    def greedy_segmentation(self, text: str) -> List[int]:
        """
        Жадный алгоритм сегментации как альтернатива DP
        
        Args:
            text: Входной текст без пробелов
            
        Returns:
            Список позиций, где должны быть пробелы
        """
        if not text:
            return []
        
        positions = []
        i = 0
        
        while i < len(text):
            # Ищем самое длинное известное слово, начинающееся с позиции i
            best_word_len = 1
            best_score = -float('inf')
            
            # Проверяем слова разной длины
            max_len = min(20, len(text) - i)
            
            for word_len in range(1, max_len + 1):
                if i + word_len > len(text):
                    break
                    
                word = text[i:i + word_len]
                word_lower = word.lower()
                
                if word_lower in self.word_freq:
                    # Известное слово - приоритет длинным
                    score = math.log(self.word_freq[word_lower] + 1) + len(word) * 0.5
                    if score > best_score and len(word) >= 2:  # Минимум 2 символа для известных слов
                        best_score = score
                        best_word_len = word_len
                
                elif len(word) >= 3 and self.looks_like_russian_word(word):
                    # Неизвестное правдоподобное слово
                    score = 3.0 + self._get_ending_bonus(word)
                    if len(word) <= 12:  # Ограничиваем длину неизвестных слов
                        if score > best_score:
                            best_score = score
                            best_word_len = word_len
            
            # Переходим к следующему слову
            i += best_word_len
            if i < len(text):
                positions.append(i)
        
        return positions
    
    def _get_words_from_positions(self, text: str, positions: List[int]) -> List[str]:
        """
        Извлекает слова из текста по позициям пробелов
        """
        if not positions:
            return [text] if text else []
        
        words = []
        all_positions = [0] + sorted(positions) + [len(text)]
        
        for i in range(len(all_positions) - 1):
            start, end = all_positions[i], all_positions[i + 1]
            word = text[start:end].strip()
            if word:
                words.append(word)
        
        return words

    def combine_methods(self, text: str) -> List[int]:
        """
        Упрощенная комбинация методов с fallback на жадный алгоритм
        
        Args:
            text: Входной текст без пробелов
            
        Returns:
            Список позиций пробелов
        """
        # Основной метод: DP
        dp_positions = self.dynamic_programming_segmentation(text)
        
        # Проверяем качество результата
        words = self._get_words_from_positions(text, dp_positions)
        
        # Считаем долю "плохих" слов (очень короткие или неизвестные длинные)
        bad_words = 0
        for word in words:
            if len(word) <= 2 and word.lower() not in self.word_freq:
                bad_words += 1
            elif len(word) > 15 and word.lower() not in self.word_freq:
                bad_words += 1
        
        bad_ratio = bad_words / len(words) if words else 0
        
        # Если слишком много плохих слов, используем жадный алгоритм
        if bad_ratio > 0.3:  # Больше 30% плохих слов
            greedy_positions = self.greedy_segmentation(text)
            
            # Сравниваем результаты и выбираем лучший
            greedy_words = self._get_words_from_positions(text, greedy_positions)
            greedy_bad = sum(1 for w in greedy_words 
                           if (len(w) <= 2 and w.lower() not in self.word_freq) or
                              (len(w) > 15 and w.lower() not in self.word_freq))
            greedy_bad_ratio = greedy_bad / len(greedy_words) if greedy_words else 1
            
            if greedy_bad_ratio < bad_ratio:
                dp_positions = greedy_positions
        
        # Простая фильтрация
        result = self._filter_positions_simple(text, dp_positions)
        
        return result
    
    def _filter_positions_simple(self, text: str, positions: List[int]) -> List[int]:
        """
        Упрощенная фильтрация позиций
        """
        if not positions:
            return positions
        
        filtered = []
        
        for pos in sorted(positions):
            # Убираем позиции на краях
            if pos <= 0 or pos >= len(text):
                continue
            
            # Убираем позиции слишком близко друг к другу
            if filtered and pos - filtered[-1] <= 1:
                continue
            
            filtered.append(pos)
        
        return filtered
        
    def predict_space_positions(self, text: str) -> List[int]:
        """
        Предсказывает позиции пробелов в тексте
        
        Основной публичный метод для получения позиций пробелов.
        Выполняет предобработку текста и применяет улучшенный алгоритм сегментации.
        
        Args:
            text: Входной текст без пробелов
            
        Returns:
            List[int]: Отсортированный список позиций пробелов
        """
        if not text or len(text) < 2:
            return []
        
        # Предобработка текста
        processed_text = text.strip().lower()
        
        # Комбинируем методы с интеллектуальным выбором
        positions = self.combine_methods(processed_text)
        
        # Фильтрация: убираем позиции в начале и конце
        positions = [pos for pos in positions if 0 < pos < len(processed_text)]
        
        # Убираем дубликаты и сортируем
        positions = sorted(list(set(positions)))
        
        return positions
    
    def restore_spaces(self, text: str) -> str:
        """
        Восстанавливает пробелы в тексте
        
        Convenience метод для получения текста с восстановленными пробелами.
        
        Args:
            text: Входной текст без пробелов
            
        Returns:
            str: Текст с восстановленными пробелами
        """
        positions = self.predict_space_positions(text)
        
        if not positions:
            return text
        
        result = ""
        prev = 0
        for pos in positions:
            result += text[prev:pos] + " "
            prev = pos
        result += text[prev:]
        
        return result


def load_dataset(filename: str = "dataset_1937770_3.txt") -> pd.DataFrame:
    """
    Загружает датасет для обработки, правильно обрабатывая запятые в тексте
    
    Args:
        filename: Имя файла с данными
        
    Returns:
        pd.DataFrame: Загруженные данные
    """

    # Читаем файл построчно и обрабатываем
    data = []
    with open(filename, 'r', encoding='utf-8') as f:
        header_line = f.readline().strip()
        
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            # Разделяем только по первой запятой
            if ',' in line:
                first_comma = line.find(',')
                id_part = line[:first_comma].strip()
                text_part = line[first_comma + 1:].strip()
                
                # Заменяем дополнительные запятые и другие знаки препинания пробелами в тексте
                import string
                # Создаем таблицу замены: все знаки препинания кроме букв, цифр и дефисов заменяем пробелами
                punctuation_chars = ',;:!?"\'()[]{}«»„"-—–.…'
                spaces = ' ' * len(punctuation_chars)  # Создаем строку пробелов той же длины
                translator = str.maketrans(punctuation_chars, spaces)
                text_part = text_part.translate(translator)
                
                # Убираем множественные пробелы, но сохраняем одиночные
                import re
                text_part = re.sub(r'\s+', ' ', text_part)  # Заменяем множественные пробелы одним пробелом
                text_part = text_part.strip()  # Убираем пробелы в начале и конце
                
                id_val = int(id_part)
                data.append({'id': id_val, 'text_no_spaces': text_part})
            else:
                continue

    df = pd.DataFrame(data)

    return df
        


def process_dataset(df: pd.DataFrame, restorer: SpaceRestorer) -> pd.DataFrame:
    """
    Обрабатывает весь датасет и предсказывает позиции пробелов
    
    Args:
        df: Датасет с текстами
        restorer: Инициализированный восстановитель пробелов
        
    Returns:
        pd.DataFrame: Датасет с добавленной колонкой predicted_positions
    """
    
    # Создаем копию датасета
    result_df = df.copy()
    
    # Определяем колонку с текстом
    text_column = None
    for col in ['text_no_spaces', 'text', 'input_text', 'source_text', 'content']:
        if col in df.columns:
            text_column = col
            break
    
    
    # Обрабатываем каждую строку
    predicted_positions = []
    processing_times = []
    
    for idx, row in df.iterrows():
        start_time = time.time()
        
        text = str(row[text_column]).strip()
        if not text:
            positions = []
        else:
            positions = restorer.predict_space_positions(text)
        
        predicted_positions.append(positions)
        
        processing_time = time.time() - start_time
        processing_times.append(processing_time)
        
    # Добавляем результаты в датасет
    result_df['predicted_positions'] = predicted_positions
    
    return result_df


def save_submission(df: pd.DataFrame, filename: str = "submission.csv") -> None:
    """
    Сохраняет результаты в формате для отправки
    
    Args:
        df: Датасет с результатами
        filename: Имя файла для сохранения
    """
    # Подготавливаем данные в нужном формате
    submission_df = df[['id', 'predicted_positions']].copy()
    
    # Конвертируем списки в строки в нужном формате
    submission_df['predicted_positions'] = submission_df['predicted_positions'].apply(
        lambda x: str(x) if isinstance(x, list) else "[]"
    )
    
    # Сохраняем
    submission_df.to_csv(filename, index=False)


        

if __name__ == "__main__":
    """
    Основная функция для выполнения всего процесса
    """
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