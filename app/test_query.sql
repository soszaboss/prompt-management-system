-- Active: 1719482823859@@127.0.0.1@5432@flask_prompt_rest_api_app
SELECT *FROM public.statuts;


-- do 
-- $$
-- declare
--    selected_actor actor%rowtype;
-- begin
--    -- select actor with id 10   
--    select * 
--    from actor
--    into selected_actor
--    where actor_id = 10;

--    -- show the number of actor
--    raise notice 'The actor name is % %',
--       selected_actor.first_name,
--       selected_actor.last_name;
-- end; 
-- $$;

-- constant_name constant data_type = expression;
CREATE OR REPLACE FUNCTION get_user_by_id(
    user_id INT
)
RETURNS TABLE (username VARCHAR(25), email VARCHAR(50), user_role TEXT)
AS $$
BEGIN
    RETURN QUERY
        SELECT
            u.username,
            u.email,
            CASE
                WHEN u.role_id = 1 THEN 'admin'
                WHEN u.role_id = 2 THEN 'user'
                ELSE 'guest'
            END
        FROM users u
        WHERE u.id = user_id;

    IF NOT FOUND THEN
        RETURN ;
    END IF;
END;
$$
LANGUAGE plpgsql;

SELECT get_user_by_id(1);


CREATE TABLE groupes(
    id SERIAL PRIMARY KEY,
    groupe VARCHAR(35) NOT NULL UNIQUE
);

CREATE TABLE  groupes_users(
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    groupe_id INT NOT NULL,
    CONSTRAINT fk_users_groupes_users FOREIGN KEY(user_id) REFERENCES users(id),
    CONSTRAINT fk_groupes_groupes_users FOREIGN KEY(groupe_id) REFERENCES groupes(id)
);

CREATE OR REPLACE FUNCTION is_user_same_groupe(
    user1_id INT,
    user2_id INT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    groupe_user1_id INT;
    groupe_user2_id INT;
    result BOOLEAN;
BEGIN
    SELECT gu.groupe_id INTO groupe_user1_id FROM groupes_users gu WHERE gu.user_id = user1_id;
    SELECT gu.groupe_id INTO groupe_user2_id FROM groupes_users gu WHERE gu.user_id = user2_id;

    IF groupe_user1_id = groupe_user2_id THEN
        result := TRUE;
    ELSE
        result := FALSE;
    END IF;

    RETURN result;
END $$;

SELECT is_user_same_groupe(2, 4);

CREATE OR REPLACE FUNCTION create_get_user(
    username_parameter VARCHAR,
    email_parameter VARCHAR,
    password_parameter TEXT,
    role_id_parameter INT
)
RETURNS TABLE (
    user_id INT,
    user_username VARCHAR(25),
    user_email VARCHAR(50),
    user_role_id TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (username, email, password, role_id)
    VALUES (username_parameter, email_parameter, password_parameter, role_id_parameter);

    RETURN QUERY
        SELECT 
            u.id,
            u.username,
            u.email,
            CASE
                WHEN u.role_id = 1 THEN 'admin'
                WHEN u.role_id = 2 THEN 'user'
                ELSE 'guest'
            END
        FROM users u
        WHERE u.username = username_parameter AND u.email = email_parameter;
END;
$$;

SELECT create_get_user('soszaboss', 'boss@email.com', 'none',1);
