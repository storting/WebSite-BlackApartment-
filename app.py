from flask import Flask, render_template, request
from config import Config
import json, os, re, phonenumbers
from datetime import datetime

app = Flask(__name__)

USERS_FILE = 'users.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log')
def login():
    return render_template('login.html')

@app.route('/reg', methods=['GET', 'POST'])
def register():
    
    return render_template('register.html')
    
@app.route('/sumbit/<string:form_type>', methods=['POST'])
def sumbit(form_type):
    
    if(form_type == 'tenant'):
        user_data = {
                'TYPE' : f'{form_type}',
                'username': request.form.get('username', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'name': request.form.get('name', '').strip(),
                'password': request.form.get('password', '').strip()
            }
        json_str = json.dumps(user_data, ensure_ascii=False, indent=4)
        print(json_str)
    if(form_type == 'landlord'):
        user_data = {
                'TYPE' : f'{form_type}',
                'username': request.form.get('username', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'name': request.form.get('name', '').strip(),
                'birth_date': request.form.get('birth_date', '').strip(),
                'password': request.form.get('password', '').strip(),
                'last_login': None,
                'is_active': True,
                'role': 'landlord',
                'email_verified': False,
                'properties': [],
                'documents': [],
                'balance': 0.0,
                'rating': 0.0,
                'verified': False
            }
        json_str = json.dumps(user_data, ensure_ascii=False, indent=4)
        users[username] = user_data
        save_users(users)
        print(json_str)
    return render_template('register.html')

@app.route('/apart')
def apart():
    return render_template('apartments.html')

@app.route("/apart/det/<int:id>")
def apart_det(id):
    print(id)
    return render_template('apartment-detail.html')

def save_users(users_dict):
    """Сохраняем пользователей в JSON файл"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_dict, f, ensure_ascii=False, indent=4)

def load_users():
    """Загружаем пользователей из JSON файла"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def validate_registration(data):
    """Валидация данных регистрации"""
    errors = {}
    
    if(data.TYPE == "tenant"):
        # Проверка имени пользователя
        username = data.get('username', '').strip()
        if not username:
            errors['username'] = 'Имя пользователя обязательно'
        elif len(username) < 3:
            errors['username'] = 'Имя должно быть не менее 3 символов'
        elif len(username) > 20:
            errors['username'] = 'Имя должно быть не более 20 символов'
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors['username'] = 'Имя может содержать только буквы, цифры и _'
        
        # Проверка email
        email = data.get('email', '').strip()
        if not email:
            errors['email'] = 'Email обязателен'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Неверный формат email'
        
        # Проверка phone
        phone = data.get('phone', '').strip()
        if not phone:
            errors['phone'] = 'телефон обязателен'
        else:
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            parsed = phonenumbers.parse(cleaned_phone, None)
        if not phonenumbers.is_valid_number(parsed):
            errors['phone'] = 'Неверный номер телефона'

        # Проверка имени
        full_name = data.get('name', '').strip()
        if not full_name:
            errors['name'] = 'Имя обязательно'
        elif len(full_name) < 2:
            errors['name'] = 'Имя должно быть не менее 2 символов'
        
        # Проверка пароля
        password = data.get('password', '')
        if not password:
            errors['password'] = 'Пароль обязателен'
        elif len(password) < 8:
            errors['password'] = 'Пароль должен быть не менее 8 символов'
        elif not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            errors['password'] = 'Пароль должен содержать буквы и цифры'
        
        # Проверка подтверждения пароля
        confirm_password = data.get('confirmPassword', '')
        if not confirm_password:
            errors['confirmPassword'] = 'Подтверждение пароля обязательно'
        elif password != confirm_password:
            errors['confirmPassword'] = 'Пароли не совпадают'

        # Проверка чекбокса
        # if not data.get('terms'):
        #     errors['terms'] = 'Вы должны принять условия'
        
        # Проверка уникальности
        users = load_users()
        if username in users:
            errors['username'] = 'Это имя пользователя уже занято'
        
        if any(user['email'] == email for user in users.values()):
            errors['email'] = 'Этот email уже зарегистрирован'
        
        return errors
    if(data.TYPE == "landlord"):
        # Проверка имени пользователя
        username = data.get('username', '').strip()
        if not username:
            errors['username'] = 'Имя пользователя обязательно'
        elif len(username) < 3:
            errors['username'] = 'Имя должно быть не менее 3 символов'
        elif len(username) > 20:
            errors['username'] = 'Имя должно быть не более 20 символов'
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            errors['username'] = 'Имя может содержать только буквы, цифры и _'
        
        # Проверка email
        email = data.get('email', '').strip()
        if not email:
            errors['email'] = 'Email обязателен'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Неверный формат email'
        
        # Проверка пароля
        password = data.get('password', '')
        if not password:
            errors['password'] = 'Пароль обязателен'
        elif len(password) < 8:
            errors['password'] = 'Пароль должен быть не менее 8 символов'
        elif not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            errors['password'] = 'Пароль должен содержать буквы и цифры'
        
        # Проверка подтверждения пароля
        confirm_password = data.get('confirmPassword', '')
        if not confirm_password:
            errors['confirmPassword'] = 'Подтверждение пароля обязательно'
        elif password != confirm_password:
            errors['confirmPassword'] = 'Пароли не совпадают'
        
        # Проверка имени
        full_name = data.get('name', '').strip()
        if not full_name:
            errors['name'] = 'Имя обязательно'
        elif len(full_name) < 2:
            errors['name'] = 'Имя должно быть не менее 2 символов'
        
        # Проверка чекбокса
        # if not data.get('terms'):
        #     errors['terms'] = 'Вы должны принять условия'
        
        # Проверка уникальности
        users = load_users()
        if username in users:
            errors['username'] = 'Это имя пользователя уже занято'
        
        if any(user['email'] == email for user in users.values()):
            errors['email'] = 'Этот email уже зарегистрирован'
        
        return errors


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')