SELECT 
    AVG(a.rating) as avg_rating,
    AVG(CASE WHEN DATE(a.time_utc) != CURRENT_DATE THEN a.rating END) as avg_rating_yesterday
FROM answers a
JOIN chats c ON a.chat_id = c.id
JOIN users u ON c.user_id = u.id
WHERE u.uuid = $1;