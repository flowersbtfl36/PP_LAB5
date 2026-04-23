from datetime import datetime
from rich.console import Console

console = Console()

class Node:
    #Клас вузла дерева

    def __init__(self, key, value):
        self.key = key          # Unix-timestamp
        self.value = value      # Деталі транзакції 
        self.left = None        # Лівий нащадок 
        self.right = None       # Правий нащадок  


class BSTIterator:
    #Ітератор для покрокового обходу дерева (Завдання 3.1)
    def __init__(self, root):
        self.stack = []
        self._push_left(root)

    def _push_left(self, node):
        #Допоміжний метод: додає в стек вузол та всіх його лівих нащадків
        while node:
            self.stack.append(node)
            node = node.left

    def hasNext(self):
        #Чи є ще транзакції в черзі?
        return len(self.stack) > 0

    def next(self):
        #Повертає наступну за часом транзакцію (O(1) в середньому)
        if not self.hasNext():
            raise StopIteration()
        
        node = self.stack.pop()
        # Якщо у вузла є правий нащадок, додаємо його ліву гілку в стек
        if node.right:
            self._push_left(node.right)
            
        return node.key, node.value

class BinarySearchTree:
    #Клас Бінарного дерева пошуку

    def __init__(self):
        self.root = None        # Вказівник на корінь 
        console.print("[green]Binary search tree initialized[/green]")

    def insert(self, key, value):
        dt = datetime.fromtimestamp(key).strftime('%Y-%m-%d %H:%M')
        console.print(f"[yellow]Inserting transaction for {dt}...[/yellow]")
        #Публічний метод для додавання вузла 
        if self.root is None:
            self.root = Node(key, value) 
        else:
            self._insert_recursive(self.root, key, value)

    def _insert_recursive(self, node, key, value):
        #Допоміжна рекурсивна функція вставки 

        if key == node.key:
            node.value = value  # Оновлення значення, якщо ключ існує 
        elif key < node.key: # Якщо ключ менший - йдемо вліво, якщо там вільно
            if node.left is None:
                node.left = Node(key, value) 
            else:
                self._insert_recursive(node.left, key, value) 
                #якщо хтось є, викликаємо ту ж функцію, але вузол вже той хто ліворуч
        else:
            if node.right is None:
                node.right = Node(key, value) 
            else:
                self._insert_recursive(node.right, key, value)

    def search(self, key):
        #Пошук за ключем
        result = self._search_recursive(self.root, key)
        if result is None:
            raise KeyError(f"Key {key} not found")  
        return result.value  

    def _search_recursive(self, node, key):
        #Рекурсивний пошук  
        if node is None or node.key == key:
            return node  
        if key < node.key:
            return self._search_recursive(node.left, key)  
        return self._search_recursive(node.right, key) 

    def find_min(self):
       #Пошук вузла з мінімальним ключем 
        if self.root is None:
            return None
        current = self.root #то стаємо на верхівку, корень
        while current.left:
            current = current.left 
        return current.key, current.value

    def find_max(self):
       #Пошук вузла з максимальним ключем 
        if self.root is None:
            return None
        current = self.root
        while current.right:
            current = current.right 
        return current.key, current.value

    def inorder_traversal(self):
        #Обхід у глибину (In-order) через генератор 
        yield from self._inorder_recursive(self.root)  

    def _inorder_recursive(self, node):
        #Рекурсивний обхід для генератора   
        if node:
            yield from self._inorder_recursive(node.left)   
            yield (node.key, node.value)    
            yield from self._inorder_recursive(node.right)  

    def get_height(self):
        #Визначення висоти дерева 
        return self._get_height_recursive(self.root)

    def _get_height_recursive(self, node):
        #Обчислення максимальної відстані до листа 
        if node is None:
            return 0
        return 1 + max(self._get_height_recursive(node.left),  
                       # рівень висоти на якому стоїмо, також рівень, + додаємо 1
                       self._get_height_recursive(node.right))

    def find_range(self, min_key, max_key):
        #Пошук значень у заданому діапазоні 
        results = []
        self._find_range_recursive(self.root, min_key, max_key, results)
        return results 

    def _find_range_recursive(self, node, min_key, max_key, results):
        if node is None:
            return
        # Якщо ключ вузла більший за мінімум, перевіряємо ліве піддерево
        if node.key > min_key:
            self._find_range_recursive(node.left, min_key, max_key, results)
        # Якщо ключ у межах - додаємо
        if min_key <= node.key <= max_key:
            results.append((node.key, node.value))
        # Якщо ключ вузла менший за максимум, перевіряємо праве піддерево
        if node.key < max_key:
            self._find_range_recursive(node.right, min_key, max_key, results)

    
    def delete(self, key):
        #Публічний метод видалення
        self.root = self._delete_recursive(self.root, key)

    def _delete_recursive(self, node, key):
        #Рекурсивне видалення за трьома випадками (Завдання 3.1)
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete_recursive(node.left, key)
        elif key > node.key:
            node.right = self._delete_recursive(node.right, key)
        else:
            # Ключ знайдено
            # Випадок 1 та 2: Один нащадок або лист
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left

            # Випадок 3: Два нащадки
            # Знаходимо мінімальний ключ у правому піддереві
            min_larger_node_key, min_larger_node_value = self._find_min_from_node(node.right)
            node.key = min_larger_node_key
            node.value = min_larger_node_value
            # Видаляємо дублікат з правого піддерева
            node.right = self._delete_recursive(node.right, min_larger_node_key)

        return node

    def _find_min_from_node(self, node):
        #Допоміжний метод для пошуку мінімуму в піддереві
        current = node
        while current.left:
            current = current.left
        return current.key, current.value

    def is_valid_bst(self):
        #Перевірка валідності дерева (Завдання 3.1)
        return self._is_valid_recursive(self.root, float('-inf'), float('inf'))

    def _is_valid_recursive(self, node, min_val, max_val):
        if node is None:
            return True # Якщо ми досягли листа без помилок то шик
        if not (min_val < node.key < max_val):
            return False
        return (self._is_valid_recursive(node.left, min_val, node.key) and
                self._is_recursive(node.right, node.key, max_val))

    


test_data = [
    (datetime(2023, 10, 10, 9, 15), {"amount": 500, "desc": "Оплата кафе"}),
    (datetime(2023, 10, 5, 14, 20), {"amount": 150, "desc": "Netflix Subscription"}),
    (datetime(2023, 10, 1, 0, 5), {"amount": 12000, "desc": "Зарплата"}),
    (datetime(2023, 10, 8, 12, 30), {"amount": 300, "desc": "Продукти (Сільпо)"}),
    (datetime(2023, 10, 3, 18, 45), {"amount": 2100, "desc": "Комунальні платежі"}),
]

registry = BinarySearchTree()

# Наповнення
for dt, info in test_data:
    ts = dt.timestamp()
    registry.insert(ts, info)

# Хронологічний аудит
print("Chronological registry:")
for ts, info in registry.inorder_traversal():
    dt = datetime.fromtimestamp(ts)
    print(f"[{dt.strftime('%Y-%m-%d %H:%M')}] {info['desc']}: {info['amount']}")

# Аналіз екстремумів
min_ts, min_info = registry.find_min()
print(f"\nFirst event: {datetime.fromtimestamp(min_ts)} ({min_info['desc']})")

# Діапазон
print("\nSearch for period (October 4-7):")
start = datetime(2023, 10, 4, 0, 0).timestamp()
end = datetime(2023, 10, 7, 23, 59).timestamp()
for ts, info in registry.find_range(start, end):
    print(f"- {datetime.fromtimestamp(ts).strftime('%Y-%m-%d')}: {info['desc']}")

print(f"\nTree height: {registry.get_height()}")