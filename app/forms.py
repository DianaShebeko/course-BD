from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SelectField, DateField, IntegerField, PasswordField, SubmitField, FloatField, DecimalField, validators
from wtforms.validators import ValidationError, InputRequired
from wtforms.validators import DataRequired, EqualTo, Regexp
from wtforms.validators import Email
from datetime import date
import re

#Форма регистрации
class RegistrationForm(FlaskForm):
    login = StringField('Login', [validators.InputRequired(), validators.Email(message="Введите правильный формат электронной почты")
                                  ])
    name = StringField('Name', validators=[validators.InputRequired()])
    phone = StringField('Phone', validators=[DataRequired(), 
                           Regexp(r'^\+7\d{10}$', 
                           message="Неправильный формат номера. Должен начинаться с +7.")])
    password = PasswordField('Password', [validators.InputRequired(),
                                        validators.Length(min=8, max=100),
                                        validators.EqualTo('confirm', message='Пароли должны совпадать')])
    confirm  = PasswordField('Повторите пароль')
    submit = SubmitField('Зарегистрироваться')

#Форма логина
class LoginForm(FlaskForm):
    username = StringField('Логин', [validators.InputRequired(), ])
    password = PasswordField('Пароль', [validators.InputRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

#Форма редактирования пользователя
class EditUserForm(FlaskForm):
    phone = StringField('Phone', [validators.InputRequired(), validators.Regexp(r'^\+7\d{10}$', message="Неправильный формат номера. Должен начинаться с +7.")])
    name = StringField('Name', [validators.InputRequired()])
    password = PasswordField('Password', [validators.InputRequired(),
                                        validators.Length(min=8, max=100),
                                        validators.EqualTo('confirm', message='Пароли должны совпадать')])
    confirm  = PasswordField('Повторите пароль')
    submit = SubmitField('Сохранить')

#Форма выпадающего списка фильтрации объявлений
class CategoryForm(FlaskForm):
     category = SelectField('Категория', coerce=str )
     manufacturer = SelectField('Производитель', coerce=str)
     search = StringField('Поиск по заголовку')

#Форма отзывов
class ReviewForm(FlaskForm):
    rating = SelectField('Выберите оценку (от 1 до 5 звёзд)', choices=[(1),(2),(3),(4),(5)],validate_choice=True)
    text = StringField('Ваш комментарий',[validators.Optional()])
    submit = SubmitField('Отправить')

#Форма изменения статуса
class EditStatusForm(FlaskForm):
     status = SelectField('Статус заявки:', choices=[('На рассмотрении'),('Принята'),('Отклонена')], coerce=str )
     submit = SubmitField('Сохранить')

#Кастомная функция проверки дат в форме заявки
def check_dates(form, field):
    if form.rentstartdate.data >= field.data:
        raise ValidationError("Дата окончания должна быть позже даты начала аренды")
def check_date_today(form, field):
    if field.data < date.today():
        raise ValidationError("Дата начала аренды не может быть раньше сегодняшней")

#Форма заявки
class CreateApplication(FlaskForm):
     rentstartdate = DateField('Дата начала аренды', validators=[DataRequired(), check_date_today])
     rentenddate = DateField('Дата окончания аренды', validators=[DataRequired(), check_dates])
     submit = SubmitField('Сохранить данные')    

#Форма редактирования количества оборудования
class ItemEdit(FlaskForm):
    equipmentquantity = IntegerField('Количество (шт.)', [validators.InputRequired(), validators.NumberRange(min=1, message='Количество должно быть больше 0')])
    submit = SubmitField('Сохранить')

#Форма создания карточки
class CreateAd(FlaskForm):
    category = SelectField('Категория', coerce=str )
    manufacturer = SelectField('Производитель', coerce=str)
    title = StringField('Заголовок',[validators.InputRequired()])
    price = DecimalField('Цена', places=2, validators =
        [validators.InputRequired(message="Цена обязательна для заполнения."),
        validators.NumberRange(min=1.00, message="Цена должна быть больше 0.")])
    description = StringField('Описание')
    submit = SubmitField('Создать')
