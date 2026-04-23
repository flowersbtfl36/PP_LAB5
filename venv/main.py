from rich.console import Console
from structures import MyHashTable, BinarySearchTree
from datetime import datetime

# Створюємо об'єкт консолі для кольорового виводу
console = Console()

def main():
    console.rule("[bold blue]Лабораторна робота №5: Архітектура проєкту[/bold blue]")

    console.print("\n[bold yellow]Крок 1: Тестування MyHashTable[/bold yellow]")
    
    try:
        ht = MyHashTable(capacity=5)
    except Exception as e:
        console.print(f"[red]Помилка при створенні таблиці: {e}[/red]")

    console.print("[yellow]Додавання даних у хеш-таблицю...[/yellow]")
    ht["apple"] = 10
    ht["banana"] = 20
    console.print(f"[green]Успішно додано 'apple' та 'banana'[/green]")

    # Тест помилки (Червоний - error)
    console.print("[yellow]Перевірка пошуку відсутнього ключа:[/yellow]")
    try:
        _ = ht["cherry"]
    except KeyError:
        console.print("[red]Ключ 'cherry' не знайдено (Помилка оброблена успішно)[/red]")


    console.print("\n[bold yellow]Тестування BinarySearchTree[/bold yellow]")
    
    try:
        tree = BinarySearchTree()
    except Exception as e:
        console.print(f"[red]Помилка при створенні дерева: {e}[/red]")

    # Вставка транзакції
    test_ts = datetime.now().timestamp()
    console.print(f"[yellow]Початок тестування методу insert для дерева...[/yellow]")
    tree.insert(test_ts, {"amount": 500, "desc": "Тестова транзакція"})
    console.print(f"[green]Транзакцію успішно додано в дерево[/green]")

    console.rule("[bold blue]Тестування завершено[/bold blue]")

if __name__ == "__main__":
    main()