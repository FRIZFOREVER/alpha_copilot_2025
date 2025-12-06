SELECT 
    q.question_id,
    a.answer_id,
    q.message AS question_message,
    a.message AS answer_message,
    q.time_utc AS question_time,
    a.time_utc AS answer_time,
    q.voice_url,
    q.file_url,
    a.rating,
    a.file_url
FROM questions q
LEFT JOIN answers a ON q.answer_id = a.answer_id
LEFT JOIN chats c ON q.chat_id = c.id
WHERE c.user_id = (SELECT id FROM users WHERE uuid = $1)
AND a.visible = true
AND (q.message LIKE $2 OR a.message LIKE $2)
ORDER BY 
    CASE 
        WHEN q.message LIKE $2 THEN 1 
        WHEN a.message LIKE $2 THEN 2 
        ELSE 3 
    END,
    q.time_utc DESC;