from logicSite.requestSQL import with_database
import sqlite3


@with_database()
def setAnime(title, rating, released, parent_id, episode_count, url, whatIsIt, idImage,
             **kwargs):
    return """
    INSERT INTO anime (title, rating, released, parent_id, episode_count, url, whatIsIt, idImage)
    VALUES
    (?, ?, ?, ?, ?, ?, ?, ?);
    """, (title, rating, released, parent_id, episode_count, url, whatIsIt, idImage)


@with_database()
def getGenge(name):
    return """
    SELECT id FROM genres WHERE name = ?;
    """, (name, )


@with_database()
def setGenre(name):
    return """
    INSERT INTO genres (name)
    VALUES
    (?);
    """, (name, )


@with_database()
def plusAnimeGenre(idAnime, idGenre):
    return """
    INSERT INTO genre_anime (anime_id, genre_id)
    VALUES 
    (?, ?);
    """, (idAnime, idGenre)


@with_database()
def setWatched(isWatched, idAnime):
    return """
    UPDATE anime SET watched = ? WHERE id = ?;
    """, (isWatched, idAnime)


@with_database()
def getAnumeIDByUrl(sUrl):
    return """
    SELECT id FROM anime WHERE url = ?;
    """, (sUrl, )


@with_database()
def uploadAnime(title, rating, released, parent_id, episode_count, whatIsIt,
                anime_id, idImage, **kwargs):
    return """
        UPDATE anime 
        SET title = ?, 
            rating = ?, 
            released = ?, 
            parent_id = ?, 
            episode_count = ?,  
            whatIsIt = ?,
            idImage = ?
        WHERE id = ?;
    """, (title, rating, released, parent_id, episode_count, whatIsIt, idImage,
          anime_id)


@with_database()
def anime():
    return """
    SELECT 
    a.id AS anime_id,
    a.title AS anime_title,
    a.rating AS anime_rating,
    a.episode_count AS anime_episode_count,
    a.released AS anime_released,
    a.watched AS anime_watched,
    a.url AS anime_url,
    GROUP_CONCAT(g.name) AS genres
FROM 
    anime a
LEFT JOIN 
    genre_anime ag ON a.id = ag.anime_id
LEFT JOIN 
    genres g ON ag.genre_id = g.id
LEFT JOIN 
    anime a2 ON a.parent_id = a2.id
WHERE a.watched = 0 
  AND (a.parent_id IS NULL OR a2.watched = 1)  -- Условие для родительского аниме
GROUP BY 
    a.id, a.title, a.rating, a.episode_count, a.released, a.watched, a.url
ORDER BY 
    a.released DESC;
    """, ()

@with_database()
def animeNotReleased():
    return """
    SELECT a.url
    from anime a
    where a.released = 0
    """, ()

@with_database()
def createNewCol(nameTab, nameCol):
    return f'''ALTER TABLE {nameTab} ADD COLUMN {nameCol} TEXT;''', ()

def updateUrlDomen(oldDomen, newDomen):
    connection = sqlite3.connect('test.db')
    cursor = connection.cursor()
    try:
        # Начинаем транзакцию
        connection.execute("BEGIN TRANSACTION;")

        # Шаг 1: Создать временную колонку
        cursor.execute("ALTER TABLE anime ADD COLUMN temp_url TEXT;")

        # Шаг 2: Заполнить временную колонку новыми значениями URL
        cursor.execute(
            f"""
            UPDATE anime 
            SET temp_url = replace(url, '{oldDomen}', ?)
            WHERE url LIKE '%{oldDomen}%'
            AND released = 0;
        """, (newDomen, ))

        # Шаг 3: Проверить уникальность новых значений
        cursor.execute("""
            SELECT temp_url 
            FROM anime 
            WHERE temp_url IN (SELECT url FROM anime)
            AND temp_url IS NOT NULL;
        """)
        duplicates = cursor.fetchall()

        if duplicates:
            print("Обнаружены дублирующиеся URL:")
            for duplicate in duplicates:
                print(duplicate[0])
            raise Exception("Нельзя обновить URL, так как найдены дубликаты.")

        # Шаг 4: Безопасно скопировать значения из temp_url в url
        cursor.execute("""
            UPDATE anime 
            SET url = temp_url 
            WHERE temp_url IS NOT NULL;
        """)

        # Шаг 5: Удалить временную колонку
        cursor.execute("ALTER TABLE anime DROP COLUMN temp_url;")

        # Подтверждаем транзакцию
        connection.commit()
        print("URL успешно обновлены через временную колонку.")
    except Exception as e:
        # Откатываем изменения при ошибке
        connection.rollback()
        print(f"Ошибка при обновлении: {e}")


@with_database()
def deleteAnime(id):
    return """
    delete from anime where id = ?;
    """, (id, )
