SELECT 
    q.tag,
    COUNT(q.tag) as tag_count
FROM questions q
JOIN chats c ON q.chat_id = c.id
JOIN users u ON c.user_id = u.id
WHERE u.uuid = $1 AND q.tag IS NOT NULL
GROUP BY q.tag
ORDER BY tag_count DESC;