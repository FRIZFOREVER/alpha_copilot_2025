SELECT 
    COUNT(a.answer_id) as count_files,
    COUNT(CASE WHEN DATE(a.time_utc) != CURRENT_DATE THEN a.answer_id END) as count_files_yesterday
FROM answers a
JOIN chats c ON a.chat_id = c.id
JOIN users u ON c.user_id = u.id
WHERE u.uuid = $1 AND a.file_url IS NOT NULL;