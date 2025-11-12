-- +goose Up
-- +goose StatementBegin
ALTER TABLE users ADD COLUMN user_info TEXT;
ALTER TABLE users ADD COLUMN business_info TEXT;
ALTER TABLE users ADD COLUMN additional_instructions TEXT;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE users DROP COLUMN user_info;
ALTER TABLE users DROP COLUMN business_info;
ALTER TABLE users DROP COLUMN sadditional_instruction;
-- +goose StatementEnd
