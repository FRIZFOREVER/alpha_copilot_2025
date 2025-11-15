-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS answer_graph_hsitory (
    id SERIAL PRIMARY KEY,
    answer_id INTEGER NOT NULL,
    tag VARCHAR(63),
    message VARCHAR(255),
    time_utc TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (answer_id) REFERENCES answers(answer_id) ON DELETE CASCADE,
)
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS answer_graph_hsitory;
-- +goose StatementEnd
