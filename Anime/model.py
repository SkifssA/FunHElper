from logicSite.requestSQL import with_database

@with_database()
def Anime():
    return """
    CREATE TABLE IF NOT EXISTS anime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                                 -- Название аниме
    rating REAL CHECK (rating >= 0 AND rating <= 10),    -- Оценка от 0 до 10
    released INTEGER CHECK (released IN (0, 1)),         -- Вышло ли аниме (0 или 1)
    parent_id INTEGER,                                   -- Ссылка на предка
    watched INTEGER CHECK (watched IN (0, 1)) DEFAULT 0, -- Просмотрено ли аниме (0 или 1), по умолчанию 0
    episode_count INTEGER CHECK (episode_count >= 0),    -- Количество серий
    url TEXT NOT NULL UNIQUE,                            -- URL на сайт
    idImage TEXT NOT NULL,                               -- id картинки сайте
    whatIsIt TEXT,                                       -- Что это такое
    FOREIGN KEY (parent_id) REFERENCES anime(id) ON DELETE SET NULL
);
    """, ()

@with_database()
def genres():
  return """
  CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE               -- Название жанра (уникальное)
  );""", ()

@with_database()
def genre_anime():
  return """
  CREATE TABLE IF NOT EXISTS genre_anime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anime_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    FOREIGN KEY (anime_id) REFERENCES anime(id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE
  );""", ()

def createTab():
  Anime()
  genres()
  genre_anime()