"""
Simple i18n helper for translations
This is a simple implementation before Babel is fully set up
"""
from flask import session, current_app

# Translation dictionaries
TRANSLATIONS = {
    'en': {
        # Navigation
        'Dashboard': 'Dashboard',
        'Price Comparison': 'Price Comparison',
        'History': 'History',
        'Users': 'Users',
        'User Management': 'User Management',
        'Create User': 'Create User',
        'Edit User': 'Edit User',
        'Back to List': 'Back to List',
        'Username': 'Username',
        'Email': 'Email',
        'Password': 'Password',
        'Role': 'Role',
        'Created': 'Created',
        'Last Login': 'Last Login',
        'Actions': 'Actions',
        'Edit': 'Edit',
        'Delete': 'Delete',
        'Cancel': 'Cancel',
        'Create': 'Create',
        'Update': 'Update',
        'Viewer': 'Viewer',
        'Manager': 'Manager',
        'Admin': 'Admin',
        'Read-only access': 'Read-only access',
        'View and export data': 'View and export data',
        'Full access': 'Full access',
        'Logout': 'Logout',
        'Never': 'Never',
        'No users found': 'No users found',
        'Please fill all required fields': 'Please fill all required fields',
        'Username or email already exists': 'Username or email already exists',
        'User created successfully': 'User created successfully',
        'User updated successfully': 'User updated successfully',
        'User %(username)s deleted successfully': 'User %(username)s deleted successfully',
        'You cannot change your own role': 'You cannot change your own role',
        'You cannot delete your own account': 'You cannot delete your own account',
        'Are you sure you want to delete this user?': 'Are you sure you want to delete this user?',
        'leave empty to keep current password': 'leave empty to keep current password',
        
        # Dashboard
        'Total Products': 'Total Products',
        'In inventory': 'In inventory',
        'Total Value': 'Total Value',
        'GEL': 'GEL',
        'We are Cheaper': 'We are Cheaper',
        'Products': 'Products',
        'Last Update': 'Last Update',
        'Top Products (Most Competitors)': 'Top Products (Most Competitors)',
        'Model': 'Model',
        'Our Price': 'Our Price',
        'Competitors': 'Competitors',
        'Status': 'Status',
        'Cheaper': 'Cheaper',
        'Recent Uploads': 'Recent Uploads',
        'products': 'products',
        
        # Comparison
        'Export Excel': 'Export Excel',
        'PDF Report': 'PDF Report',
        'Filters': 'Filters',
        'No Comparison Data Available': 'No Comparison Data Available',
        'Upload your price comparison file to see the data': 'Upload your price comparison file to see the data',
        
        # History
        'Upload History': 'Upload History',
        'Date': 'Date',
        'Uploaded At': 'Uploaded At',
        'Total Value': 'Total Value',
        'Avg Price': 'Avg Price',
        'Status': 'Status',
        'Completed': 'Completed',
        'Processing': 'Processing',
        'Failed': 'Failed',
        'View': 'View',
        'No History Available': 'No History Available',
        'Upload price comparison files to build your history': 'Upload price comparison files to build your history',
        
        # Auth
        'Login to access the dashboard': 'Login to access the dashboard',
        'Enter username': 'Enter username',
        'Enter password': 'Enter password',
        'Remember me': 'Remember me',
        'Login': 'Login',
    },
    'ru': {
        # Navigation
        'Dashboard': 'Панель управления',
        'Price Comparison': 'Сравнение цен',
        'History': 'История',
        'Users': 'Пользователи',
        'User Management': 'Управление пользователями',
        'Create User': 'Создать пользователя',
        'Edit User': 'Редактировать пользователя',
        'Back to List': 'Вернуться к списку',
        'Username': 'Имя пользователя',
        'Email': 'Электронная почта',
        'Password': 'Пароль',
        'Role': 'Роль',
        'Created': 'Создан',
        'Last Login': 'Последний вход',
        'Actions': 'Действия',
        'Edit': 'Редактировать',
        'Delete': 'Удалить',
        'Cancel': 'Отмена',
        'Create': 'Создать',
        'Update': 'Обновить',
        'Viewer': 'Просмотр',
        'Manager': 'Менеджер',
        'Admin': 'Администратор',
        'Read-only access': 'Только чтение',
        'View and export data': 'Просмотр и экспорт данных',
        'Full access': 'Полный доступ',
        'Logout': 'Выйти',
        'Never': 'Никогда',
        'No users found': 'Пользователи не найдены',
        'Please fill all required fields': 'Заполните все обязательные поля',
        'Username or email already exists': 'Имя пользователя или email уже существует',
        'User created successfully': 'Пользователь успешно создан',
        'User updated successfully': 'Пользователь успешно обновлен',
        'User %(username)s deleted successfully': 'Пользователь %(username)s успешно удален',
        'You cannot change your own role': 'Вы не можете изменить свою роль',
        'You cannot delete your own account': 'Вы не можете удалить свою учетную запись',
        'Are you sure you want to delete this user?': 'Вы уверены, что хотите удалить этого пользователя?',
        'leave empty to keep current password': 'оставьте пустым, чтобы сохранить текущий пароль',
        
        # Dashboard
        'Total Products': 'Всего товаров',
        'In inventory': 'В остатках',
        'Total Value': 'Общая стоимость',
        'GEL': 'GEL',
        'We are Cheaper': 'Мы дешевле',
        'Products': 'Товаров',
        'Last Update': 'Последнее обновление',
        'Top Products (Most Competitors)': 'Топ товаров (больше всего конкурентов)',
        'Model': 'Модель',
        'Our Price': 'Наша цена',
        'Competitors': 'Конкуренты',
        'Status': 'Статус',
        'Cheaper': 'Дешевле',
        'Recent Uploads': 'Недавние загрузки',
        'products': 'товаров',
        
        # Comparison
        'Export Excel': 'Экспорт Excel',
        'PDF Report': 'PDF Отчет',
        'Filters': 'Фильтры',
        'No Comparison Data Available': 'Нет данных для сравнения',
        'Upload your price comparison file to see the data': 'Загрузите файл сравнения цен, чтобы увидеть данные',
        
        # History
        'Upload History': 'История загрузок',
        'Date': 'Дата',
        'Uploaded At': 'Загружено',
        'Total Value': 'Общая стоимость',
        'Avg Price': 'Средняя цена',
        'Status': 'Статус',
        'Completed': 'Завершено',
        'Processing': 'Обработка',
        'Failed': 'Ошибка',
        'View': 'Просмотр',
        'No History Available': 'История недоступна',
        'Upload price comparison files to build your history': 'Загружайте файлы сравнения цен для создания истории',
        
        # Auth
        'Login to access the dashboard': 'Войдите для доступа к панели управления',
        'Enter username': 'Введите имя пользователя',
        'Enter password': 'Введите пароль',
        'Remember me': 'Запомнить меня',
        'Login': 'Войти',
    },
    'ka': {
        # Navigation
        'Dashboard': 'დეშბორდი',
        'Price Comparison': 'ფასების შედარება',
        'History': 'ისტორია',
        'Users': 'მომხმარებლები',
        'User Management': 'მომხმარებლების მართვა',
        'Create User': 'მომხმარებლის შექმნა',
        'Edit User': 'მომხმარებლის რედაქტირება',
        'Back to List': 'სიაში დაბრუნება',
        'Username': 'მომხმარებლის სახელი',
        'Email': 'ელფოსტა',
        'Password': 'პაროლი',
        'Role': 'როლი',
        'Created': 'შექმნილია',
        'Last Login': 'ბოლო შესვლა',
        'Actions': 'მოქმედებები',
        'Edit': 'რედაქტირება',
        'Delete': 'წაშლა',
        'Cancel': 'გაუქმება',
        'Create': 'შექმნა',
        'Update': 'განახლება',
        'Viewer': 'ნახვა',
        'Manager': 'მენეჯერი',
        'Admin': 'ადმინისტრატორი',
        'Read-only access': 'მხოლოდ ნახვა',
        'View and export data': 'მონაცემების ნახვა და ექსპორტი',
        'Full access': 'სრული წვდომა',
        'Logout': 'გასვლა',
        'Never': 'არასოდეს',
        'No users found': 'მომხმარებლები არ მოიძებნა',
        'Please fill all required fields': 'გთხოვთ შეავსოთ ყველა სავალდებულო ველი',
        'Username or email already exists': 'მომხმარებლის სახელი ან ელფოსტა უკვე არსებობს',
        'User created successfully': 'მომხმარებელი წარმატებით შეიქმნა',
        'User updated successfully': 'მომხმარებელი წარმატებით განახლდა',
        'User %(username)s deleted successfully': 'მომხმარებელი %(username)s წარმატებით წაიშალა',
        'You cannot change your own role': 'თქვენ არ შეგიძლიათ თქვენი საკუთარი როლის შეცვლა',
        'You cannot delete your own account': 'თქვენ არ შეგიძლიათ თქვენი საკუთარი ანგარიშის წაშლა',
        'Are you sure you want to delete this user?': 'დარწმუნებული ხართ, რომ გსურთ ამ მომხმარებლის წაშლა?',
        'leave empty to keep current password': 'დატოვეთ ცარიელი მიმდინარე პაროლის შესანარჩუნებლად',
        
        # Dashboard
        'Total Products': 'სულ პროდუქტი',
        'In inventory': 'ნაშთებში',
        'Total Value': 'საერთო ღირებულება',
        'GEL': 'GEL',
        'We are Cheaper': 'ჩვენ უფრო იაფი ვართ',
        'Products': 'პროდუქტი',
        'Last Update': 'ბოლო განახლება',
        'Top Products (Most Competitors)': 'ტოპ პროდუქტები (უმეტესი კონკურენტი)',
        'Model': 'მოდელი',
        'Our Price': 'ჩვენი ფასი',
        'Competitors': 'კონკურენტები',
        'Status': 'სტატუსი',
        'Cheaper': 'იაფი',
        'Recent Uploads': 'ბოლო ატვირთვები',
        'products': 'პროდუქტი',
        
        # Comparison
        'Export Excel': 'Excel-ის ექსპორტი',
        'PDF Report': 'PDF ანგარიში',
        'Filters': 'ფილტრები',
        'No Comparison Data Available': 'შედარების მონაცემები არ არის ხელმისაწვდომი',
        'Upload your price comparison file to see the data': 'ატვირთეთ თქვენი ფასების შედარების ფაილი მონაცემების სანახავად',
        
        # History
        'Upload History': 'ატვირთვების ისტორია',
        'Date': 'თარიღი',
        'Uploaded At': 'ატვირთულია',
        'Total Value': 'საერთო ღირებულება',
        'Avg Price': 'საშუალო ფასი',
        'Status': 'სტატუსი',
        'Completed': 'დასრულებული',
        'Processing': 'მუშავდება',
        'Failed': 'შეცდომა',
        'View': 'ნახვა',
        'No History Available': 'ისტორია არ არის ხელმისაწვდომი',
        'Upload price comparison files to build your history': 'ატვირთეთ ფასების შედარების ფაილები ისტორიის შესაქმნელად',
        
        # Auth
        'Login to access the dashboard': 'შედით დეშბორდზე წვდომისთვის',
        'Enter username': 'შეიყვანეთ მომხმარებლის სახელი',
        'Enter password': 'შეიყვანეთ პაროლი',
        'Remember me': 'დამახსოვრება',
        'Login': 'შესვლა',
    }
}

def get_translation(key, language=None):
    """
    Get translation for a key
    
    Args:
        key: Translation key
        language: Language code (en, ru, ka). If None, uses session language
    
    Returns:
        str: Translated string or key if not found
    """
    if language is None:
        from flask import session
        language = session.get('language', 'en')
    
    return TRANSLATIONS.get(language, TRANSLATIONS['en']).get(key, key)

def gettext(key):
    """Alias for get_translation for Flask-Babel compatibility"""
    return get_translation(key)

