UPDATE users
SET user_info = $1, business_info = $2, additional_instructions = $3
WHERE uuid = $4;