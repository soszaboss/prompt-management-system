BEGIN;

-- Drop existing tables and functions
DROP TABLE IF EXISTS roles, users, tokens_block_list, statuts, prompts, notes, votes, groupes, groupes_users CASCADE;
DROP FUNCTION IF EXISTS is_user_same_groupe, create_get_user, get_user_by_id, get_jti_or_none, trigger_set_timestamp, create_and_get_prompt, is_prompt_owned_by_user, get_prompts_by_status, update_prompt_status, update_prompt_prix, manage_prompt_status, calculate_vote_points, vote_for_prompt_activation, get_users_by_group, delete_user_and_dependencies, get_row_by_id, recalculate_prompt_price, check_prompt_activation;
DROP TYPE IF EXISTS prompt_type;
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
    ('En attente', $$'Lors de l'ajout d'un Prompt par un utilisateur.'$$),
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
    CONSTRAINT fk_roles_users FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE ON UPDATE CASCADE
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
    prix INT DEFAULT 1000,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_statut FOREIGN KEY(statut_id) REFERENCES statuts(id) ON UPDATE CASCADE
);

-- Create notes table
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    prompt_id INT NOT NULL,
    user_id INT NOT NULL,
    note NUMERIC NOT NULL CHECK (note BETWEEN -10 AND 10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_prompt FOREIGN KEY(prompt_id) REFERENCES prompts(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create groupes table
CREATE TABLE groupes(
    id SERIAL PRIMARY KEY,
    name VARCHAR(35) NOT NULL UNIQUE,
    description TEXT,
    created_by INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_users_groupes FOREIGN KEY(created_by) REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- Create groupes_users table
CREATE TABLE groupes_users(
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    groupe_id INT NOT NULL,
    added_by INT NOT NULL,
    added_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_users_groupes_users FOREIGN KEY(user_id) REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_added_by_groupes_users FOREIGN KEY(added_by) REFERENCES users(id) ON UPDATE CASCADE,
    CONSTRAINT fk_groupes_groupes_users FOREIGN KEY(groupe_id) REFERENCES groupes(id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create votes table
CREATE TABLE votes (
    id SERIAL PRIMARY KEY,
    prompt_id INT REFERENCES prompts(id) ON DELETE CASCADE ON UPDATE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    points INT CHECK (points IN (1, 2)),
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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

-- Fonction pour savoir si deux utilisateurs sont dans le même groupe
CREATE OR REPLACE FUNCTION is_user_same_groupe(user1_id INT, user2_id INT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    groupe_user1_id INT;
    groupe_user2_id INT;
BEGIN
    SELECT gu.groupe_id INTO groupe_user1_id FROM groupes_users gu WHERE gu.user_id = user1_id LIMIT 1;
    SELECT gu.groupe_id INTO groupe_user2_id FROM groupes_users gu WHERE gu.user_id = user2_id LIMIT 1;

    RETURN groupe_user1_id = groupe_user2_id;
END;
$$;

-- Fonction pour récupérer un utilisateur par son id

CREATE OR REPLACE FUNCTION create_get_user(
    p_username VARCHAR(25),
    p_email VARCHAR(50),
    p_password TEXT
)
RETURNS TABLE (
    id INT,
    username VARCHAR(25),
    email VARCHAR(50),
    user_role TEXT,
    is_activated BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
DECLARE
    user_id INT;
BEGIN
    -- Insérer le nouvel utilisateur
    INSERT INTO users (username, email, password, role_id)
    VALUES (p_username, p_email, p_password, 2) -- role_id 2 correspond au rôle "user"
    RETURNING users.id INTO user_id;

    -- Retourner les données de l'utilisateur créé
    RETURN QUERY
    SELECT
        u.id,
        u.username,
        u.email,
        CASE
            WHEN u.role_id = 1 THEN 'admin'
            WHEN u.role_id = 2 THEN 'user'
            ELSE 'guest'
        END,
        u.is_activated,
        u.created_at,
        u.updated_at
    FROM users u
    WHERE u.id = user_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_user_by_id(user_id INT)
RETURNS TABLE (id INT,username VARCHAR(25), email VARCHAR(50), user_role TEXT, is_activated BOOLEAN, created_at TIMESTAMPTZ, updated_at TIMESTAMPTZ)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
        SELECT
            u.id,
            u.username,
            u.email,
            CASE
                WHEN u.role_id = 1 THEN 'admin'
                WHEN u.role_id = 2 THEN 'user'
                ELSE 'guest'
            END,
            u.is_activated,
            u.created_at,
            u.updated_at
        FROM users u
        WHERE u.id = user_id;
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
CREATE TYPE prompt_type AS (
    id INT,
    prompt TEXT,
    user_id INT,
    prix INT,
    statut_id INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE OR REPLACE FUNCTION create_and_get_prompt(
    prompt_text TEXT,
    prompt_user INT,
    prompt_prix INT DEFAULT 1000,
    prompt_statut_id INT DEFAULT 1
)
RETURNS prompt_type
LANGUAGE plpgsql
AS $$
DECLARE
    prompt_row prompt_type;
BEGIN
    -- Insérer le nouveau prompt
    INSERT INTO prompts (prompt, user_id, prix,statut_id)
    VALUES (prompt_text, prompt_user, prompt_prix, prompt_statut_id)
    RETURNING id, prompt, user_id, prix, statut_id, created_at, updated_at
    INTO prompt_row;
    
    -- Retourner la ligne insérée
    RETURN prompt_row;
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
            s.id AS statuts,
            s.description AS statuts_description
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

CREATE OR REPLACE FUNCTION manage_prompt_status()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Rappeler les prompts si aucune action n'a été prise dans les deux jours
    UPDATE prompts
    SET statut_id = (SELECT id FROM statuts WHERE statut = 'Rappel'),
        updated_at = NOW()
    WHERE statut_id = (SELECT id FROM statuts WHERE statut = 'En attente')
    AND created_at <= NOW() - INTERVAL '1 day';

    -- Supprimer les prompts avec le statut "À supprimer"
    DELETE FROM prompts
    WHERE statut_id = (SELECT id FROM statuts WHERE statut = 'À supprimer');
END;
$$;

-- Calcul des points pour le vote
CREATE OR REPLACE FUNCTION calculate_vote_points(user_id INT, prompt_id INT)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    points INT;
    same_group BOOLEAN;
BEGIN
    same_group := is_user_same_groupe(user_id, (SELECT p.user_id FROM prompts p WHERE p.id = prompt_id));
    
    IF same_group THEN
        points := 2;
    ELSE
        points := 1;
    END IF;
    
    RETURN points;
END;
$$;

-- Calcul la note d'un membre du même groupe
CREATE OR REPLACE FUNCTION calculate_note(
    user_id INT,
    prompt_id INT,
    note NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    note_result NUMERIC;
    same_group BOOLEAN;
BEGIN
    same_group := is_user_same_groupe(user_id, (SELECT p.user_id FROM prompts p WHERE p.id = prompt_id));

    IF same_group THEN
        note_result := 0.6 * note;
    ELSE
        note_result := 0.4 * note;
    END IF;

    RETURN note_result;
END;
$$;

-- Fonction pour recalculer le prix du prompt
CREATE OR REPLACE FUNCTION recalculate_prompt_price(p_id INT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    avg_note FLOAT;
    new_price INT;
BEGIN
    SELECT AVG(note) INTO avg_note
    FROM notes
    WHERE prompt_id = p_id;

    new_price := 1000 * (1 + avg_note);

    UPDATE prompts
    SET prix = new_price, updated_at = NOW()
    WHERE id = p_id;
END;
$$;

-- Fonction pour vérifier l'activation du prompt
CREATE OR REPLACE FUNCTION check_prompt_activation(p_id INT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    IF (SELECT SUM(points) FROM votes WHERE prompt_id = p_id) >= 6 THEN
        UPDATE prompts
        SET statut_id = (SELECT id FROM statuts WHERE statut = 'Activer'), updated_at = NOW()
        WHERE id = p_id;
    END IF;
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

-- Fonction pour récupérer le JTI si existant dans la liste de blocage
CREATE OR REPLACE FUNCTION get_jti_or_none(jti_token VARCHAR)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
DECLARE
    result VARCHAR;
BEGIN
    SELECT jti INTO result
    FROM tokens_block_list
    WHERE jti = jti_token;

    RETURN result;
END;
$$;

CREATE TRIGGER set_timestamp_users
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE TRIGGER set_timestamp_prompts
BEFORE UPDATE ON prompts
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

CREATE OR REPLACE FUNCTION delete_unactivated_users()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM users
    WHERE is_activated = FALSE
    AND created_at < NOW() - INTERVAL '15 minutes';
END;
$$;


CREATE OR REPLACE FUNCTION trigger_check_unactivated_users()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    PERFORM delete_unactivated_users();
    RETURN NEW;
END;
$$;



-- Création des triggers
CREATE TRIGGER check_unactivated_users_trigger
AFTER INSERT ON users
FOR EACH STATEMENT
EXECUTE FUNCTION trigger_check_unactivated_users();

-- CREATE TRIGGER trigger_recalculate_prompt_price
-- AFTER INSERT OR UPDATE ON notes
-- FOR EACH ROW
-- EXECUTE FUNCTION recalculate_prompt_price();

-- CREATE TRIGGER trigger_check_prompt_activation
-- AFTER INSERT ON votes
-- FOR EACH ROW
-- EXECUTE FUNCTION check_prompt_activation();

-- Indices
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

COMMIT;
