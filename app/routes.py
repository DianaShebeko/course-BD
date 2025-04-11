from flask import request, render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, login_required, logout_user
from app import app
from app.forms import RegistrationForm, LoginForm, CategoryForm
from app.user import User
import psycopg
from flask_wtf import FlaskForm

@app.route('/testdb')
def test_connection():
    con = None
    message = ""
    try:
        con = psycopg.connect(host=app.config['DB_SERVER'],
                              user=app.config['DB_USER'],
                              password=app.config['DB_PASSWORD'],
                              dbname=app.config['DB_NAME'])
    except Exception as e:
        message = f"Ошибка подключения: {e}"
    else:
        message = "Подключение успешно"
    finally:
        if con:
            con.close()
        return message

@app.route('/', methods=['GET'])
def index():
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()
    return render_template('index.html')

#Регистрация в системе
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        login = reg_form.login.data
        password_hash = generate_password_hash(reg_form.password.data)
        phone = reg_form.phone.data
        name = reg_form.name.data
        with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
            cur = con.cursor()
            cur.execute('INSERT INTO appuser (login, name, phone, password)'
                        'VALUES (%s, %s, %s, %s)',
                        (login,name, phone, password_hash))
        flash(f'Регистрация {reg_form.login.data} завершена. Можете войти в систему.')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Регистрация пользователя', form=reg_form)

#Вход в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if current_user.is_authenticated:
        print(f"Уже авторизован")
        return redirect(url_for('index'))
    if login_form.validate_on_submit():
        with psycopg.connect(
            host=app.config['DB_SERVER'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            dbname=app.config['DB_NAME']) as con:
            cur = con.cursor()

            res = cur.execute('SELECT Login, Name, Phone, Password '
                              'FROM AppUser '
                              'WHERE Login = %s', (login_form.username.data,)).fetchone()
        if res is None or not check_password_hash(res[3], login_form.password.data):
            flash('Попытка входа неудачна', 'danger')
            return redirect(url_for('login'))

        login, name, phone, password = res
        user = User(login, name, phone, password)
        login_user(user, remember=login_form.remember_me.data)
        flash(f'Вы успешно вошли в систему, {user.name}', 'success')
        return redirect(url_for('user_profile', user_login=login))
    return render_template('login.html', title='Вход', form=login_form)

#Выход из аккаунта
from app import app
from flask_login import logout_user
from flask import redirect, url_for

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


#Редактирование профиля
from app import app
from app.forms import EditUserForm
from flask import render_template, redirect, flash, url_for
import urllib.parse


from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from psycopg import connect
from app.forms import EditUserForm

#Редактирование пользователя
@app.route('/edituser/<user_login>', methods=['GET', 'POST'])
@login_required
def edit_user(user_login):
    if user_login != current_user.login:
         flash('У вас нет прав для редактирования этого пользователя.', 'danger')
         return redirect(url_for('index'))
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME'],
                         ) as con:
        cur = con.cursor()
        cur.execute('SELECT name, phone, password '
                      'FROM appuser '
                     'WHERE login = %s', (user_login,))
        
        user_data = cur.fetchone()

        print(user_data)
        name, ph, passw = user_data

        form = EditUserForm(name=name, phone=ph, password=passw)
        if form.validate_on_submit():
            name = form.name.data
            ph = form.phone.data
            passw = form.password.data

            print(name)
            
            cur.execute('UPDATE AppUser SET name = %s, phone =%s, password=%s WHERE login =%s',
                            (name, ph, passw, user_login))
            flash('Изменения сохранены')
            return redirect(url_for('user_profile', user_login=user_login))
        else:
            print("Форма не прошла валидацию")
            print(form.errors) 

    return render_template('eduser.html', form=form, user_login = user_login)

#____________________ОБЪЯВЛЕНИЯ__________________________
#Создание объявления
from app.forms import CreateAd
from flask import request, render_template

@app.route('/<user_login>/create_ad', methods=['GET', 'POST'])
@login_required
def create_ad(user_login):
    if user_login != current_user.login:
         flash('У вас нет прав для редактирования этого пользователя.', 'danger')
         return redirect(url_for('index'))

    form = CreateAd()
    category = request.args.get('category', '')
    manufacturer = request.args.get('manufacturer', '')

    if category:
        form.category.data = category
    if manufacturer:
        form.manufacturer.data = manufacturer

    if form.validate_on_submit():
        category = form.category.data
        print(category)
        manufacturer = form.manufacturer.data
        title = form.title.data
        price = form.price.data
        description = form.description.data
        with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
            cur = con.cursor()
            cur.execute('INSERT INTO ad (userlogin, equipmenttypename, manufacturername, title, price, description)'
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (user_login, category, manufacturer, title, price, description))
        flash(f'Карточка создалась.')
        return redirect(url_for('user_profile', user_login = user_login))
    return render_template('createad.html', title='Создание объявления', form=form, user_login = user_login)

#Редактирование объявления
from app.forms import CreateAd
@app.route('/ad/<user_login>/<adid>/edit', methods=['GET', 'POST'])
@login_required
def editad(user_login, adid):
    if user_login != current_user.login:
         flash('У вас нет прав для редактирования этого объявления.', 'danger')
         return redirect(url_for('index'))
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME'],
                         ) as con:
        cur = con.cursor()
        cur.execute('SELECT equipmenttypename, manufacturername,  title, price, description '
                      'FROM ad '
                     'WHERE id = %s', (adid,))
        
        ad_data = cur.fetchone()
        category, manufacturer, title, price, description = ad_data

        form = CreateAd(category=category, manufacturer=manufacturer, title=title, price=price, description=description)
        if form.validate_on_submit():
            category = form.category.data
            manufacturer = form.manufacturer.data
            title = form.title.data
            price = form.price.data
            description = form.description.data
            
            cur.execute('UPDATE Ad SET equipmenttypename = %s, manufacturername  = %s,  title  = %s, price  = %s, description  = %s WHERE id =%s',
                            (category, manufacturer, title, price, description, adid))
            flash('Изменения сохранены')
            return redirect(url_for('ad_card', ad_id=adid))
        else:
            print("Форма не прошла валидацию")
            print(form.errors) 

    return render_template('edcard.html', adid = adid, form=form, user_login = user_login)

#Удаление объявления
@app.route('/delete_ad/<adid>/<user_login>', methods=['POST'])
@login_required
def deletead(adid, user_login):
    #Проверка доступа для удаления
    if user_login != current_user.login:
         flash('У вас нет прав для удаления этого объявления.', 'danger')
         return redirect(url_for('index'))
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME'],
                         ) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM ad WHERE id = %s", (adid,))
        con.commit()
    cur.close()
    con.close()
    flash('Объявление успешно удалено')
    return redirect(url_for('user_profile', user_login=user_login))

#Просмотр всех карточек
from flask import request, render_template
from app.forms import CategoryForm  

@app.route('/ads', methods=['GET', 'POST'])
def ads():
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME'],
                         ) as con:
        cur = con.cursor()

        category = cur.execute('SELECT name FROM EquipmentType ').fetchall()
        manufacturer = cur.execute('SELECT name FROM Manufacturer').fetchall()

        category_choices = [(str(i), gen[0]) for i, gen in enumerate(category, 1)]
    
        form = CategoryForm()
        form.category.choices = category_choices


        selected_category = request.args.get('category')
        search_title = request.args.get('search')

        query = "SELECT * FROM ad WHERE TRUE"
        params = []

        if selected_category:
            query += " AND equipmenttypename = %s"
            params.append(selected_category)

        cur.execute(query, params)
        ads = cur.fetchall()

    return render_template('ads.html', ads=ads, form=form)

#отдельная карточка
@app.route('/ad/<int:ad_id>', methods=['GET'])
def ad_card(ad_id):
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM Ad WHERE id = %s', (ad_id,))
        ad = cur.fetchone()
        if ad is None:
            return "Карточка не найдена", 404 
        
        #Получаем все отзывы из объявления
        cur.execute('''
            SELECT SenderLogin, Text, Rating, PublishDate
            FROM Review
            JOIN Ad ON Review.AdId = Ad.id
            WHERE Ad.id = %s
        ''', (ad_id,))
        reviews = cur.fetchall()

        return render_template('card.html', ad=ad, reviews=reviews)


from flask import request, render_template
from app.forms import CategoryForm  

#профиль пользователя
@app.route('/user/<user_login>', methods=['GET'])
def user_profile(user_login):
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        with con.cursor() as cur:

            user_data =cur.execute("SELECT Login, Name, Phone FROM AppUser WHERE Login = %s", (user_login,)).fetchone()

            if user_data is None:
             return "Пользователь не найден", 404
   
            login, name, phone = user_data;
        
            rating = cur.execute('''
                SELECT ROUND(AVG(Rating), 2) FROM Review
                JOIN Ad ON Review.AdId = Ad.id
                WHERE Ad.UserLogin = %s
            ''', (user_login,)).fetchone()[0]
            if rating is None:
                rating = 0

            #Меню фильтрации
            form = CategoryForm()

            selected_category = request.args.get('category')
            selected_manufacturer = request.args.get('manufacturer')
            search_title = request.args.get('search') 

            query = "SELECT * FROM Ad WHERE UserLogin = %s"
            params = [user_login]

            if selected_category:
                query += " AND equipmenttypename = %s"
                params.append(selected_category)
            if selected_manufacturer:
                query += " AND manufacturername = %s"
                params.append(selected_manufacturer)
            if search_title:
                query += " AND title ILIKE %s"
                params.append(f'%{search_title}%')

            cur.execute(query, tuple(params))
            ads = cur.fetchall()

    return render_template('user_profile.html', rating=rating, ads=ads, user_login=login, name=name, phone=phone, form=form)

#написать отзыв
from app.forms import ReviewForm
from datetime import date
# import logging
@app.route('/add_review/<int:ad_id>', methods=['GET', 'POST'])
def add_review(ad_id):
    if not isinstance(ad_id, int):
        abort(400)
    rev_form = ReviewForm()
    publishdate = date.today()
    if rev_form.validate_on_submit():
        rating = rev_form.rating.data
        text = rev_form.text.data.encode('utf-8', errors='ignore').decode('utf-8')
        senderlogin = current_user.login

        with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
            cur = con.cursor()

            cur.execute('INSERT INTO review (adid, senderlogin, text, rating, publishdate)'
                        'VALUES (%s, %s, %s, %s, %s)',
                        (ad_id, senderlogin, text, rating, publishdate))

        flash(f'Отзыв оставлен.', 'success')
        return redirect(url_for('ad_card',  ad_id=ad_id))
    return render_template('add_review.html', title='Оставить отзыв', public_date=publishdate, form=rev_form)

# ____________________________ЗАЯВКИ_НАЧ______________________________________

#История заявок в качестве арендодателя
@app.route('/user_profile/<user_login>/in_application', methods=['GET'])
def inapplication(user_login):
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM Application WHERE LandlordLogin = %s', (user_login,))
        inapp = cur.fetchall()
        return render_template('inapplication.html', inapp=inapp)

#История заявок в качестве арендатора
@app.route('/user_profile/<user_login>/my_application', methods=['GET'])
def myapplication(user_login):
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM Application WHERE TenantLogin = %s', (user_login,))
        myapp = cur.fetchall()
        print(myapp)
        return render_template('myapplication.html', myapp=myapp)

#Данные по конкретной заявке
@app.route('/user_profile/<user_login>/application/<aplication_id>', methods=['GET'])
def appitem(user_login, aplication_id):
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM ApplicationItem WHERE ApplicationId = %s', (aplication_id,))
        appitem = cur.fetchall()

        cur.execute('SELECT * FROM Application WHERE id = %s', (aplication_id,))
        appinform = cur.fetchone()

        #Телефон арендодатель
        cur.execute('SELECT phone FROM appuser WHERE login = %s', (appinform[1],))
        landlord_phone = cur.fetchone()

        #Телефон арендатор
        cur.execute('SELECT phone FROM appuser WHERE login = %s', (appinform[2],))
        tenant_phone = cur.fetchone()

        return render_template('appitemdetail.html', appitem=appitem, appinform=appinform, landlord_phone=landlord_phone,  tenant_phone= tenant_phone)

from app.forms import EditStatusForm

#Изменение статуса конкретной заявке
@app.route('/user_profile/<user_login>/application/<aplication_id>/red', methods=['GET', 'POST'])
def appstatus_red(user_login, aplication_id):
    if user_login != current_user.login:
        flash('У вас нет прав для изменения заявки.', 'danger')
        return redirect(url_for('index'))

    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()

        #текущий статус заявки
        cur.execute('SELECT statusname FROM Application WHERE id = %s', (aplication_id,))
        status = cur.fetchone()
        if not status:
            flash('Заявка не найдена.', 'danger')
            return redirect(url_for('index'))

        form = EditStatusForm(status=status[0])
        if form.validate_on_submit():
            new_status = form.status.data
            cur.execute('UPDATE Application SET statusname = %s WHERE id = %s', (new_status, aplication_id))
            con.commit()
            flash('Изменения сохранены.', 'success')
            return redirect(url_for('appitem', user_login=user_login, aplication_id=aplication_id))

    return render_template('appstatus_red.html', form=form, ap_id=aplication_id)

from app.forms import CreateApplication

#Работа с созданием заявки
@app.route('/user_profile/<user_login>/newapplication/<landlordlogin>/<adid>', methods=['GET', 'POST'])
def newapplication(user_login, adid, landlordlogin):
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:
        cur = con.cursor()   
        tenantlogin = user_login
        statusname = 'Черновик'

        form = CreateApplication()
        form_is = True
        
        # Есть ли заявка с этим арендодателем как черновик
        cur.execute('''SELECT id FROM Application 
                        WHERE landlordlogin = %s AND tenantlogin = %s AND statusname = %s
                        ''', (landlordlogin, tenantlogin, statusname))
        res_appid = cur.fetchone()
        print(res_appid)

        #есть
        if res_appid:
            applicationid = res_appid[0]

            #Проверка есть ли эта карточка в заявке
            cur.execute('''SELECT 1 FROM ApplicationItem 
                        WHERE applicationid = %s AND adid = %s''', (applicationid, adid))
            res_item = cur.fetchone()

            #если есть, то выводим сообщение
            if res_item:
                flash('Эта карточка уже добавлена в вашу заявку.')
                form_is = False 
            else:
            #если нет,то вставляем новую позицию в заявку
                #вычисление последней позиции
                cur.execute('''SELECT COALESCE(MAX(number), 0)+1   
                                 FROM ApplicationItem 
                                 WHERE applicationid = %s''', (applicationid,))
                number = cur.fetchone()[0]

                #создание новой записи
                cur.execute('''INSERT INTO ApplicationItem (number, applicationid, adid)
                        VALUES (%s, %s, %s)''', (number, applicationid, adid))
                flash('Новая позиция добавлена в существующую заявку')
                form_is = False
                return redirect(url_for('myapplication', user_login=tenantlogin))
        elif form.validate_on_submit():
                rentstartdate = form.rentstartdate.data
                rentenddate = form.rentenddate.data
       
                #Новая заявка
                cur.execute('''INSERT INTO Application (landlordlogin, tenantlogin, rentstartdate, rentenddate, statusname)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id''', 
                       (landlordlogin, tenantlogin, rentstartdate, rentenddate, statusname))
            
                applicationid = cur.fetchone()[0]

                cur.execute('''SELECT COALESCE(MAX(number), 0)+1   
                                 FROM ApplicationItem 
                                 WHERE applicationid = %s''', (applicationid,))
                number = cur.fetchone()[0] 
                #Добавление записи в ApplicationId
                cur.execute('''INSERT INTO ApplicationItem (number, applicationid, adid) 
                       VALUES (%s, %s, %s)''', (number, applicationid, adid))

                con.commit()
                flash('Заявка успешно создана', 'succes')
                return redirect(url_for('myapplication', user_login=current_user.login))

    return render_template('newapplication.html', form=form, form_is=form_is, landlordlogin=landlordlogin, tenantlogin=tenantlogin, status=statusname)

#Когда пользователь отправил заявку. Статус заявки меняется от чероник -> на рассмотрении
@app.route('/<user_login>/<application_id>/applicationsended', methods=['GET', 'POST'])
def app_sended(application_id, user_login):
     with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:

        cur = con.cursor()  
        statusname = 'На рассмотрении'
        cur.execute('''UPDATE Application SET statusname
                       = %s WHERE id = %s''', 
                       (statusname, application_id))
        con.commit()
        flash('Заявка отправлена', 'success')

        cur.execute('SELECT * FROM Application WHERE TenantLogin = %s', (user_login,))
        myapp = cur.fetchall()
        print(myapp)
        cur.close()
        return render_template('myapplication.html', myapp=myapp)

#Редактирование заявки (в сатусе черновик)
from app.forms import CreateApplication
@app.route('/application/<user_login>/<application_id>/edit', methods=['GET', 'POST'])
@login_required
def app_edit(user_login, application_id):
    if user_login != current_user.login:
         flash('У вас нет прав для редактирования этой заявки.', 'danger')
         return redirect(url_for('index'))
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME'],
                         ) as con:
        cur = con.cursor()
        cur.execute('SELECT rentstartdate, rentenddate '
                      'FROM application '
                     'WHERE id = %s', (application_id,))
        
        application_data = cur.fetchone()
        print(application_data)
        rentstartdate, rentenddate = application_data

        form = CreateApplication(rentstartdate = rentstartdate , rentenddate = rentenddate)
        if form.validate_on_submit():
            rentstartdate = form.rentstartdate.data
            rentenddate = form.rentenddate.data
            
            cur.execute('UPDATE Application SET rentstartdate = %s, rentenddate  = %s WHERE id =%s',
                            (rentstartdate,  rentenddate, application_id))
            flash('Изменения сохранены')
            cur = con.cursor()
            return redirect(url_for('myapplication', user_login=user_login))
        cur.close()
    return render_template('edapplication.html', application_id = application_id, form=form, user_login = user_login)

#Удаление заявки (если она в статусе черновик)
@app.route('/application/<application_id>/<user_login>/delete', methods=['POST'])
@login_required
def app_delete(application_id, user_login):
    #Проверка доступа для удаления
    if user_login != current_user.login:
         flash('У вас нет прав для удаления этой заявки.', 'danger')
         return redirect(url_for('index'))
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME'],
                         ) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM application WHERE id = %s", (application_id, ))
        con.commit()
    cur.close()
    con.close()
    flash('Заявка успешна удалена')
    return redirect(url_for('myapplication', user_login=user_login))

 #Редактирование позиции (изменение количества)
from app.forms import ItemEdit
@app.route('/<application_id>/<adid>/<number>/edit', methods=['GET', 'POST'])
def item_edit(application_id, number, adid):
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME']) as con:

        cur = con.cursor()  
        cur.execute('SELECT equipmentquantity '
                    'FROM  ApplicationItem '
                    'WHERE number = %s '
                    'AND applicationid = %s', (number, application_id ))
        result = cur.fetchone()

        if result is None:
            return "Запись не найдена", 404

        colvo = result[0]
        form = ItemEdit(equipmentquantity=colvo)
        if form.validate_on_submit():
            colvo = form.equipmentquantity.data
            cur.execute('''UPDATE ApplicationItem SET equipmentquantity
                       = %s WHERE number = %s AND applicationid = %s''', 
                       (colvo, number, application_id))
            con.commit()

            cur.execute('SELECT * FROM ApplicationItem WHERE ApplicationId = %s', (application_id,))
            appitem = cur.fetchall()

            cur.execute('SELECT * FROM Application WHERE id = %s', (application_id,))
            appinform = cur.fetchone()
            cur.close()
            return render_template('appitemdetail.html', appitem=appitem, appinform=appinform)
        cur.close()

    return render_template('item_edit.html', title='Редактирование позиции', form=form)

#Удаление позиции (если она в статусе черновик)
@app.route('/application/<user_login>/<application_id>/<adid>/<number>/delete', methods=['POST'])
@login_required
def item_delete(application_id, number, adid, user_login):
    #Проверка доступа для удаления
    if user_login != current_user.login:
         flash('У вас нет прав для удаления позиции.', 'danger')
         return redirect(url_for('index'))
    with psycopg.connect(host=app.config['DB_SERVER'],
                         user=app.config['DB_USER'],
                         password=app.config['DB_PASSWORD'],
                         dbname=app.config['DB_NAME'],
                         ) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM applicationitem WHERE applicationid = %s AND number = %s ", (application_id, number))
        con.commit()
    cur.close()
    con.close()
    flash('Позиция успешно удалена')
    return redirect(url_for('appitem', user_login = user_login, aplication_id = application_id))
# ____________________________ЗАЯВКИ_КОН______________________________________