SELECT id, fio, login, user_info, business_info, additional_instructions login FROM users WHERE uuid = $1;
