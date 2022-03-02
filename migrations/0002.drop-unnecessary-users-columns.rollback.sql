ALTER TABLE users
    ADD COLUMN reset_password_token   character varying,
    ADD COLUMN reset_password_sent_at timestamp without time zone,
    ADD COLUMN allow_password_change  boolean DEFAULT false,
    ADD COLUMN remember_created_at    timestamp without time zone,
    ADD COLUMN confirmation_token     character varying,
    ADD COLUMN confirmation_sent_at   timestamp without time zone,
    ADD COLUMN tokens                 text;
