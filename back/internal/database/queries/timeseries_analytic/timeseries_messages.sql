WITH date_range AS (
    SELECT generate_series(
        DATE($2), 
        DATE($3), 
        '1 day'::interval
    )::date as day
)
SELECT 
    dr.day,
    COUNT(all_messages.time_utc) as count_messages
FROM date_range dr
LEFT JOIN (
    SELECT q.time_utc 
    FROM questions q
    JOIN chats c ON q.chat_id = c.id
    JOIN users u ON c.user_id = u.id
    WHERE u.uuid = $1
      AND q.time_utc BETWEEN $2 AND $3
    
    UNION ALL
    
    SELECT a.time_utc 
    FROM answers a
    JOIN chats c ON a.chat_id = c.id
    JOIN users u ON c.user_id = u.id
    WHERE u.uuid = $1
      AND a.time_utc BETWEEN $2 AND $3
) as all_messages ON DATE(all_messages.time_utc) = dr.day
GROUP BY dr.day
ORDER BY dr.day;