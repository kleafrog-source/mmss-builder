import os
import sys

TARGET_DIR = r"D:\AMMS-Vault"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "directory_structure.txt")

def human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            if unit == 'B':
                return f"{int(size_bytes)} {unit}"
            else:
                return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def dump_clean_structure(root, output_file):
    root_abs = os.path.abspath(root)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Структура: {root_abs}\n")
        f.write("="*60 + "\n\n")

        # Соберём все относительные пути файлов для быстрой проверки
        file_paths = set()
        dir_paths = set()

        for dirpath, dirnames, filenames in os.walk(root_abs):
            rel_dir = os.path.relpath(dirpath, root_abs)
            if rel_dir == ".":
                rel_dir = ""
            dir_paths.add(rel_dir if rel_dir else ".")

            for filename in filenames:
                rel_file = os.path.relpath(os.path.join(dirpath, filename), root_abs)
                file_paths.add(rel_file)

        # Отсортируем всё для предсказуемого порядка
        all_items = sorted(file_paths | dir_paths)

        # Выводим каждый элемент
        for item in all_items:
            if item in file_paths:
                # Это файл
                abs_path = os.path.join(root_abs, item)
                try:
                    size = os.path.getsize(abs_path)
                except (OSError, FileNotFoundError):
                    size = 0
                size_str = human_readable_size(size)
                f.write(f"{item} size: {size_str}\n")
            else:
                # Это папка (возможно, пустая)
                if item == ".":
                    continue  # корень не выводим отдельно — файлы и так от корня
                f.write(f"{item}\n")

if __name__ == "__main__":
    if not os.path.exists(TARGET_DIR):
        print(f"[Ошибка] Директория не найдена: {TARGET_DIR}")
        sys.exit(1)

    print(f"Генерация чистой структуры → {OUTPUT_FILE}")
    dump_clean_structure(TARGET_DIR, OUTPUT_FILE)
    print("Готово.")