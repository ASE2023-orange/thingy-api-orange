-- This file is used when launching Posgresql database for the first time.
-- It creates necessary schema for keycloak as well as relations for metadata.

-- Create the "keycloak" schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS keycloak;

-- Create the "Plant" table in the "public" schema if it doesn't exist
-- Note that the script might fail if keycloak is not initialized,
-- if so, rerun the script manually.
CREATE TABLE IF NOT EXISTS public."Plant"
(
    id character varying(36) NOT NULL,
    friendly_name character varying(255),
    thingy_id character varying(255),
    locality character varying(255),
    npa character varying(12),
    lat numeric,
    lng numeric,
    max_power integer,
    nr_panels integer,
    contact_person character varying(36),
    created_at timestamp DEFAULT NOW(),
    updated_at timestamp DEFAULT NOW(),
    PRIMARY KEY (id),
    CONSTRAINT fk_plant_user FOREIGN KEY (contact_person)
        REFERENCES keycloak.user_entity (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE SET NULL
        NOT VALID
);

-- Create trigger function to update timestamp when modifying records.
CREATE OR REPLACE FUNCTION public.trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_plant_updated_at
BEFORE UPDATE ON public."Plant"
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

-- Creates table to store all known thingys id
CREATE TABLE IF NOT EXISTS public.thingy_id
(
    id serial NOT NULL,
    name character varying(255) COLLATE pg_catalog."default",
    created_at timestamp with time zone DEFAULT now(),
    updated_at time with time zone DEFAULT now(),
    CONSTRAINT thingy_id_pkey PRIMARY KEY (id)
)

-- Table: public.Maintenance

CREATE TABLE IF NOT EXISTS public."Maintenance"
(
    thingy_id character varying COLLATE pg_catalog."default" NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    maintenance_start timestamp without time zone[],
    maintenance_end timestamp without time zone[],
    maintenance_status boolean DEFAULT false,
    CONSTRAINT "Maintenance_pkey" PRIMARY KEY (thingy_id)
)