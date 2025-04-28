from flask import Flask
from Anime import anime_bp
from Main import main_bp

app = Flask(__name__)

# Регистрация Blueprint'ов
app.register_blueprint(main_bp)
app.register_blueprint(anime_bp, url_prefix='/anime')

if __name__ == '__main__':
  app.run(debug=False)


# Сделать более добавить больше кнопок и сделать их иконками
# Добавить создание кнопок и фильтрок
