SELECT 
    q.question_id,
    a.answer_id,
    q.message as question_message,
    a.message as answer_message,
    q.time_utc as question_time,
    a.time_utc as answer_time,
    q.voice_url,
    q.file_url,
    a.rating
FROM questions q
LEFT JOIN answers a ON q.answer_id = a.answer_id
LEFT JOIN chats c ON q.chat_id = c.id
LEFT JOIN users u ON c.user_id = u.id
WHERE u.uuid = $1
AND a.visible = true
LIMIT $2;