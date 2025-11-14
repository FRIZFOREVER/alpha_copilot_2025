-- +goose Up
-- +goose StatementBegin
ALTER TABLE questions ADD COLUMN tag varchar(127);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE questions DROP COLUMN tag;
-- +goose StatementEnd
