-- +goose Up
-- +goose StatementBegin
ALTER TABLE answers ADD COLUMN file_url TEXT;
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE answers DROP COLUMN file_url;
-- +goose StatementEnd
