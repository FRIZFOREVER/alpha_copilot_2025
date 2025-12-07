<div align="center">

# АЛЬФА БУДУЩЕЕ ХАКАТОН `<br>` Разработка copilot-приложения для клиентов микробизнеса

<img height="300" alt="logo" src="header.png">

</div>

Ссылка на этот репозиторий: https://github.com/FRIZFOREVER/alpha_copilot_2025

## Оглавление

- ### [Кейс](#1)
- ### [Решение](#2)
- ### [Запуск кода](#3)
- ### [Уникальность нашего решения](#4)
- ### [Стек](#5)
- ### [Команда](#6)
- ### [Скринкаст](#7)

## `<a name="1">` Кейс `</a>`

Разработайте приложение-помощник, которое поможет владельцам малого бизнеса эффективно решать повседневные задачи с использованием возможностей LLM (Language Learning Models). Приложение должно предоставлять рекомендации по ключевым аспектам бизнеса, таким как юридические вопросы, маркетинг, финансы и другие.

## `<a name="2">`Решение `</a>`

### Архетиктура решения

Решение представляет собой микро-сервисную архитектуру, включающую в себя:

- Backend - Golang + Fiber
- Frontend - TypeScript + React
- Ml - LangGraph + FastAPI
- Ollama
- S3 - Minio
- БД - Postgres
- STT - AssemblyAI, Whisper
- Протоколы - https(sse), webscoket

### Архетиктура модели

LangGraph-пайплайн `pipeline.py` ML-сервиса состоит из режимов `fast`, `thinking` и `research`. Узел `Mode Decider`
определяет режим и направляет состояние GraphState:

- **Fast**: цепочка `Flash Memories → Fast answer → Final answer` быстро генерирует ответ, если
  контекст достаточен.
- **Thinking**: `Thinking planner` строит пошаговый план, исполняет вспомогательные инструменты и
  агрегирует доказательства, после чего `Thinking answer` формирует итог.
- **Research**: цикл `Research reason → Research tool call ↔ Research observer → Research answer`
  позволяет агенту запрашивать зарегистрированные инструменты, валидировать аргументы и сохранять
  наблюдения, пока `NextAction` не укажет на готовность финализировать ответ.

GraphState хранит историю шагов, доказательства, промежуточные подсказки и активные наблюдения, что
делает пайплайн детерминированным и пригодным для отладки. Перед запуском графа сервис проверяет
валидность голосового ввода, определяет тег диалога (юридические вопросы, маркетинг и т.д.) и только
после этого запускает потоковое поколение ответа.

В решении допускается использование внешних провайдеров при выставлении соответствующей нестандартной конфигруации
Все валидации реализованы в виде самостоятельных агенгтов

## `<a name="3">`Запуск кода `</a>`

### Последовательные шаги для запуска кода:

1. Склонируйте гит репозиторий;

```Bash
git clone https://github.com/FRIZFOREVER/alfa_copilot_2025.git
```

2. Прочитайте .env.example и по инструкциям в нём создайте и заполните .env в той же папке
3. Убедитесь, что у вас установлен и сконфигурирован nvidia-container-toolkit и запустите все контейнеры:

```shell
docker compose -f compose.localrelease.yml up --build
```

3.1 После успешного поднятия, внутренний сервис с ml логикой: ml-api начнёт скачивать модели через клиент ollama. При этом остальные части приложения уже будут работать. Если отправить запрос, пока модели всё ещё инициализируются, то сервис вернёт ошибку 500(503) - модели всё ещё инициализируются и вам прийдёт пустой ответ

4. Для доступа к сайту необходимо перейти по ссылке [http://localhost:5173/](http://localhost:5173/)

Также у нас есть видео-скринкаст (см конец этого README), где демонстрируется запуск и функционал приложения

## `<a name="4">`Уникальность нашего решения `</a>`

### Киллерфичи:

1. Несколько режимов работы логики нашего решения со стороны ml, который адаптируется к не до конца заполненным данным и запросам пользователя
2. Backend на Golang полностью покрыт unit-тестами, все сервисы коммуницируют друг с другом только через него
3. Реализованы интеграции с интернет-поиском через агента и отправкой сообщений в телеграм через Frontend
4. Решение разворачивается полностью локально, использует только Open-source источники и не требует внешнего платного API для функционирования
5. Агент отправляет статус своих размышлений по технологии Websocket и это отрисовывается на Frontend'е
6. Ответ на Frontend поступает по протоколу SSE, что позволяет генерировать ответ на глазах, не дожидаясь окончания его генерации
7. Чтение, изменение и генерация файлов. Поддерживаемые форматы: txt, pdf, md, csv (Нужен режим **Thinking**)
8. Интеграция с telegram с возможностью отправки сообщений через интерфейс телеграмма
9. Интеграция с Todoist ...

### Советуем попробовать:

1. Попробуйте заполнить информацию о себе и посмотреть, как изменяться ответы LLM и проверить, действительно ли она вас знает!
2. Попробуйте начать ваше сообщение с @ и воспользоваться предложенными тегам
3. Попробуйте зайти в свой профиль на платформе, подключить телеграм и отправить кому-то сообщение через кнопку в конце любого сгенерированного сообщения
4. Попробуйте нажать на кнопку микрофона и задать свой вопрос голосом
5. Попробуйте режим Deep Research с сложным вопросом, но аккуратно, он может думать ну ОЧЕНЬ долго (20-30 минут)

## `<a name="5">`Стек `</a>`

<div align="center">
  <img src="https://github.com/devicons/devicon/blob/master/icons/python/python-original-wordmark.svg" title="Python" alt="Python" height="40"/>
  <img src="./assets/ollama.svg" title="lama" alt="lama" height="40"/>
  <img src="./assets/uvicorn.svg" title="uvicorn" alt="uvicorn" height="40"/>
  <img src="https://github.com/simple-icons/simple-icons/raw/refs/heads/develop/icons/langchain.svg" title="langchain" alt="langchain" height="40"/>
  <img src="https://github.com/simple-icons/simple-icons/raw/refs/heads/develop/icons/langgraph.svg" title="langgraph" alt="langgraph" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/fastapi/fastapi-plain-wordmark.svg" title="fastapi" alt="fastapi" height="40"/>
  <img src="https://fronty.com/static/uploads/1.11-30.11/languages%20in%202022/go.png" title="GO" alt="GO" height="40"/>
  <img src="./assets/websocket.svg" title="websocket" alt="websocket" height="40"/>  <img src="./assets/minio.svg" title="minio" alt="minio" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/fiber/fiber-plain.svg" title="Fiber" alt="Fiber" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/postgresql/postgresql-plain.svg" title="postgres" alt="postgres" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/react/react-original.svg" title="react" alt="react" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/typescript/typescript-plain.svg" title="typescript" alt="typescript" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/tailwindcss/tailwindcss-original.svg" title="tailwind" alt="tailwind" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/vitejs/vitejs-original.svg" title="vite" alt="vite" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/lodash/lodash-original.svg" title="lodash" alt="lodash" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/redux/redux-original.svg" title="redux" alt="redux" height="40"/>
  <img src="https://github.com/devicons/devicon/blob/master/icons/vitest/vitest-original.svg" title="vitest" alt="vitest" height="40"/>
</div>

## `<a name="6">`Команда `</a>`

*Состав команды "Жабки МИСИС"*

- <h4><img align="center" height="25" src="https://user-images.githubusercontent.com/51875349/198863127-837491f2-b57f-4c75-9840-6a4b01236c7a.png">: @facT0RR, Маслов Денис - Backend-developer</h3>
- <h4><img align="center" height="25" src="https://user-images.githubusercontent.com/51875349/198863127-837491f2-b57f-4c75-9840-6a4b01236c7a.png">: @FRIZFOREVER, Хромов Кирилл - ML-engineer / ML-Ops</h3>
- <h4><img align="center" height="25" src="https://user-images.githubusercontent.com/51875349/198863127-837491f2-b57f-4c75-9840-6a4b01236c7a.png">: @egoryaaa, Яровицын Егор - Frontend-developer</h3>
- <h4><img align="center" height="25" src="https://user-images.githubusercontent.com/51875349/198863127-837491f2-b57f-4c75-9840-6a4b01236c7a.png">: @Llaceyne, Гулария Лана - UI/UX Designer </h3>

## `<a name="7">`Скринкаст `</a>`

- [Cсылка на скринкаст](https://youtu.be/UypCoDZtJKo?si=_nhtPIP5xlJcuEwv)&nbsp;
