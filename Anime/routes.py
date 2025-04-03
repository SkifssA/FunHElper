from flask import Blueprint, jsonify, request, render_template
from .workByKeys import *

from .model import createTab
from .requestSQL import *
from .requestsSite import requisites

# createTab()
# print(createNewCol('anime', 'idImage'))
print(updateUrlDomen('https://animego.one', 'https://animego.la'))
for i in animeNotReleased():
    requisites(i[0], isPush=True)



anime_bp = Blueprint('anime', __name__)
"""
Добавить кнопки изменить домен
"""

@anime_bp.route('/')
def index():
    return render_template('anime.html', anime_list=anime())


@anime_bp.route('/add-anime', methods=['POST'])
def add_anime():
    data = request.json
    url = data.get('url')
    if url:
        # Здесь можно добавить логику для обработки нового аниме
        requisites(url)
        return jsonify({"message": "Аниме успешно добавлено!"})
    return jsonify({"message": "URL не указан!"}), 400


@anime_bp.route('/mark-as-watched', methods=['POST'])
def mark_as_watched():
    data = request.json
    anime_id = int(data.get('id'))
    setWatched(1, anime_id)
    return jsonify({"message": "Аниме помечено как просмотренное!"})


@anime_bp.route('/delete-anime', methods=['POST'])
def delete_anime():
    data = request.get_json()
    anime_id = data.get('id')
    if anime_id:
        # Удаление аниме из базы данных
        success = deleteAnime(anime_id) # Реализуйте эту функцию
        if success:
            return jsonify({
                'success': True,
                'message': 'Аниме успешно удалено'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Ошибка при удалении аниме'
            })
    else:
        return jsonify({'success': False, 'message': 'ID аниме не указан'})


@anime_bp.route('/save-subscription', methods=['POST'])
def save_subscription():
    subscription = request.get_json()
    registerPushUser(subscription)
    return jsonify({'success': True})
