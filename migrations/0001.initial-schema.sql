CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS accounts (
                                 id SERIAL PRIMARY KEY,
                                 uid uuid DEFAULT uuid_generate_v4(),
                                 type_account character varying(1),
                                 currency character varying(3),
                                 initial_balance numeric(10,2) DEFAULT 0.0,
                                 current_balance numeric(10,2) DEFAULT 0.0,
                                 broker_id integer,
                                 created_at timestamp without time zone NOT NULL,
                                 updated_at timestamp without time zone NOT NULL,
                                 user_id integer
);

CREATE TABLE IF NOT EXISTS brokers (
                                id SERIAL PRIMARY KEY,
                                uid uuid DEFAULT uuid_generate_v4(),
                                name character varying,
                                user_id integer,
                                created_at timestamp without time zone NOT NULL,
                                updated_at timestamp without time zone NOT NULL
);

CREATE TABLE IF NOT EXISTS strategies (
                                   id SERIAL PRIMARY KEY,
                                   uid uuid DEFAULT uuid_generate_v4(),
                                   name character varying,
                                   user_id integer NOT NULL,
                                   created_at timestamp(6) without time zone NOT NULL,
                                   updated_at timestamp(6) without time zone NOT NULL
);

CREATE TABLE IF NOT EXISTS trades (
                               id SERIAL PRIMARY KEY,
                               uid uuid DEFAULT uuid_generate_v4(),
                               value numeric(10,2),
                               profit numeric(10,2),
                               result boolean,
                               result_balance numeric(10,2),
                               account_id integer,
                               user_id integer,
                               created_at timestamp without time zone NOT NULL,
                               updated_at timestamp without time zone NOT NULL,
                               type_trade character varying(1) DEFAULT 'T'::character varying,
                               strategy_id bigint
);


CREATE TABLE IF NOT EXISTS users (
                              id SERIAL PRIMARY KEY,
                              uid uuid DEFAULT uuid_generate_v4(),
                              encrypted_password character varying DEFAULT ''::character varying NOT NULL,
                              reset_password_token character varying,
                              reset_password_sent_at timestamp without time zone,
                              allow_password_change boolean DEFAULT false,
                              remember_created_at timestamp without time zone,
                              confirmation_token character varying,
                              confirmed_at timestamp without time zone,
                              confirmation_sent_at timestamp without time zone,
                              unconfirmed_email character varying,
                              name character varying,
                              email character varying,
                              risk integer,
                              tokens text,
                              created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
                              updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX index_accounts_on_broker_id ON accounts USING btree (broker_id);

CREATE INDEX index_accounts_on_user_id ON accounts USING btree (user_id);

CREATE INDEX index_brokers_on_user_id ON brokers USING btree (user_id);

CREATE INDEX index_strategies_on_user_id ON strategies USING btree (user_id);

CREATE INDEX index_trades_on_account_id ON trades USING btree (account_id);

CREATE INDEX index_trades_on_strategy_id ON trades USING btree (strategy_id);

CREATE INDEX index_trades_on_user_id ON trades USING btree (user_id);

CREATE UNIQUE INDEX index_users_on_confirmation_token ON users USING btree (confirmation_token);

CREATE UNIQUE INDEX index_users_on_email ON users USING btree (email);

CREATE UNIQUE INDEX index_users_on_reset_password_token ON users USING btree (reset_password_token);

ALTER TABLE ONLY trades
    ADD CONSTRAINT fk_trades_users FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY brokers
    ADD CONSTRAINT fk_brokers_users FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY trades
    ADD CONSTRAINT fk_trades_accounts FOREIGN KEY (account_id) REFERENCES accounts(id);

ALTER TABLE ONLY accounts
    ADD CONSTRAINT fk_accounts_brokers FOREIGN KEY (broker_id) REFERENCES brokers(id);

ALTER TABLE ONLY accounts
    ADD CONSTRAINT fk_accounts_users FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY strategies
    ADD CONSTRAINT fk_strategies_users FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE ONLY trades
    ADD CONSTRAINT fk_trades_strategies FOREIGN KEY (strategy_id) REFERENCES strategies(id);
