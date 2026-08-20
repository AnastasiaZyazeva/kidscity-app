--
-- PostgreSQL database dump
--

\restrict V23ioMlwfvY5zfwD3S12sclh89aSW4EYJtbqzwnsoddbmu2m1yCHBuMIJpXhNlC

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: children; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.children (
    id_child integer NOT NULL,
    name character varying(100) NOT NULL,
    age integer NOT NULL,
    id_parent integer
);


ALTER TABLE public.children OWNER TO postgres;

--
-- Name: children_id_child_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.children_id_child_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.children_id_child_seq OWNER TO postgres;

--
-- Name: children_id_child_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.children_id_child_seq OWNED BY public.children.id_child;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.locations (
    id_location integer NOT NULL,
    name_location character varying(150) NOT NULL,
    age_range character varying(20),
    description text,
    cost numeric(10,2),
    image text,
    id_preference integer
);


ALTER TABLE public.locations OWNER TO postgres;

--
-- Name: locations_id_location_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.locations_id_location_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.locations_id_location_seq OWNER TO postgres;

--
-- Name: locations_id_location_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.locations_id_location_seq OWNED BY public.locations.id_location;


--
-- Name: parents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.parents (
    id_parent integer NOT NULL,
    last_name character varying(100) NOT NULL,
    first_name character varying(100) NOT NULL,
    middle_name character varying(100),
    phone character varying(20),
    login character varying(50) NOT NULL,
    password character varying(255) NOT NULL
);


ALTER TABLE public.parents OWNER TO postgres;

--
-- Name: parents_id_parent_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.parents_id_parent_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.parents_id_parent_seq OWNER TO postgres;

--
-- Name: parents_id_parent_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.parents_id_parent_seq OWNED BY public.parents.id_parent;


--
-- Name: preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.preferences (
    id_preference integer NOT NULL,
    id_location integer,
    age_preference character varying(20)
);


ALTER TABLE public.preferences OWNER TO postgres;

--
-- Name: preferences_id_preference_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.preferences_id_preference_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.preferences_id_preference_seq OWNER TO postgres;

--
-- Name: preferences_id_preference_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.preferences_id_preference_seq OWNED BY public.preferences.id_preference;


--
-- Name: tickets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tickets (
    id_ticket integer NOT NULL,
    id_parent integer,
    id_child integer,
    id_location integer,
    data date
);


ALTER TABLE public.tickets OWNER TO postgres;

--
-- Name: tickets_id_ticket_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tickets_id_ticket_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tickets_id_ticket_seq OWNER TO postgres;

--
-- Name: tickets_id_ticket_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tickets_id_ticket_seq OWNED BY public.tickets.id_ticket;


--
-- Name: children id_child; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.children ALTER COLUMN id_child SET DEFAULT nextval('public.children_id_child_seq'::regclass);


--
-- Name: locations id_location; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations ALTER COLUMN id_location SET DEFAULT nextval('public.locations_id_location_seq'::regclass);


--
-- Name: parents id_parent; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parents ALTER COLUMN id_parent SET DEFAULT nextval('public.parents_id_parent_seq'::regclass);


--
-- Name: preferences id_preference; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preferences ALTER COLUMN id_preference SET DEFAULT nextval('public.preferences_id_preference_seq'::regclass);


--
-- Name: tickets id_ticket; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets ALTER COLUMN id_ticket SET DEFAULT nextval('public.tickets_id_ticket_seq'::regclass);


--
-- Name: children children_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.children
    ADD CONSTRAINT children_pkey PRIMARY KEY (id_child);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id_location);


--
-- Name: parents parents_login_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parents
    ADD CONSTRAINT parents_login_key UNIQUE (login);


--
-- Name: parents parents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.parents
    ADD CONSTRAINT parents_pkey PRIMARY KEY (id_parent);


--
-- Name: preferences preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preferences
    ADD CONSTRAINT preferences_pkey PRIMARY KEY (id_preference);


--
-- Name: tickets tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_pkey PRIMARY KEY (id_ticket);


--
-- Name: idx_children_parent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_children_parent ON public.children USING btree (id_parent);


--
-- Name: idx_tickets_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_location ON public.tickets USING btree (id_location);


--
-- Name: idx_tickets_parent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_parent ON public.tickets USING btree (id_parent);


--
-- Name: children children_id_parent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.children
    ADD CONSTRAINT children_id_parent_fkey FOREIGN KEY (id_parent) REFERENCES public.parents(id_parent) ON DELETE CASCADE;


--
-- Name: locations preferences_id_location_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT preferences_id_location_fkey FOREIGN KEY (id_preference) REFERENCES public.preferences(id_preference) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: tickets tickets_id_child_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_id_child_fkey FOREIGN KEY (id_child) REFERENCES public.children(id_child) ON DELETE CASCADE;


--
-- Name: tickets tickets_id_location_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_id_location_fkey FOREIGN KEY (id_location) REFERENCES public.locations(id_location) ON DELETE CASCADE;


--
-- Name: tickets tickets_id_parent_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_id_parent_fkey FOREIGN KEY (id_parent) REFERENCES public.parents(id_parent) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict V23ioMlwfvY5zfwD3S12sclh89aSW4EYJtbqzwnsoddbmu2m1yCHBuMIJpXhNlC

