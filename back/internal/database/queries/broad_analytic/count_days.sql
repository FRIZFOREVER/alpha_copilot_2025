SELECT COUNT(DISTINCT DATE(time_utc)) as count_days
FROM (
    SELECT q.time_utc 
    FROM questions q
    JOIN chats c ON q.chat_id = c.id
    JOIN users u ON c.user_id = u.id
    WHERE u.uuid = $1
    
    UNION ALL
    
    SELECT a.time_utc 
    FROM answers a
    JOIN chats c ON a.chat_id = c.id
    JOIN users u ON c.user_id = u.id
    WHERE u.uuid = $1
) as all_messages;