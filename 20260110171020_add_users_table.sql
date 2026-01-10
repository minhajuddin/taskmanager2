-- +goose Up
-- +goose StatementBegin
CREATE TABLE users(
  id BIGSERIAL,
  email varchar,
  hashed_password varchar,
  created_at timestamp,
  updated_at timestamp
);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE users
-- +goose StatementEnd
