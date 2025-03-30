<h1>Блочное кодирование</h1>

<h3>Цель работы: </h3> 
Экспериментальное изучение свойств блочного кодирования.

<h3>Среда программирования:</h3>
Python

<h3>Задание:</h3>

```
1 Для выполнения работы необходим сгенерированный файл с
неравномерным распределением из практической работы 1
При блочном кодировании входная последовательность разбивается на блоки
равной длины, которые кодируются целиком. Поскольку вероятностное
распределение символов в файле известно, то и вероятности блоков могут
быть вычислены и использованы для построения кода.
2 Закодировать файл блочным методом кодирования (можно использовать
любой метод кодирования), размер блока n=1,2,3,4. Вычислить избыточность
кодирования на символ входной последовательности для каждого размера
блока.
3 После тестирования программы необходимо заполнить таблицу и
проанализировать полученные результаты, сравнить с теоретическими
оценками.
```

---

<h3>Техническое описание: </h3>

def calculate_symbol_probabilities(data: str) -> Dict[str, float]:

```python
def calculate_symbol_probabilities(data: str) -> Dict[str, float]:
    """Вычисление вероятностей символов"""
    freq = defaultdict(int)
    total = len(data)

    for char in data:
        freq[char] += 1

    return {char: count / total for char, count in freq.items()}
```
1. Считает частоту каждого символа в тексте.
2. Возвращает словарь {символ: вероятность}.

   ---

def calculate_block_probabilities(data: str, block_size: int) -> Dict[str, float]:

```python
def calculate_block_probabilities(data: str, block_size: int) -> Dict[str, float]:
    """Вычисление вероятностей блоков заданного размера"""
    if len(data) % block_size != 0:
        data = data[:-(len(data) % block_size)]  # Отбрасываем неполный блок

    freq = defaultdict(int)
    total_blocks = len(data) // block_size

    for i in range(total_blocks):
        block = data[i * block_size: (i + 1) * block_size]
        freq[block] += 1

    return {block: count / total_blocks for block, count in freq.items()}
```
1. Разбивает текст на блоки длины block_size.
2. Вычисляет вероятность каждого блока (например, для block_size=2 считает вероятности пар символов).

---

def build_huffman_tree(prob_dict: Dict[str, float]) -> HuffmanNode:

```python
def build_huffman_tree(prob_dict: Dict[str, float]) -> HuffmanNode:
    """Построение дерева Хаффмана"""
    heap = []
    for symbol, prob in prob_dict.items():
        heapq.heappush(heap, HuffmanNode(symbol=symbol, prob=prob))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)

        merged = HuffmanNode(prob=left.prob + right.prob)
        merged.left = left
        merged.right = right

        heapq.heappush(heap, merged)

    return heapq.heappop(heap)
```
1. Создаёт минимальную кучу (min-heap) из узлов.
2. Объединяет два узла с наименьшими вероятностями в новый узел.
3. Повторяет, пока не останется один корневой узел.

---

def generate_huffman_codes(node: HuffmanNode, code="", code_dict=None):

```python
def generate_huffman_codes(node: HuffmanNode, code="", code_dict=None):
    """Генерация кодов Хаффмана"""
    if code_dict is None:
        code_dict = {}

    if node.symbol is not None:
        code_dict[node.symbol] = code  # Код для символа
        return

    generate_huffman_codes(node.left, code + "0", code_dict)   # Левая ветвь → 0
    generate_huffman_codes(node.right, code + "1", code_dict)  # Правая ветвь → 1

    return code_dict
```
1. Рекурсивно обходит дерево, присваивая коды:
```
  Левая ветвь: 0.

  Правая ветвь: 1.
```

---

def encode_data(data: str, code_dict: Dict[str, str], block_size: int) -> str: 

```python
def encode_data(data: str, code_dict: Dict[str, str], block_size: int) -> str:
    """Кодирование данных с использованием кодового словаря"""
    encoded = ""
    if len(data) % block_size != 0:
        data = data[:-(len(data) % block_size)]  # Отбрасываем неполный блок

    total_blocks = len(data) // block_size
    for i in range(total_blocks):
        block = data[i * block_size: (i + 1) * block_size]
        encoded += code_dict[block]

    return encoded
```
1. Разбивает данные на блоки и заменяет каждый блок соответствующим кодом Хаффмана.

---

def analyze_block_encoding(filename: str, max_block_size: int = 4):

```python 
def analyze_block_encoding(filename: str, max_block_size: int = 4):
    """Анализ блочного кодирования для разных размеров блоков"""
    data = read_file(filename)
    symbol_probs = calculate_symbol_probabilities(data)
    symbol_entropy = calculate_entropy(symbol_probs)

    print(f"Энтропия символа: {symbol_entropy:.4f} бит/символ")
    print("\nРезультаты блочного кодирования:")
    print("Размер блока | Энтропия блока | Средняя длина кода | Избыточность")
    print("------------|----------------|--------------------|-------------")

    for block_size in range(1, max_block_size + 1):
        block_probs = calculate_block_probabilities(data, block_size)
        block_entropy = calculate_entropy(block_probs)

        huffman_tree = build_huffman_tree(block_probs)
        huffman_codes = generate_huffman_codes(huffman_tree)

        # Средняя длина кода на блок
        avg_code_length = sum(len(huffman_codes[block]) * prob for block, prob in block_probs.items())

        # Средняя длина кода на символ
        avg_code_length_per_symbol = avg_code_length / block_size

        # Избыточность на символ
        redundancy = avg_code_length_per_symbol - symbol_entropy

        encoded_data = encode_data(data, huffman_codes, block_size)
        calculated_redundancy = calculate_redundancy(data, encoded_data, block_size)

        print(
            f"{block_size:11d} | {block_entropy / block_size:14.4f} | {avg_code_length_per_symbol:18.4f} | {redundancy:11.4f}")
```
1. Сравнивает эффективность кодирования для разных размеров блоков (1–4 символа).
2. Выводит таблицу с:
```
  Энтропией на символ.
  
  Средней длиной кода Хаффмана.
  
  Избыточностью.
```

---

Этот код:

1. Читает текстовые данные.

2. Строит коды Хаффмана для блоков разного размера (1–4 символа).

3. Сравнивает:
```
Энтропию (теоретический минимум бит/символ).

Среднюю длину кода (практический результат).

Избыточность (разницу между ними).
```
4. Показывает, как увеличение размера блока улучшает сжатие.

<h3>Результат работы: </h3>

![image](https://github.com/user-attachments/assets/98caa005-734f-47fb-9355-af8c5d04e902)
