# PVZ_Avito
Порядок запуска и работы сервиса
---------------------------

1) Клонируем репозиторий себе на устройство
2) Устанавливаем зависимости pip install -r requirements.txt (прежде стоит создать окружение или воспользоваться имеющимся) (версия Python 3.13)
3) Собрать Docker контейнер docker-compose up --build
4) Открыть Postman (или любой другой сервис заменяющий его) и на адрес http://localhost:8000/ производить запросы по необходимым ручкам, указывая необходимые параметры в Body raw (JSON)
5) Пример одного запроа на адрес http://localhost:8000/auth/dummyLogin . В Body указываем следующее: {"role": "moderator"} и отправляем запрос, где получаем ответ в виде jwt токена
6) Пример с адресами требующими токенов: http://localhost:8000/pvz . В Body указываем следующее: {"city": "Москва"}, а в Authorization выбираем Bearer Token и вставляем наш JWT токен, и отправляем запрос, где получаем ответ в виде информации о созданном ПВЗ (если токен с соответствующими правами) или отказ в доступе или описание ошибки

Ссылки на ручки:
-------------
POST:
  http://localhost:8000/auth/dummyLogin
  http://localhost:8000/auth/register
  http://localhost:8000/auth/login
  http://localhost:8000/pvz
  http://localhost:8000/pvz/{pvz_id}/close_last_reception
  http://localhost:8000/pvz/{pvz_id}/delete_last_product
  http://localhost:8000/products
  http://localhost:8000/receptions
  
GET:
  http://localhost:8000/pvz
  
  
