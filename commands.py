import json

def load_commands_from_json():
    try:
        with open("commands.json", "r", encoding="utf-8") as f:
            commands = json.load(f)
            print("Команды успешно загружены из файла.")
            return commands
    except FileNotFoundError:
        print("Ошибка: файл 'commands.json' не найден.")
        return {}
    except json.JSONDecodeError:
        print("Ошибка: не удается декодировать JSON в файле 'commands.json'.")
        return {}
    except Exception as e:
        print(f"Неизвестная ошибка при загрузке команд: {e}")
        return {}

# Загрузка команд из файла JSON
commands = load_commands_from_json()

# Печать содержимого команд для проверки
print(commands)
