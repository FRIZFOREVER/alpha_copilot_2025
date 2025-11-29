SELECT 
    COUNT(c.id) as count_chats,
    COUNT(CASE WHEN DATE(c.create_date) != CURRENT_DATE THEN c.id END) as count_chats_yesterday
FROM chats c
JOIN users u ON c.user_id = u.id
WHERE u.uuid = $1;