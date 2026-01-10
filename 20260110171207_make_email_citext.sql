-- +goose Up
-- +goose StatementBegin
ALTER TABLE users (last_sign_in_at timestamp)
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
-- +goose StatementEnd
