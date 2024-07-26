BEGIN;

-- Insert roles
INSERT INTO roles (role, description) VALUES 
    ('admin', $$'Peut créer des utilisateurs individuels ou des groupes d'utilisateurs, valide, demande la modification, ou supprime des Prompts, peut voir tous les Prompts mais ne peut pas voter ni noter.'$$),
    ('user', $$'Proposent des Prompts à vendre, peuvent voter pour l'activation des Prompts en attente de validation, peuvent noter les Prompts activés, mais ne peuvent ni voter ni noter leurs propres Prompts, les membres d'un même groupe ont un impact plus fort sur la note et les votes.'$$),
    ('guest', $$'Peut consulter un Prompt, Peut rechercher un prompt par son contenu ou par mot clefs, Peut Acheter un Prompt.'$$);

-- Insert statuses
INSERT INTO statuts (statut, description) VALUES
    ('En attente', $$'Lors de l'ajout d'un Prompt par un utilisateur.'$$),
    ('Activer', $$'Après validation par un administrateur ou par vote.'$$),
    ('À revoir', $$'Si l'administrateur demande une modification.'$$),
    ('Rappel', $$'Si aucune action n'est prise par l'administrateur dans les deux jours suivant l'ajout ou une demande de suppression/modification.'$$),
    ('À supprimer', $$'Lorsque l'utilisateur demande la suppression de son propre Prompt.'$$);

-- Insert users
INSERT INTO users (username, email, password, is_activated, role_id) VALUES 
    ('admin', 'admin@example.com', 'adminpassword', TRUE, 1),
    ('user1', 'user1@example.com', 'password1', TRUE, 2),
    ('user2', 'user2@example.com', 'password2', TRUE, 2),
    ('guest', 'guest@example.com', 'guestpassword', FALSE, 3);

-- Insert groups
INSERT INTO groupes (name, description, created_by) VALUES
    ('Group 1', 'Description for Group 1', 2),
    ('Group 2', 'Description for Group 2', 3);

-- Insert group members
INSERT INTO groupes_users (user_id, groupe_id, added_by) VALUES 
    (2, 1, 1),
    (3, 2, 1);

-- Insert prompts
INSERT INTO prompts (prompt, user_id, statut_id, prix) VALUES
    ('Prompt 1', 2, 1, 1000),
    ('Prompt 2', 3, 1, 1000);

-- Insert notes
INSERT INTO notes (prompt_id, user_id, note) VALUES
    (1, 3, 5),
    (2, 2, -3);

-- Insert votes
INSERT INTO votes (prompt_id, user_id, points) VALUES
    (1, 2, 2),
    (2, 3, 1);

-- Insert tokens_block_list
INSERT INTO tokens_block_list (jti) VALUES 
    ('sample_jti_1'),
    ('sample_jti_2');

COMMIT;