--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Debian 16.8-1.pgdg120+1)
-- Dumped by pg_dump version 17.5

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

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: descriptions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.descriptions (
    id uuid NOT NULL,
    term_id uuid NOT NULL,
    raw_text character varying NOT NULL,
    cleaned_text character varying NOT NULL,
    stemmed_text character varying NOT NULL,
    language character varying NOT NULL,
    info character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.descriptions OWNER TO "user";

--
-- Name: embeddings; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.embeddings (
    id uuid NOT NULL,
    description_id uuid NOT NULL,
    embedding public.vector(300),
    language character varying NOT NULL,
    info character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.embeddings OWNER TO "user";

--
-- Name: graphs; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.graphs (
    id uuid NOT NULL,
    description_id uuid NOT NULL,
    triplet_count integer NOT NULL,
    graph jsonb NOT NULL,
    language character varying NOT NULL,
    info character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.graphs OWNER TO "user";

--
-- Name: terms; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.terms (
    id uuid NOT NULL,
    topic_id uuid NOT NULL,
    language character varying NOT NULL,
    raw_text character varying NOT NULL,
    cleaned_text character varying NOT NULL,
    stemmed_text character varying NOT NULL,
    first_letter character varying(1) NOT NULL,
    info character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.terms OWNER TO "user";

--
-- Name: topics; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.topics (
    id uuid NOT NULL,
    name character varying NOT NULL,
    info character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.topics OWNER TO "user";

--
-- Name: triplets; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.triplets (
    id uuid NOT NULL,
    description_id uuid NOT NULL,
    "position" integer NOT NULL,
    subject character varying NOT NULL,
    subject_type character varying,
    predicate character varying NOT NULL,
    predicate_type character varying,
    object character varying NOT NULL,
    object_type character varying,
    language character varying NOT NULL,
    info character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.triplets OWNER TO "user";

--
-- Name: descriptions descriptions_cleaned_text_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.descriptions
    ADD CONSTRAINT descriptions_cleaned_text_key UNIQUE (cleaned_text);


--
-- Name: descriptions descriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.descriptions
    ADD CONSTRAINT descriptions_pkey PRIMARY KEY (id);


--
-- Name: descriptions descriptions_raw_text_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.descriptions
    ADD CONSTRAINT descriptions_raw_text_key UNIQUE (raw_text);


--
-- Name: descriptions descriptions_stemmed_text_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.descriptions
    ADD CONSTRAINT descriptions_stemmed_text_key UNIQUE (stemmed_text);


--
-- Name: embeddings embeddings_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.embeddings
    ADD CONSTRAINT embeddings_pkey PRIMARY KEY (id);


--
-- Name: graphs graphs_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.graphs
    ADD CONSTRAINT graphs_pkey PRIMARY KEY (id);


--
-- Name: terms terms_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.terms
    ADD CONSTRAINT terms_pkey PRIMARY KEY (id);


--
-- Name: topics topics_name_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_name_key UNIQUE (name);


--
-- Name: topics topics_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (id);


--
-- Name: triplets triplets_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.triplets
    ADD CONSTRAINT triplets_pkey PRIMARY KEY (id);


--
-- Name: ix_descriptions_term_id; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_descriptions_term_id ON public.descriptions USING btree (term_id);


--
-- Name: ix_embeddings_description_id; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_embeddings_description_id ON public.embeddings USING btree (description_id);


--
-- Name: ix_graphs_description_id; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_graphs_description_id ON public.graphs USING btree (description_id);


--
-- Name: ix_terms_topic_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_terms_topic_id ON public.terms USING btree (topic_id);


--
-- Name: ix_triplets_description_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_triplets_description_id ON public.triplets USING btree (description_id);


--
-- Name: descriptions descriptions_term_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.descriptions
    ADD CONSTRAINT descriptions_term_id_fkey FOREIGN KEY (term_id) REFERENCES public.terms(id);


--
-- Name: embeddings embeddings_description_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.embeddings
    ADD CONSTRAINT embeddings_description_id_fkey FOREIGN KEY (description_id) REFERENCES public.descriptions(id);


--
-- Name: graphs graphs_description_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.graphs
    ADD CONSTRAINT graphs_description_id_fkey FOREIGN KEY (description_id) REFERENCES public.descriptions(id);


--
-- Name: terms terms_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.terms
    ADD CONSTRAINT terms_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id);


--
-- Name: triplets triplets_description_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.triplets
    ADD CONSTRAINT triplets_description_id_fkey FOREIGN KEY (description_id) REFERENCES public.descriptions(id);


--
-- PostgreSQL database dump complete
--

