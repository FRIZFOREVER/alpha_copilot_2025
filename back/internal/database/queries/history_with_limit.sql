WITH latest_messages AS (
    -- Последние LIMIT $2 сообщений (вне зависимости от тега)
    SELECT 
        q.question_id,
        a.answer_id,
        q.message as question_message,
        a.message as answer_message,
        q.time_utc as question_time,
        a.time_utc as answer_time,
        q.voice_url,
        q.file_url,
        a.file_url as answer_file_url, -- Новое поле
        a.rating,
        q.tag,
        1 as priority -- Высший приоритет для последних сообщений
    FROM questions q
    LEFT JOIN answers a ON q.answer_id = a.answer_id
    LEFT JOIN chats c ON q.chat_id = c.id
    LEFT JOIN users u ON c.user_id = u.id
    WHERE u.uuid = $1
    AND a.visible = true
    AND q.tag != $3
    ORDER BY a.time_utc DESC NULLS LAST
    LIMIT $2
),
tagged_messages AS (
    -- Последние LIMIT $2 сообщений с определенным тегом
    SELECT 
        q.question_id,
        a.answer_id,
        q.message as question_message,
        a.message as answer_message,
        q.time_utc as question_time,
        a.time_utc as answer_time,
        q.voice_url,
        q.file_url,
        a.file_url as answer_file_url, -- Новое поле
        a.rating,
        q.tag,
        2 as priority -- Низший приоритет для сообщений с тегом
    FROM questions q
    LEFT JOIN answers a ON q.answer_id = a.answer_id
    LEFT JOIN chats c ON q.chat_id = c.id
    LEFT JOIN users u ON c.user_id = u.id
    WHERE u.uuid = $1
    AND a.visible = true
    AND q.tag = $3
    ORDER BY a.time_utc DESC NULLS LAST
    LIMIT $2
),
combined_messages AS (
    -- Объединяем оба набора и убираем дубликаты
    SELECT * FROM latest_messages
    UNION 
    SELECT * FROM tagged_messages
)
-- Финальный результат с сортировкой по answer_time
SELECT DISTINCT
    question_id,
    answer_id,
    question_message,
    answer_message,
    question_time,
    answer_time,
    voice_url,
    file_url,
    rating,
    tag,
    answer_file_url
FROM combined_messages
ORDER BY answer_time NULLS LAST;