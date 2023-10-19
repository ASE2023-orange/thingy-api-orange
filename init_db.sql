-- This file is used when launching Posgresql database for the first time.
-- It creates necessary schema for keycloak as well as relations for metadata.

-- Create the "keycloak" schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS keycloak;

-- Create the "Plant" table in the "public" schema if it doesn't exist
CREATE TABLE IF NOT EXISTS public.Plant (
    id serial PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lng DOUBLE PRECISION NOT NULL
);