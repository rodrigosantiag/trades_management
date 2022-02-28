CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS public.accounts (
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

CREATE TABLE IF NOT EXISTS public.brokers (
                                id SERIAL PRIMARY KEY,
                                uid uuid DEFAULT uuid_generate_v4(),
                                name character varying,
                                user_id integer,
                                created_at timestamp without time zone NOT NULL,
                                updated_at timestamp without time zone NOT NULL
);

CREATE TABLE IF NOT EXISTS public.strategies (
                                   id SERIAL PRIMARY KEY,
                                   uid uuid DEFAULT uuid_generate_v4(),
                                   name character varying,
                                   user_id integer NOT NULL,
                                   created_at timestamp(6) without time zone NOT NULL,
                                   updated_at timestamp(6) without time zone NOT NULL
);

CREATE TABLE IF NOT EXISTS public.trades (
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


CREATE TABLE IF NOT EXISTS public.users (
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
                              created_at timestamp without time zone NOT NULL,
                              updated_at timestamp without time zone NOT NULL
);

CREATE INDEX index_accounts_on_broker_id ON public.accounts USING btree (broker_id);

CREATE INDEX index_accounts_on_user_id ON public.accounts USING btree (user_id);

CREATE INDEX index_brokers_on_user_id ON public.brokers USING btree (user_id);

CREATE INDEX index_strategies_on_user_id ON public.strategies USING btree (user_id);

CREATE INDEX index_trades_on_account_id ON public.trades USING btree (account_id);

CREATE INDEX index_trades_on_strategy_id ON public.trades USING btree (strategy_id);

CREATE INDEX index_trades_on_user_id ON public.trades USING btree (user_id);

CREATE UNIQUE INDEX index_users_on_confirmation_token ON public.users USING btree (confirmation_token);

CREATE UNIQUE INDEX index_users_on_email ON public.users USING btree (email);

CREATE UNIQUE INDEX index_users_on_reset_password_token ON public.users USING btree (reset_password_token);

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT fk_trades_users FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.brokers
    ADD CONSTRAINT fk_brokers_users FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT fk_trades_accounts FOREIGN KEY (account_id) REFERENCES public.accounts(id);

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT fk_accounts_brokers FOREIGN KEY (broker_id) REFERENCES public.brokers(id);

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT fk_accounts_users FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.strategies
    ADD CONSTRAINT fk_strategies_users FOREIGN KEY (user_id) REFERENCES public.users(id);

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT fk_trades_strategies FOREIGN KEY (strategy_id) REFERENCES public.strategies(id);

