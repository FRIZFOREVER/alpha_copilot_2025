-- +goose Up
-- +goose StatementBegin
ALTER TABLE questions ADD COLUMN file_url TEXT;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE questions DROP COLUMN file_url;
-- +goose StatementEnd
