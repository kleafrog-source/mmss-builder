"""
Запуск Flask приложения MMSS System
"""

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("MMSS System - Запуск веб-сервера")
    print("=" * 60)
    print("\nСервер будет доступен по адресу:")
    print("  http://localhost:5000")
    print("  http://127.0.0.1:5000")
    print("\nДля остановки нажмите Ctrl+C")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)





