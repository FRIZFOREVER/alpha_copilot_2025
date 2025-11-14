UPDATE answers 
SET message = $1, time_utc = $2 
WHERE answer_id = $3