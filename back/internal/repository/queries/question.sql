INSERT INTO questions
  (time_utc, message, chat_id, answer_id, voice_url, file_url, tag)
VALUES
  ($1, $2, $3, $4, $5, $6, $7)
RETURNING question_id;