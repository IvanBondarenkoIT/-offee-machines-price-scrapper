"""
Тест локального Railway сервера
"""
import requests
import sys
import io

# Windows console encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8080"

def test_endpoint(name, url, expected_status=200):
    """Test single endpoint"""
    print(f"\n{'='*60}")
    print(f"Тест: {name}")
    print(f"URL: {url}")
    print('='*60)
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Статус: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ УСПЕХ!")
            
            # Print response content
            if 'application/json' in response.headers.get('Content-Type', ''):
                import json
                print(f"\nОтвет (JSON):")
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            elif 'text/html' in response.headers.get('Content-Type', ''):
                print(f"\nОтвет: HTML страница ({len(response.text)} символов)")
                # Print first 500 chars
                print(response.text[:500])
            else:
                print(f"\nТип: {response.headers.get('Content-Type')}")
                print(f"Размер: {len(response.content)} байт")
        else:
            print(f"❌ ОШИБКА! Ожидался {expected_status}, получен {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ ИСКЛЮЧЕНИЕ: {e}")

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 ТЕСТИРОВАНИЕ RAILWAY API (ЛОКАЛЬНО)")
    print("="*60)
    
    # Test all endpoints
    test_endpoint("1. Главная страница", f"{BASE_URL}/")
    test_endpoint("2. Статус системы", f"{BASE_URL}/status")
    test_endpoint("3. Список отчетов", f"{BASE_URL}/reports/list")
    test_endpoint("4. Health check", f"{BASE_URL}/health")
    test_endpoint("5. Последний Excel", f"{BASE_URL}/reports/latest/excel")
    test_endpoint("6. Последний Word", f"{BASE_URL}/reports/latest/word")
    test_endpoint("7. Последний PDF", f"{BASE_URL}/reports/latest/pdf")
    
    # Final summary
    print("\n" + "="*60)
    print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("="*60)
    print(f"\n🌐 Откройте в браузере: {BASE_URL}")
    print("\n💡 Если всё работает локально, то будет работать и на Railway!")

if __name__ == "__main__":
    main()

