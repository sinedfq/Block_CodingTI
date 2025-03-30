import os
import math
from collections import defaultdict
import heapq
from typing import Dict, Tuple, List


def read_file(filename: str) -> str:
    """Чтение содержимого файла"""
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()


def calculate_symbol_probabilities(data: str) -> Dict[str, float]:
    """Вычисление вероятностей символов"""
    freq = defaultdict(int)
    total = len(data)

    for char in data:
        freq[char] += 1

    return {char: count / total for char, count in freq.items()}


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


class HuffmanNode:
    """Узел дерева Хаффмана"""

    def __init__(self, symbol=None, prob=0.0):
        self.symbol = symbol
        self.prob = prob
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.prob < other.prob


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


def generate_huffman_codes(node: HuffmanNode, code="", code_dict=None):
    """Генерация кодов Хаффмана"""
    if code_dict is None:
        code_dict = {}

    if node.symbol is not None:
        code_dict[node.symbol] = code
        return

    generate_huffman_codes(node.left, code + "0", code_dict)
    generate_huffman_codes(node.right, code + "1", code_dict)

    return code_dict


def calculate_entropy(prob_dict: Dict[str, float]) -> float:
    """Вычисление энтропии"""
    entropy = 0.0
    for prob in prob_dict.values():
        if prob > 0:
            entropy -= prob * math.log2(prob)
    return entropy


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


def calculate_redundancy(original_data: str, encoded_data: str, block_size: int) -> float:
    """Вычисление избыточности на символ"""
    original_bits = len(original_data) * 8  # Предполагаем 8 бит на символ
    encoded_bits = len(encoded_data)

    # Избыточность на символ исходных данных
    return (encoded_bits / len(original_data)) - calculate_entropy(calculate_symbol_probabilities(original_data))


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


if __name__ == "__main__":
    input_file = "input_data.txt"  # Файл, сгенерированный в практической работе 1
    if not os.path.exists(input_file):
        print(f"Ошибка: файл {input_file} не найден.")
        print("Сгенерируйте файл с неравномерным распределением символов.")
    else:
        analyze_block_encoding(input_file, max_block_size=4)