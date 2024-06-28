
BEGIN;
    DROP TABLE IF EXISTS roles, users, statuts, prompts;
-- Create roles table
    CREATE TABLE roles (
        id SERIAL PRIMARY KEY,
        role VARCHAR(25) NOT NULL,
        description TEXT
    );

    INSERT INTO roles (role, description) VALUES (
                                                    'admin',
                                                    $$Peut créer des utilisateurs individuels ou des groupes d'utilisateurs,
                                                        valide, demande la modification, ou supprime des Prompts,
                                                        peut voir tous les Prompts mais ne peut pas voter ni noter.$$
                                                ),
                                                (
                                                    'user',
                                                    $$Proposent des Prompts à vendre,
                                                    peuvent voter pour l'activation des Prompts en attente de validation,
                                                    peuvent noter les Prompts activés, mais ne peuvent ni voter ni noter leurs propres Prompts,
                                                    les membres d'un même groupe ont un impact plus fort sur la note et les votes.$$
                                                ),
                                                (
                                                    'guest',
                                                    '
                                                        Peut consulter un Prompt, 
                                                        Peut rechercher un prompt par son contenu ou par mot clefs,
                                                        Peut Acheter un Prompt
                                                    '
                                                );
    -- Create statuts table
    CREATE TABLE statuts (
                            id SERIAL PRIMARY KEY,
                            statut VARCHAR(25),
                            description TEXT
                        );

    INSERT INTO statuts (statut, description) VALUES('En attente' , $$'Lors de l'ajout d'un Prompt par un utilisateur.'$$ ),
                                                    ('Activer' , $$'Après validation par un administrateur ou par vote.'$$),
                                                    ( 'À revoir' ,$$' Si l'administrateur demande une modification.'$$),
                                                    ('Rappel' , $$'Si aucune action n'est prise par l'administrateur dans les deux jours suivant l'ajout ou une demande de suppression/modification.'$$),
                                                    (' À supprimer' , $$'Lorsque l'utilisateur demande la suppression de son propre Prompt.'$$);
    -- Create users table
    CREATE TABLE users (
                            id SERIAL PRIMARY KEY,
                            username VARCHAR(25) UNIQUE,
                            email VARCHAR(50) UNIQUE, 
                            password TEXT NOT NULL,
                            role_id INT NOT NULL DEFAULT 3,
                            CONSTRAINT fk_roles_users FOREIGN KEY (role_id) REFERENCES roles(id)
                        );

    -- Create prompts table
    CREATE TABLE prompts (
                            id SERIAL PRIMARY KEY,
                            prompt TEXT NOT NULL,
                            user_id INT NOT NULL,
                            statut_id INT NOT NULL DEFAULT 1,
                            CONSTRAINT fk_users_prompts FOREIGN KEY (user_id) REFERENCES users(id),
                            CONSTRAINT fk_statuts_prompts FOREIGN KEY (statut_id) REFERENCES statuts(id)
                        );


    CREATE OR REPLACE FUNCTION get_user_by_id(user_id INT)
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
COMMIT
