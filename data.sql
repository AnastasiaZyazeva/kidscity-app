--
-- PostgreSQL database dump
--

\restrict lVDGc4P6r0ifnZakcwmCPefmX7YaeIAtzWvRQAoPIlW7a5JXKIOnz8SaQOifDNW

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

--
-- Data for Name: parents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.parents (id_parent, last_name, first_name, middle_name, phone, login, password) FROM stdin;
1	Титова	Виктория	Сергеевна	+79229653251	вика	вика
3	Бахчеван	Надежда	Андреевна	+79229653251	надя	надя
9	Зязева	Любовь	Анатольевна	+79229331552	любовь	любовь
8	Петюк	Анна	Вячеславовна	+79999874562	анна	анна
4	Леонов	Денис	Алексеевич	+79660609949	денс	денс
11	Гракила	Аделина	Григорьевна	+7903144630	deli	123
12	Бузова	Ольга	Игоревна	+79036615789	buzova1986	olecka123
2	Зязева	Анастасия	Сергеевна	+79229653251	анастасия	111
10	Рыбальченко	Кристина	Андреевна	+79081862641	KrblsaRim	Krblsaaa$0066
13	Зязев	Сергей	Иванович	6757579	сергей1	сергей
14	Куертова	Анастасия	Сергеевна	89229653251	Анастасия	123
15	Куертов	Влад	Дмитриевич	89091313213	влад	1313
\.


--
-- Data for Name: children; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.children (id_child, name, age, id_parent) FROM stdin;
1	надя	6	1
2	аня	3	1
4	надежда	6	1
5	аня	5	3
6	настя	7	3
7	вика	4	3
8	Влада	5	4
9	настя	7	1
10	леша	7	1
11	соня	6	2
12	карина	6	2
17	слава	7	8
20	аня	6	2
21	денис	8	2
24	матвей	8	9
23	настя	10	9
25	карина	9	9
22	влада	6	4
3	тема	6	1
26	Тема	11	10
27	маша	12	11
28	Дмитрий	8	12
19	надя	5	2
29	кристина	5	2
30	антон	3	2
31	настя	5	13
32	Маргарита	4	14
33	Маргарита	4	15
34	настя	18	14
35	глеб	3	14
\.


--
-- Data for Name: preferences; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.preferences (id_preference, id_location, age_preference) FROM stdin;
7	\N	3+
8	\N	4+
9	\N	5+
10	\N	6+
11	\N	7+
12	\N	8+
29	189	3+
30	190	3+
31	191	3+
32	192	4+
33	193	4+
34	194	4+
35	195	5+
36	196	5+
37	197	5+
38	198	6+
39	199	6+
40	200	7+
41	201	7+
42	202	8+
43	203	8+
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.locations (id_location, name_location, age_range, description, cost, image, id_preference) FROM stdin;
207	Ветеринарная клиника	3+	В данной локации дети смогут узнать как правильно ухаживать за животными, как спасти их от опасных насекомых и что необходимо разместить в клетке для грызунов и птиц.	650.00	images/locations/1781453061392_ветеринар.jpg	\N
213	Работа ру	6+	Локация, куда приходят на тренинги, чтобы стать самыми ценными работниками. Всё начинается с теста, благодаря которому понятно, какая профессия больше всего подходит ребёнку. Именно поэтому Работа.ру – это первое место в городе, откуда начинается маршрут.	780.00	images/locations/1781453449989_работа ру.jpeg	\N
209	Инкассация	7+	Профессия инкассатора! Готовьтесь выносить деньги из магазина и банкомата, но, в отличие от ограблений, абсолютно законно. В очках и специальных жилетах, постоянно оглядываясь и следя за безопасностью, как шпионы.	750.00	images/locations/1781453218762_инкас.jpeg	\N
214	Стадион Спартак	3+	В данной локации дети смогут почувствовать себя настоящими футболистами, посетить тренировку и даже принять участие в футбольном матче. А для самых маленьких гостей нашего города на стадионе «Спартак» проводятся весёлые старты.	650.00	images/locations/1781453544296_спартак.jpg	\N
215	Салон красоты	4+	В данной локации дети могут узнать об уходе за собой. Здесь они смогут научиться делать стильные причёски и даже сделать себе маникюр безопасным лаком.	670.00	images/locations/1781453595271_салон красоты.jpeg	\N
216	Русское радио	7+	В данной локации дети смогут почувствовать себя настоящими радиоведущими и выйти в прямой эфир для участия в познавательной викторине, чтобы заработать как можно больше лайков.	850.00	images/locations/1781453647234_радио.jpeg	\N
217	hveguigb	6+	gfiydfydy	0.00	images/locations/1781689671249_блогер.jpeg	\N
205	Пещера	3+	Кто и зачем разрисовал стены пещеры? Ответ на этот вопрос дети получат в пещере нашего города. Они узнают много интересного о наскальной живописи, способах её нанесения, познакомятся с профессией археолога и некоторыми фактами из жизни древних людей, а после теории отправляются на поиски различных экспонатов.	560.00	images/locations/1781452624502_Image_1280x853_1.jpg	\N
212	Киностудия ОККО	5+	Опытный ведущий создает настоящую атмосферу телевизионного шоу, а все дети активно участвуют в съемочном процессе. Темы обсуждения постоянно меняются, чтобы ребенок мог выбрать то, что ему интересно.	750.00	images/locations/1781453400190_окко.jpeg	\N
206	Школа блогеров	8+	В этой локации ребята узнают: какие бывают блогеры, как придумать идею для видео и набрать свою первую тысячу лайков. И даже успеют снять первый выпуск своего блога!	800.00	images/locations/1781452993237_блогер.jpeg	\N
\.


--
-- Data for Name: tickets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tickets (id_ticket, id_parent, id_child, id_location, data) FROM stdin;
59	14	32	214	2026-06-15
60	14	34	213	2026-06-16
61	14	35	213	2026-06-16
62	14	34	207	2026-06-14
\.


--
-- Name: children_id_child_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.children_id_child_seq', 35, true);


--
-- Name: locations_id_location_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.locations_id_location_seq', 217, true);


--
-- Name: parents_id_parent_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.parents_id_parent_seq', 15, true);


--
-- Name: preferences_id_preference_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.preferences_id_preference_seq', 43, true);


--
-- Name: tickets_id_ticket_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tickets_id_ticket_seq', 62, true);


--
-- PostgreSQL database dump complete
--

\unrestrict lVDGc4P6r0ifnZakcwmCPefmX7YaeIAtzWvRQAoPIlW7a5JXKIOnz8SaQOifDNW

