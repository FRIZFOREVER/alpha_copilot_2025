INSERT INTO questions
  (time_utc, message, chat_id, answer_id, voice_url, file_url)
VALUES
  ($1, $2, $3, $4, $5, $6)
RETURNING question_id;