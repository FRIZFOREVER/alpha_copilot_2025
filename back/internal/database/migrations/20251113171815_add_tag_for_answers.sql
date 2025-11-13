-- +goose Up
-- +goose StatementBegin
ALTER TABLE answers ADD COLUMN tag varchar(127);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
ALTER TABLE answers DROP COLUMN tag;
-- +goose StatementEnd
