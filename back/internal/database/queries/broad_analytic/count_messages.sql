SELECT 
    COUNT(*) as count_messages,
    COUNT(CASE WHEN DATE(time_utc) != CURRENT_DATE THEN 1 END) as count_messages_yesterday
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