from datetime import datetime
import json
import math
from rich.console import Console
from pathlib import Path

console = Console()

class MyHashTable:
    # Спеціальний маркер для Lazy Deletion (видалення) 
    _DELETED = object()

    def save_to_json(self, filename="data.json"):
        # Перетворюємо дані таблиці у список словників 
        data_to_save = [{"key": key, "value": value} for key, value in self.items()]
        
        # Визначаємо шлях до файлу за допомогою pathlib 
        file_path = Path(filename)
        
        try:
            console.print(f"[yellow]Starting to write to file {filename}...[/yellow]")  
            # Записуємо у файл 
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            console.print(f"[green]Data successfully saved to {filename}[/green]")  
        except Exception as e:
            console.print(f"[red]Error during saving: {e}[/red]")  

    def load_from_json(self, filename="data.json"):
        file_path = Path(filename)
        
        # Перевірка наявності файлу
        if not file_path.exists():
            console.print(f"[red]Error: File {filename} not found[/red]") 
            return

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Очищуємо поточну таблицю та завантажуємо нові дані 
            self.table = [None] * self.capacity
            self.size = 0
            
            for item in data:
                self.put(item["key"], item["value"])  
            
            console.print(f"[green]Data successfully loaded from {filename}[/green]")  
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[red]Error: File is corrupted or has invalid format ({e})[/red]")

    def __init__(self, capacity=11):
        # Початкова ємність 11 
        self.capacity = capacity
        self.size = 0
        # Масив для зберігання пар (key, value)
        self.table = [None] * self.capacity #none * 11..
        console.print(f"[green]Hash table successfully created with capacity {capacity}[/green]")

    def _is_prime(self, n):
        #Допоміжний метод для перевірки, чи є число простим
        if n < 2: return False
        for i in range(2, int(math.sqrt(n)) + 1): #Load Factor 
#Чи ділиться 100 на щось крім 1 та себе? 2, 3, 4, 5, 6, 7, 8, 9, 10...
# а корінь з 100 - це 10, тому перевіряємо до 10 включно. 
# Якщо знайдемо дільник, то число не просте.
            if n % i == 0: return False
        return True

    def _get_next_prime(self, n):
        #Знаходить найближче просте число, більше за n.
        new_n = n
        while not self._is_prime(new_n):
            new_n += 1
        return new_n

    def _hash1(self, key):
        # Перша хеш-функція: hash(key) % capacity
        #Якщо hash("apple") повернув 25, а capacity у нас 11:
        #25 % 11 = 3
        return hash(key) % self.capacity

    def _hash2(self, key):
        #Рахуємо частину в дужках: 125 % (11 - 1) => 125 % 10 = 5. 
                return 1 + (hash(key) % (self.capacity - 1))
        #Додаємо одиницю: 1 + 5 = 6

    def _resize(self):
        #Динамічне перехешування при LF > 0.7
        console.print(f"[yellow]Starting rehashing... New capacity: {self.capacity * 2}[/yellow]")  
        old_table = self.table
        # Збільшуємо у 2 рази до найближчого простого числа 
        self.capacity = self._get_next_prime(self.capacity * 2)
        self.table = [None] * self.capacity
        self.size = 0
        
        # Переносимо всі існуючі елементи за новими адресами
        for item in old_table:
            if item is not None and item is not self._DELETED:
                self.put(item[0], item[1])
        console.print("[green]Rehashing completed successfully![/green]")
        #Перевіряє розмір логу і архівує його, якщо він > 1 КБ
        log_path = Path("history.log")
        # stat().st_size повертає розмір у байтах (1024 байт = 1 КБ)
        if log_path.exists() and log_path.stat().st_size > 1024:  
            archive_path = Path("history.log.old") 
            log_path.rename(archive_path) 
            console.print("[yellow]Log file exceeded 1 KB and was archived as history.log.old[/yellow]")

    def put(self, key, value):
        # Перевірка Load Factor
        if self.size / self.capacity > 0.7: 
            self._resize()

        h1 = self._hash1(key)
        h2 = self._hash2(key)
        first_deleted_idx = None
        
        for i in range(self.capacity):
            idx = (h1 + i * h2) % self.capacity
            item = self.table[idx]
            
            # ВИПАДОК 1: Знайшли порожнє місце
            if item is None:
                target_idx = first_deleted_idx if first_deleted_idx is not None else idx
                self.table[target_idx] = (key, value)
                
                if first_deleted_idx is None:
                    self.size += 1
                
                # Логування та кольоровий вивід
                self._log_action(f"Added new element: Key={key}") 
                console.print(f"[green]Successfully added: {key}[/green]")
                return

            # ВИПАДОК 2: Знайшли маркер видалення
            if item is self._DELETED:
                if first_deleted_idx is None:
                    first_deleted_idx = idx
                continue

            # ВИПАДОК 3: Ключ уже існує (Оновлення)
            if item[0] == key:
                self.table[idx] = (key, value)
                
                self._log_action(f"Updated existing key: {key}")
                console.print(f"[yellow]Updated value for: {key}[/yellow]") 
                return
        
        raise Exception("Hash table is full")
    
    def _log_action(self, message):
        try:
            self._rotate_logs()  
            log_path = Path("history.log")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with log_path.open("a", encoding="utf-8") as f: 
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            console.print(f"[red]Logging error: {e}[/red]") 

    def get(self, key):
        #Повертає значення за ключем
        h1 = self._hash1(key)
        h2 = self._hash2(key)
        
        for i in range(self.capacity):
            idx = (h1 + i * h2) % self.capacity
            item = self.table[idx]
            
            if item is None:
                break # Ключа точно немає 
            
            if item is not self._DELETED and item[0] == key:
                #item[0] == key:
                #  Якщо ми знайшли комірку, де ключ збігається, ми повертаємо значення (item[1]).
                return item[1]
        console.print(f"[red]Error: Key '{key}' not found[/red]")
        raise KeyError(f"Key '{key}' not found")

    def remove(self, key):
        #Видалення ключа (Lazy Deletion)
        h1 = self._hash1(key)
        h2 = self._hash2(key)
        
        for i in range(self.capacity):
            idx = (h1 + i * h2) % self.capacity
            item = self.table[idx]
            
            if item is None:
                break
                
            if item is not self._DELETED and item[0] == key:
                self.table[idx] = self._DELETED # Ставимо маркер 
                self.size -= 1
                return
                
        raise KeyError(f"Key '{key}' not found")

    # Методи для доступу через квадратні дужки [] 
    def __setitem__(self, key, value):
        self.put(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __len__(self):
        return self.size 

    def __iter__(self):
        #Ітерування по існуючих ключах
        for item in self.table:
            if item is not None and item is not self._DELETED:
                yield item[0]

    def items(self):
        #Генератор пар (key, value)
        for item in self.table:
            if item is not None and item is not self._DELETED:
                yield item


if __name__ == "__main__":
    # Створюємо таблицю з початковою ємністю 7 
    table = MyHashTable(capacity=7)

    print("Test 1: Basic operations (Insert and retrieve)")
    table["apple"] = 10       # Виклик put("apple", 10) 
    table["banana"] = 20      
    table["cherry"] = 30      
    
    print(f"apple: {table['apple']}")    # Очікуємо: 10 
    print(f"Number of elements: {len(table)}") # Очікуємо: 3 

    print("\nTest 2: Updating values")
    table["apple"] = 100      # Оновлення існуючого ключа 
    print(f"apple after update: {table['apple']}") # Очікуємо: 100 

    print("\nTest 3: Deletion and Lazy Deletion")
    # Видаляємо "banana", на місці має з'явитися маркер _DELETED 
    table.remove("banana")
    try:
        print(table["banana"])
    except KeyError:
        print("Key 'banana' successfully deleted (KeyError raised)")

    # Перевірка, що пошук "cherry" працює крізь DELETED комірку 
    print(f"cherry after deleting banana: {table['cherry']}") # Очікуємо: 30

    print("\nTest 4: Iteration")
    keys_found = []
    for key in table:         # Виклик __iter__ 
        keys_found.append(key)
    print(f"Found keys: {keys_found}") # Має бути без 'banana'  

    print("\nTest 5: Rehashing")
    print(f"Capacity before expansion: {table.capacity}")
    
    # Додаємо елементи, щоб перевищити Load Factor (0.7 * 7 = 4.9)
    table["date"] = 40        # 4-й елемент
    table["elderberry"] = 50  # 5-й елемент -> має відбутися resize 
    table["fig"] = 60         

    print(f"Capacity after rehashing: {table.capacity}") # Очікуємо збільшення   
    print(f"cherry after rehashing: {table['cherry']}") # Очікуємо: 30  
    print(f"Total number of elements: {len(table)}") 