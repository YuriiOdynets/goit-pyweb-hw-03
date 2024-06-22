import shutil
from pathlib import Path
import concurrent.futures
import sys
import logging
from time import time
from threading import current_thread

# Налаштування логування
logger = logging.getLogger()
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

# Опис логіки копіювання файлів
def copy_file(file_path, destination_directory):
    file_extension = file_path.suffix.lstrip('.').lower()
    if file_extension:
        destination_path = destination_directory / file_extension
        destination_path.mkdir(parents=True, exist_ok=True)
        shutil.copy(file_path, destination_path / file_path.name)
        logger.debug(f"Thread {current_thread().name} copied {file_path} to {destination_path / file_path.name}")
    logger.debug(f"Thread {current_thread().name} has finished copying {file_path}")

# Опис логіки обробки директорій
def process_directory(source_dir, destination_dir):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for item in source_dir.iterdir():
            if item.is_dir():
                # Обробляємо піддиректорії в окремих потоках
                futures.append(executor.submit(process_directory, item, destination_dir))
                logger.debug(f"Thread {current_thread().name} is processing directory {item}")
            else:
                # Копіюємо файли в окремих потоках
                futures.append(executor.submit(copy_file, item, destination_dir))
                logger.debug(f"Thread {current_thread().name} is processing file {item}")
        
        for future in concurrent.futures.as_completed(futures):
            future.result()
    logger.debug(f"Thread {current_thread().name} has finished processing directory {source_dir}")

if __name__ == '__main__':
    # Введення шляхів до директорій через input або аргументи командного рядка
    if len(sys.argv) >= 2:
        source_dir = Path(sys.argv[1])
    else:
        source_dir = Path(input("Enter the path to the source directory: "))
    
    if len(sys.argv) >= 3:
        dest_dir = Path(sys.argv[2])
    else:
        dest_dir = Path(input("Enter the path to the destination directory (default is 'dist'): ") or 'dist')

    # Перевірка існування директорій
    if not source_dir.exists() or not source_dir.is_dir():
        logger.error(f"Source directory {source_dir} does not exist or is not a directory.")
        sys.exit(1)

    if not dest_dir.exists():
        dest_dir.mkdir(parents=True)

    start_time = time()  # Початок відліку часу виконання після введення шляхів сорс і дест 

    # Обробка директорії
    process_directory(source_dir, dest_dir)

    end_time = time()  # Кінець відліку часу виконання
    elapsed_time = end_time - start_time
    logger.debug(f"All files have been processed. Time taken: {elapsed_time:.5f} seconds.")