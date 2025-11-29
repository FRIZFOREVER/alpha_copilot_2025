UPDATE answers 
SET message = $1, time_utc = $2, file_url = $3
WHERE answer_id = $4