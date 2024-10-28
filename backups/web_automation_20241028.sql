--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-0ubuntu0.24.04.2)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: poording
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO poording;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actions; Type: TABLE; Schema: public; Owner: poording
--

CREATE TABLE public.actions (
    id integer NOT NULL,
    website_id integer,
    name character varying(100) NOT NULL,
    action_type character varying(50) NOT NULL,
    selector_id integer,
    parameters jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.actions OWNER TO poording;

--
-- Name: actions_id_seq; Type: SEQUENCE; Schema: public; Owner: poording
--

CREATE SEQUENCE public.actions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.actions_id_seq OWNER TO poording;

--
-- Name: actions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: poording
--

ALTER SEQUENCE public.actions_id_seq OWNED BY public.actions.id;


--
-- Name: selectors; Type: TABLE; Schema: public; Owner: poording
--

CREATE TABLE public.selectors (
    id integer NOT NULL,
    website_id integer,
    name character varying(100) NOT NULL,
    selector_type character varying(20) NOT NULL,
    selector_value text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.selectors OWNER TO poording;

--
-- Name: selectors_id_seq; Type: SEQUENCE; Schema: public; Owner: poording
--

CREATE SEQUENCE public.selectors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.selectors_id_seq OWNER TO poording;

--
-- Name: selectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: poording
--

ALTER SEQUENCE public.selectors_id_seq OWNED BY public.selectors.id;


--
-- Name: user_preferences; Type: TABLE; Schema: public; Owner: poording
--

CREATE TABLE public.user_preferences (
    id integer NOT NULL,
    user_id integer,
    website_id integer,
    preference_key character varying(100) NOT NULL,
    preference_value jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_preferences OWNER TO poording;

--
-- Name: user_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: poording
--

CREATE SEQUENCE public.user_preferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_preferences_id_seq OWNER TO poording;

--
-- Name: user_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: poording
--

ALTER SEQUENCE public.user_preferences_id_seq OWNED BY public.user_preferences.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: poording
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.users OWNER TO poording;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: poording
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO poording;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: poording
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: websites; Type: TABLE; Schema: public; Owner: poording
--

CREATE TABLE public.websites (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    url character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.websites OWNER TO poording;

--
-- Name: websites_id_seq; Type: SEQUENCE; Schema: public; Owner: poording
--

CREATE SEQUENCE public.websites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.websites_id_seq OWNER TO poording;

--
-- Name: websites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: poording
--

ALTER SEQUENCE public.websites_id_seq OWNED BY public.websites.id;


--
-- Name: workflow_steps; Type: TABLE; Schema: public; Owner: poording
--

CREATE TABLE public.workflow_steps (
    id integer NOT NULL,
    workflow_id integer,
    action_id integer,
    step_order integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.workflow_steps OWNER TO poording;

--
-- Name: workflow_steps_id_seq; Type: SEQUENCE; Schema: public; Owner: poording
--

CREATE SEQUENCE public.workflow_steps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflow_steps_id_seq OWNER TO poording;

--
-- Name: workflow_steps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: poording
--

ALTER SEQUENCE public.workflow_steps_id_seq OWNED BY public.workflow_steps.id;


--
-- Name: workflows; Type: TABLE; Schema: public; Owner: poording
--

CREATE TABLE public.workflows (
    id integer NOT NULL,
    user_id integer,
    website_id integer,
    name character varying(255) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.workflows OWNER TO poording;

--
-- Name: workflows_id_seq; Type: SEQUENCE; Schema: public; Owner: poording
--

CREATE SEQUENCE public.workflows_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.workflows_id_seq OWNER TO poording;

--
-- Name: workflows_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: poording
--

ALTER SEQUENCE public.workflows_id_seq OWNED BY public.workflows.id;


--
-- Name: actions id; Type: DEFAULT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.actions ALTER COLUMN id SET DEFAULT nextval('public.actions_id_seq'::regclass);


--
-- Name: selectors id; Type: DEFAULT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.selectors ALTER COLUMN id SET DEFAULT nextval('public.selectors_id_seq'::regclass);


--
-- Name: user_preferences id; Type: DEFAULT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.user_preferences ALTER COLUMN id SET DEFAULT nextval('public.user_preferences_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: websites id; Type: DEFAULT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.websites ALTER COLUMN id SET DEFAULT nextval('public.websites_id_seq'::regclass);


--
-- Name: workflow_steps id; Type: DEFAULT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.workflow_steps ALTER COLUMN id SET DEFAULT nextval('public.workflow_steps_id_seq'::regclass);


--
-- Name: workflows id; Type: DEFAULT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.workflows ALTER COLUMN id SET DEFAULT nextval('public.workflows_id_seq'::regclass);


--
-- Data for Name: actions; Type: TABLE DATA; Schema: public; Owner: poording
--

COPY public.actions (id, website_id, name, action_type, selector_id, parameters, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: selectors; Type: TABLE DATA; Schema: public; Owner: poording
--

COPY public.selectors (id, website_id, name, selector_type, selector_value, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_preferences; Type: TABLE DATA; Schema: public; Owner: poording
--

COPY public.user_preferences (id, user_id, website_id, preference_key, preference_value, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: poording
--

COPY public.users (id, username, email, password_hash, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: websites; Type: TABLE DATA; Schema: public; Owner: poording
--

COPY public.websites (id, name, url, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: workflow_steps; Type: TABLE DATA; Schema: public; Owner: poording
--

COPY public.workflow_steps (id, workflow_id, action_id, step_order, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: workflows; Type: TABLE DATA; Schema: public; Owner: poording
--

COPY public.workflows (id, user_id, website_id, name, description, created_at, updated_at) FROM stdin;
\.


--
-- Name: actions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: poording
--

SELECT pg_catalog.setval('public.actions_id_seq', 1, false);


--
-- Name: selectors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: poording
--

SELECT pg_catalog.setval('public.selectors_id_seq', 1, false);


--
-- Name: user_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: poording
--

SELECT pg_catalog.setval('public.user_preferences_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: poording
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: websites_id_seq; Type: SEQUENCE SET; Schema: public; Owner: poording
--

SELECT pg_catalog.setval('public.websites_id_seq', 1, false);


--
-- Name: workflow_steps_id_seq; Type: SEQUENCE SET; Schema: public; Owner: poording
--

SELECT pg_catalog.setval('public.workflow_steps_id_seq', 1, false);


--
-- Name: workflows_id_seq; Type: SEQUENCE SET; Schema: public; Owner: poording
--

SELECT pg_catalog.setval('public.workflows_id_seq', 1, false);


--
-- Name: actions actions_pkey; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_pkey PRIMARY KEY (id);


--
-- Name: selectors selectors_pkey; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.selectors
    ADD CONSTRAINT selectors_pkey PRIMARY KEY (id);


--
-- Name: user_preferences user_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: websites websites_pkey; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.websites
    ADD CONSTRAINT websites_pkey PRIMARY KEY (id);


--
-- Name: workflow_steps workflow_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_pkey PRIMARY KEY (id);


--
-- Name: workflows workflows_pkey; Type: CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.workflows
    ADD CONSTRAINT workflows_pkey PRIMARY KEY (id);


--
-- Name: idx_actions_selector_id; Type: INDEX; Schema: public; Owner: poording
--

CREATE INDEX idx_actions_selector_id ON public.actions USING btree (selector_id);


--
-- Name: idx_actions_website_id; Type: INDEX; Schema: public; Owner: poording
--

CREATE INDEX idx_actions_website_id ON public.actions USING btree (website_id);


--
-- Name: idx_selectors_website_id; Type: INDEX; Schema: public; Owner: poording
--

CREATE INDEX idx_selectors_website_id ON public.selectors USING btree (website_id);


--
-- Name: idx_user_preferences_user_website; Type: INDEX; Schema: public; Owner: poording
--

CREATE INDEX idx_user_preferences_user_website ON public.user_preferences USING btree (user_id, website_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: poording
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_username; Type: INDEX; Schema: public; Owner: poording
--

CREATE INDEX idx_users_username ON public.users USING btree (username);


--
-- Name: idx_websites_url; Type: INDEX; Schema: public; Owner: poording
--

CREATE INDEX idx_websites_url ON public.websites USING btree (url);


--
-- Name: idx_workflow_steps_workflow_order; Type: INDEX; Schema: public; Owner: poording
--

CREATE INDEX idx_workflow_steps_workflow_order ON public.workflow_steps USING btree (workflow_id, step_order);


--
-- Name: actions update_actions_updated_at; Type: TRIGGER; Schema: public; Owner: poording
--

CREATE TRIGGER update_actions_updated_at BEFORE UPDATE ON public.actions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: selectors update_selectors_updated_at; Type: TRIGGER; Schema: public; Owner: poording
--

CREATE TRIGGER update_selectors_updated_at BEFORE UPDATE ON public.selectors FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: user_preferences update_user_preferences_updated_at; Type: TRIGGER; Schema: public; Owner: poording
--

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON public.user_preferences FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: poording
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: websites update_websites_updated_at; Type: TRIGGER; Schema: public; Owner: poording
--

CREATE TRIGGER update_websites_updated_at BEFORE UPDATE ON public.websites FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: workflow_steps update_workflow_steps_updated_at; Type: TRIGGER; Schema: public; Owner: poording
--

CREATE TRIGGER update_workflow_steps_updated_at BEFORE UPDATE ON public.workflow_steps FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: workflows update_workflows_updated_at; Type: TRIGGER; Schema: public; Owner: poording
--

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON public.workflows FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: actions actions_selector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_selector_id_fkey FOREIGN KEY (selector_id) REFERENCES public.selectors(id);


--
-- Name: actions actions_website_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.actions
    ADD CONSTRAINT actions_website_id_fkey FOREIGN KEY (website_id) REFERENCES public.websites(id);


--
-- Name: selectors selectors_website_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.selectors
    ADD CONSTRAINT selectors_website_id_fkey FOREIGN KEY (website_id) REFERENCES public.websites(id);


--
-- Name: user_preferences user_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_preferences user_preferences_website_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_website_id_fkey FOREIGN KEY (website_id) REFERENCES public.websites(id);


--
-- Name: workflow_steps workflow_steps_action_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_action_id_fkey FOREIGN KEY (action_id) REFERENCES public.actions(id);


--
-- Name: workflow_steps workflow_steps_workflow_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.workflow_steps
    ADD CONSTRAINT workflow_steps_workflow_id_fkey FOREIGN KEY (workflow_id) REFERENCES public.workflows(id);


--
-- Name: workflows workflows_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.workflows
    ADD CONSTRAINT workflows_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: workflows workflows_website_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: poording
--

ALTER TABLE ONLY public.workflows
    ADD CONSTRAINT workflows_website_id_fkey FOREIGN KEY (website_id) REFERENCES public.websites(id);


--
-- PostgreSQL database dump complete
--

