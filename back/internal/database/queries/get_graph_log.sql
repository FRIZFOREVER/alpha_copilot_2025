SELECT id, tag, message, time_utc 
FROM answer_graph_hsitory 
WHERE answer_id = $1
ORDER BY time_utc DESC;