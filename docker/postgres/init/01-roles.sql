-- ascua_owner owns the schema and runs migrations.
-- ascua_app is the runtime role: it never bypasses row-level security.
CREATE ROLE ascua_owner LOGIN PASSWORD 'ascua_owner' CREATEDB NOBYPASSRLS;
CREATE ROLE ascua_app LOGIN PASSWORD 'ascua_app' NOBYPASSRLS;
-- Lets the owner (and the test runner) drop to the app role with SET ROLE.
GRANT ascua_app TO ascua_owner;

CREATE DATABASE ascua OWNER ascua_owner;
\connect ascua
ALTER SCHEMA public OWNER TO ascua_owner;
GRANT USAGE ON SCHEMA public TO ascua_app;
ALTER DEFAULT PRIVILEGES FOR ROLE ascua_owner IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ascua_app;
ALTER DEFAULT PRIVILEGES FOR ROLE ascua_owner IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO ascua_app;
