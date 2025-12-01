SELECT 
    q.tag,
    COUNT(q.tag) as tag_count,
    COUNT(CASE WHEN DATE(q.time_utc) != CURRENT_DATE THEN q.tag END) as tag_count_yesterday
FROM questions q
JOIN chats c ON q.chat_id = c.id
JOIN users u ON c.user_id = u.id
WHERE u.uuid = $1 AND q.tag IS NOT NULL
GROUP BY q.tag
ORDER BY tag_count DESC;