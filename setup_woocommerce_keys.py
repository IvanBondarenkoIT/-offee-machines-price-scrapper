"""
Безопасная настройка WooCommerce API ключей
Создает .env файл локально, который НЕ попадет в Git
"""

import os
from pathlib import Path

def setup_keys():
    """Интерактивная настройка WooCommerce ключей"""
    print("="*80)
    print("НАСТРОЙКА WOOCOMMERCE API КЛЮЧЕЙ")
    print("="*80)
    print("\nЭтот скрипт создаст локальный .env файл с вашими ключами.")
    print("Файл .env уже в .gitignore и НЕ попадет в Git.\n")
    
    # Проверка существующего файла
    env_file = Path('.env')
    if env_file.exists():
        print("[WARNING] Файл .env уже существует!")
        response = input("Перезаписать? (yes/no): ").strip().lower()
        if response != 'yes':
            print("[CANCEL] Отменено")
            return
    
    # Ввод данных
    print("\nВведите данные (нажмите Enter для пропуска существующих значений):")
    print("-"*80)
    
    url = input("WC_URL [https://dimkava.ge]: ").strip()
    if not url:
        url = "https://dimkava.ge"
    
    consumer_key = input("WC_CONSUMER_KEY (ck_...): ").strip()
    if not consumer_key:
        print("[ERROR] Consumer Key обязателен!")
        return
    
    consumer_secret = input("WC_CONSUMER_SECRET (cs_...): ").strip()
    if not consumer_secret:
        print("[ERROR] Consumer Secret обязателен!")
        return
    
    api_version = input("WC_API_VERSION [wc/v3]: ").strip()
    if not api_version:
        api_version = "wc/v3"
    
    # Чтение существующего .env если есть
    existing_lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
    
    # Подготовка новых строк
    new_lines = []
    wc_vars = {
        'WC_URL': url,
        'WC_CONSUMER_KEY': consumer_key,
        'WC_CONSUMER_SECRET': consumer_secret,
        'WC_API_VERSION': api_version
    }
    
    # Обновить или добавить WooCommerce переменные
    wc_found = {key: False for key in wc_vars.keys()}
    
    for line in existing_lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith('#'):
            new_lines.append(line)
            continue
        
        # Проверить, есть ли уже эта переменная
        for key, value in wc_vars.items():
            if line_stripped.startswith(f'{key}='):
                new_lines.append(f'{key}={value}\n')
                wc_found[key] = True
                break
        else:
            # Сохранить другие переменные
            new_lines.append(line)
    
    # Добавить недостающие переменные
    if not any(wc_found.values()):
        # Добавить заголовок если это новый файл
        if not any('WooCommerce' in line for line in new_lines):
            new_lines.append('\n# WooCommerce API (для экспорта данных, опционально)\n')
    
    for key, value in wc_vars.items():
        if not wc_found[key]:
            new_lines.append(f'{key}={value}\n')
    
    # Записать файл
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print("\n" + "="*80)
        print("[OK] Файл .env создан/обновлен успешно!")
        print("="*80)
        print(f"\nСохранено:")
        print(f"  WC_URL: {url}")
        print(f"  WC_CONSUMER_KEY: {consumer_key[:15]}...")
        print(f"  WC_CONSUMER_SECRET: {consumer_secret[:15]}...")
        print(f"  WC_API_VERSION: {api_version}")
        print("\n[SECURITY] Файл .env в .gitignore и не попадет в Git")
        print("\nТеперь можно запустить: python test_woocommerce_client.py")
        
    except Exception as e:
        print(f"\n[ERROR] Ошибка при записи файла: {e}")

if __name__ == "__main__":
    setup_keys()
