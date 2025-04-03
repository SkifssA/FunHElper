import base64
import re
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

import pickle

from pywebpush import webpush, WebPushException
import json

vapid_private_key = None
vapid_public_key = None
subscriptions = []

def registerKeyPush():
    import pickle
    global vapid_public_key, vapid_private_key
    try:
        # Открываем файл для чтения
        with open("keys.pkl", "rb") as file:
            keys = pickle.load(file)  # Считываем кортеж из файла
        
        vapid_private_key = keys[0]
        vapid_public_key = keys[1]
        
    except FileNotFoundError:
        # Обработка случая, когда файла нет
        print("Ошибка: Файл 'keys.pkl' не найден.")
    
    except pickle.UnpicklingError:
        # Обработка ошибки при десериализации данных
        print("Ошибка: Не удалось прочитать данные из файла. Возможно, файл поврежден.")
    
    except Exception as e:
        # Обработка других возможных ошибок
        print(f"Произошла ошибка: {e}")
    
    def pem_to_base64(pem_key):
        # Удаление заголовка и футера PEM
        pem_data = re.sub(r"-----BEGIN.*-----|-----END.*-----|\n", "", pem_key)
        return pem_data.strip()
    
    
    # Генерация приватного ключа
    private_key = ec.generate_private_key(ec.SECP256R1())
    
    # Получение публичного ключа
    public_key = private_key.public_key()
    
    # Экспорт приватного ключа в формате PEM
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()).decode('utf-8')
    
    
    # Экспорт публичного ключа в формате base64url
    def export_public_key(key):
        public_bytes = key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint)
        return base64.urlsafe_b64encode(public_bytes).rstrip(b'=').decode('utf-8')
    
    if (vapid_private_key is None):
        vapid_private_key = pem_to_base64(pem_private_key)
        vapid_public_key = export_public_key(public_key)
    
    import pickle
    
    # Два значения для записи
    keys = (vapid_private_key, vapid_public_key)
    
    # Открываем файл для записи
    with open("keys.pkl", "wb") as file:
        pickle.dump(keys, file)  # Записываем кортеж в бинарном формате
    
    print("Значения успешно записаны!")

def loadPushUser():
    import pickle
    global subscriptions
    try:
        # Открываем файл для чтения
        with open("pushUser.pkl", "rb") as file:
            subscriptions = list(pickle.load(file))  # Считываем кортеж из файла

    except FileNotFoundError:
        # Обработка случая, когда файла нет
        print("Ошибка: Файл 'keys.pkl' не найден.")

    except pickle.UnpicklingError:
        # Обработка ошибки при десериализации данных
        print("Ошибка: Не удалось прочитать данные из файла. Возможно, файл поврежден.")

    except Exception as e:
        # Обработка других возможных ошибок
        print(f"Произошла ошибка: {e}")

registerKeyPush()
loadPushUser()

def send_web_push(subscription_info, title, message, icon):
    message = json.dumps({"title": title, "body": message, "icon":icon})
    try:
        response = webpush(
            subscription_info=subscription_info,  # Данные подписки пользователя
            data=message,                      # Payload (содержимое уведомления)
            vapid_private_key=vapid_private_key,  # Приватный VAPID-ключ
            vapid_claims={
                "sub": "mailto:your-email@example.com"  # Твой email для идентификации
            }
        )
        print("Уведомление успешно отправлено!")
    except WebPushException as ex:
        print(f"Ошибка отправки: {ex}")
        # Проверь статус ответа
        if ex.response and ex.response.json():
            print(ex.response.json())

def registerPushUser(subscription):
    loadPushUser()
    if subscription not in subscriptions:
        subscriptions.append(subscription)

    with open("pushUser.pkl", "wb") as file:
        pickle.dump(tuple(subscriptions), file)