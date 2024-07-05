BEGIN;

    DROP TABLE IF EXISTS roles, users, tokens_block_list, statuts, prompts, notes, votes, groupes, groupes_users CASCADE;
    DROP FUNCTION IF EXISTS is_user_same_groupe, create_get_user, get_user_by_id, get_jti_or_none, trigger_set_timestamp, create_and_get_prompt, is_prompt_owned_by_user, get_prompts_by_status, update_prompt_status, update_prompt_prix, manage_prompt_status, calculate_vote_points, vote_for_prompt_activation, get_users_by_group, delete_user_and_dependencies, get_row_by_id;

    -- Create roles table
    CREATE TABLE roles (
        id SERIAL PRIMARY KEY,
        role VARCHAR(25) NOT NULL,
        description TEXT
    );

    INSERT INTO roles (role, description) VALUES 
        ('admin', $$'Peut créer des utilisateurs individuels ou des groupes d'utilisateurs, valide, demande la modification, ou supprime des Prompts, peut voir tous les Prompts mais ne peut pas voter ni noter.'$$),
        ('user', $$'Proposent des Prompts à vendre, peuvent voter pour l'activation des Prompts en attente de validation, peuvent noter les Prompts activés, mais ne peuvent ni voter ni noter leurs propres Prompts, les membres d'un même groupe ont un impact plus fort sur la note et les votes.'$$),
        ('guest', $$'Peut consulter un Prompt, Peut rechercher un prompt par son contenu ou par mot clefs, Peut Acheter un Prompt.'$$);

    -- Create statuts table
    CREATE TABLE statuts (
        id SERIAL PRIMARY KEY,
        statut VARCHAR(25),
        description TEXT
    );

    INSERT INTO statuts (statut, description) VALUES
        ('En attente', $$'Lors de l'ajout d\'un Prompt par un utilisateur.'$$),
        ('Activer', $$'Après validation par un administrateur ou par vote.'$$),
        ('À revoir', $$'Si l'administrateur demande une modification.'$$),
        ('Rappel', $$'Si aucune action n'est prise par l'administrateur dans les deux jours suivant l'ajout ou une demande de suppression/modification.'$$),
        ('À supprimer', $$'Lorsque l'utilisateur demande la suppression de son propre Prompt.'$$);

    -- Create users table
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(25) UNIQUE,
        email VARCHAR(50) UNIQUE, 
        password TEXT NOT NULL,
        is_activated BOOLEAN DEFAULT FALSE,
        role_id INT NOT NULL DEFAULT 3,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT fk_roles_users FOREIGN KEY (role_id) REFERENCES roles(id)
    );

    CREATE TABLE tokens_block_list(
        id SERIAL PRIMARY KEY,
        jti VARCHAR UNIQUE, 
        create_at DATE DEFAULT CURRENT_TIMESTAMP
    );

    -- Create prompts table
    CREATE TABLE prompts (
        id SERIAL PRIMARY KEY,
        prompt TEXT NOT NULL,
        user_id INT NOT NULL,
        statut_id INT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id),
        CONSTRAINT fk_statut FOREIGN KEY(statut_id) REFERENCES statuts(id)
    );

    -- Create notes table
    CREATE TABLE notes (
        id SERIAL PRIMARY KEY,
        prompt_id INT NOT NULL,
        user_id INT NOT NULL,
        note INT NOT NULL CHECK (note BETWEEN -10 AND 10),
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        CONSTRAINT fk_prompt FOREIGN KEY(prompt_id) REFERENCES prompts(id),
        CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id)
    );

    -- Create groupes table
    CREATE TABLE groupes(
        id SERIAL PRIMARY KEY,
        name VARCHAR(35) NOT NULL UNIQUE,
        description TEXT,
        created_by INT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT fk_users_groupes FOREIGN KEY(created_by) REFERENCES users(id)
    );

    -- Create groupes_users table
    CREATE TABLE groupes_users(
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        groupe_id INT NOT NULL,
        CONSTRAINT fk_users_groupes_users FOREIGN KEY(user_id) REFERENCES users(id),
        CONSTRAINT fk_groupes_groupes_users FOREIGN KEY(groupe_id) REFERENCES groupes(id)
    );


    -- Create votes table
    CREATE TABLE votes (
        id SERIAL PRIMARY KEY,
        prompt_id INT REFERENCES prompts(id),
        user_id INT REFERENCES users(id),
        groupe_id INT REFERENCES groupes(id),
        points INT CHECK (points IN (1, 2)),
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    /*
    --------------------------------------------------------------------------------------------------------------------------------------
                                                                Fonctions
    --------------------------------------------------------------------------------------------------------------------------------------
    */

    -- Fonction pour savoir si deux utilisateurs sont dans le même groupe
    CREATE OR REPLACE FUNCTION is_user_same_groupe(user1_id INT, user2_id INT)
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

    -- Fonction pour récupérer un utilisateur par son id
    CREATE OR REPLACE FUNCTION get_user_by_id(user_id INT)
    RETURNS TABLE (username VARCHAR(25), email VARCHAR(50), user_role TEXT)
    LANGUAGE plpgsql
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
            RETURN;
        END IF;
    END;
    $$;

    -- Fonction pour créer un nouvel utilisateur et retourner ses informations
    CREATE OR REPLACE FUNCTION create_get_user(username_parameter VARCHAR, email_parameter VARCHAR, password_parameter TEXT, role_id_parameter INT)
    RETURNS TABLE (
        user_id INT,
        user_username VARCHAR(25),
        user_email VARCHAR(50),
        user_role TEXT
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        INSERT INTO users (username, email, password, role_id)
        VALUES (username_parameter, email_parameter, password_parameter, role_id_parameter)
        RETURNING id, username, email,
            CASE
                WHEN role_id = 1 THEN 'admin'
                WHEN role_id = 2 THEN 'user'
                ELSE 'guest'
            END
        INTO user_id, user_username, user_email, user_role;
    END;
    $$;

    -- Fonction pour supprimer un utilisateur et toutes ses dépendances
    CREATE OR REPLACE FUNCTION delete_user_and_dependencies(user_id INT)
    RETURNS VOID
    LANGUAGE plpgsql
    AS $$
    BEGIN
        DELETE FROM prompts WHERE user_id = user_id;
        DELETE FROM groupes_users WHERE user_id = user_id;
        DELETE FROM users WHERE id = user_id;
    END;
    $$;

    -- Fonction pour afficher les utilisateurs d'un groupe
    CREATE OR REPLACE FUNCTION get_users_by_group(group_id INT)
    RETURNS TABLE (user_id INT, username VARCHAR, email VARCHAR)
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
            SELECT u.id, u.username, u.email
            FROM users u
            JOIN groupes_users gu ON u.id = gu.user_id
            WHERE gu.groupe_id = group_id;
    END;
    $$;

    -- Fonction pour la gestion des prompts
    CREATE OR REPLACE FUNCTION create_and_get_prompt(prompt_text TEXT, prompt_user INT, prompt_statut_id INT DEFAULT 1)
    RETURNS TABLE (
        prompt_id INT,
        prompt TEXT,
        users_id INT,
        statuts_id INT,
        created_at TIMESTAMPTZ,
        updated_at TIMESTAMPTZ
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        -- Insérer le nouveau prompt
        INSERT INTO prompts (prompt, user_id, statut_id)
        VALUES (prompt_text, prompt_user, prompt_statut_id)
        RETURNING id, prompt, user_id, statut_id, created_at, updated_at
        INTO prompt_id, prompt, users_id, statuts_id, created_at, updated_at;

        -- Retourner les informations du nouveau prompt
        RETURN QUERY
            SELECT prompt_id, prompt, users_id, statuts_id, created_at, updated_at;
    END;
    $$;

    CREATE OR REPLACE FUNCTION is_prompt_owned_by_user(prompt_id INT, user_id INT)
    RETURNS BOOLEAN
    LANGUAGE plpgsql
    AS $$
    DECLARE
        result BOOLEAN;
    BEGIN
        SELECT CASE WHEN user_id = p.user_id THEN TRUE ELSE FALSE END INTO result
        FROM prompts p
        WHERE p.id = prompt_id;
        
        RETURN result;
    END;
    $$;

    CREATE OR REPLACE FUNCTION get_prompts_by_status(status VARCHAR)
    RETURNS TABLE (
        id INT,
        prompt TEXT,
        username VARCHAR,
        email VARCHAR,
        status_id INT,
        status_description VARCHAR
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
            SELECT
                p.id,
                p.prompt,
                u.username,
                u.email,
                s.id AS status_id,
                s.description AS status_description
            FROM prompts p
            JOIN users u ON p.user_id = u.id
            JOIN statuts s ON p.statut_id = s.id
            WHERE s.statut = status;
    END;
    $$;

    CREATE OR REPLACE FUNCTION update_prompt_status(prompt_id INT, new_status_id INT)
    RETURNS VOID
    LANGUAGE plpgsql
    AS $$
    BEGIN
        UPDATE prompts
        SET statut_id = new_status_id, updated_at = NOW()
        WHERE id = prompt_id;
    END;
    $$;

    CREATE OR REPLACE FUNCTION update_prompt_prix(prompt_id INT, new_prix INT)
    RETURNS VOID
    LANGUAGE plpgsql
    AS $$
    BEGIN
        UPDATE prompts
        SET prix = new_prix, updated_at = NOW()
        WHERE id = prompt_id;
    END;
    $$;

    CREATE OR REPLACE FUNCTION manage_prompt_status(prompt_id INT)
    RETURNS VOID
    LANGUAGE plpgsql
    AS $$
    BEGIN
        UPDATE prompts
        SET statut_id = 4 -- statut_id pour "Rappel"
        WHERE id = prompt_id
        AND statut_id = 1
        AND NOW() > created_at + INTERVAL '2 days';
    END;
    $$;

    CREATE OR REPLACE FUNCTION calculate_vote_points(prompt_id INT, user_id INT, groupe_id INT)
    RETURNS INT
    LANGUAGE plpgsql
    AS $$
    DECLARE
        points INT;
    BEGIN
        SELECT CASE
            WHEN is_user_same_groupe(prompt_id, user_id) THEN 2
            ELSE 1
        END
        INTO points;

        RETURN points;
    END;
    $$;

    CREATE OR REPLACE FUNCTION vote_for_prompt_activation(prompt_id INT, user_id INT)
    RETURNS VOID
    LANGUAGE plpgsql
    AS $$
    BEGIN
        INSERT INTO votes (prompt_id, user_id, points)
        VALUES (prompt_id, user_id, calculate_vote_points(prompt_id, user_id, 0));
    END;
    $$;

    -- Fonction pour obtenir un enregistrement par ID depuis une table donnée
    CREATE OR REPLACE FUNCTION get_row_by_id(table_name TEXT, row_id INT)
    RETURNS JSON
    LANGUAGE plpgsql
    AS $$
    DECLARE
        result JSON;
    BEGIN
        EXECUTE format('SELECT row_to_json(%I.*) FROM %I WHERE id = $1', table_name, table_name) USING row_id INTO result;
        RETURN result;
    END;
    $$;

    CREATE OR REPLACE FUNCTION trigger_set_timestamp()
    RETURNS TRIGGER
    LANGUAGE plpgsql
    AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$;

    -- Trigger pour mettre à jour le timestamp updated_at lors d'une modification
    CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_timestamp();

    CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON prompts
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_timestamp();

    CREATE TRIGGER set_timestamp
    BEFORE UPDATE ON groupes
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_timestamp();

COMMIT;
