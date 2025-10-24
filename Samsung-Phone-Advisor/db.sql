--
-- PostgreSQL database dump
--

\restrict s7o5vl5DeFdIH7NFHRpTVd6YUWwEyJwLhwXTaeLyQ60aeddqUb3Gnon3ZcdqmgT

-- Dumped from database version 16.10
-- Dumped by pg_dump version 16.10

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: mobile_specs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mobile_specs (
    name text,
    link text,
    released text,
    display text,
    battery text,
    camera text,
    price text,
    ram text,
    storage text
);


ALTER TABLE public.mobile_specs OWNER TO postgres;

--
-- Data for Name: mobile_specs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mobile_specs (name, link, released, display, battery, camera, price, ram, storage) FROM stdin;
SamsungGalaxy A56	https://www.gsmarena.com/samsung_galaxy_a56-13603.php	Available. Released 2025, March 10	6.7 inches, 110.2 cm	5000 mAh	50 MP, f/1.8, (wide), 1/1.56", 1.0µm, PDAF, OIS	$ 305.00 / € 290.00 / £ 252.00 / ₹ 32,724	6GB, 8GB, 12GB	128GB, 256GB
SamsungGalaxy S25 Ultra	https://www.gsmarena.com/samsung_galaxy_s25_ultra-13322.php	Available. Released 2025, February 03	6.9 inches, 116.9 cm	Li-Ion 5000 mAh	200 MP, f/1.7, 24mm (wide), 1/1.3", 0.6µm, multi-directional PDAF, OIS	$ 689.94 / € 920.00 / £ 770.00 / ₹ 97,500	12GB, 16GB	256GB, 512GB
SamsungGalaxy A17	https://www.gsmarena.com/samsung_galaxy_a17_5g-14041.php	Available. Released 2025, August 14	6.7 inches, 110.2 cm	5000 mAh	50 MP, f/1.8, (wide), 1/2.76", 0.64µm, AF, OIS	$ 205.00 / € 168.00 / £ 182.00 / ₹ 18,999	4GB, 6GB, 8GB	128GB, 256GB
SamsungGalaxy S25	https://www.gsmarena.com/samsung_galaxy_s25-13610.php	Available. Released 2025, February 03	6.2 inches, 94.4 cm	Li-Ion 4000 mAh	50 MP, f/1.8, 24mm (wide), 1/1.56", 1.0µm, dual pixel PDAF, OIS	$ 457.00 / € 519.00 / £ 479.99 / ₹ 61,350	12GB	128GB, 256GB, 512GB
SamsungGalaxy A36	https://www.gsmarena.com/samsung_galaxy_a36-13497.php	Available. Released 2025, March 10	6.7 inches, 110.2 cm	5000 mAh	50 MP, f/1.8, (wide), 1/1.96", PDAF, OIS	$ 248.00 / € 242.99 / £ 215.00 / ₹ 28,499	6GB, 8GB, 12GB	128GB, 256GB
SamsungGalaxy S25 FE	https://www.gsmarena.com/samsung_galaxy_s25_fe_5g-14042.php	Available. Released 2025, September 04	6.7 inches, 110.2 cm	4900 mAh	50 MP, f/1.8, 24mm (wide), 1/1.57", 1.0µm, dual pixel PDAF, OIS	$ 623.99 / € 578.00 / £ 599.00 / ₹ 65,999	8GB	128GB, 256GB, 512GB
SamsungGalaxy A07 4G	https://www.gsmarena.com/samsung_galaxy_a07-14066.php	Available. Released 2025, August 25	6.7 inches, 108.4 cm	5000 mAh	50 MP, f/1.8, (wide), 1/2.76", 0.64µm, PDAF	$ 143.64	4GB, 6GB, 8GB	64GB, 128GB, 256GB
SamsungGalaxy S24 Ultra	https://www.gsmarena.com/samsung_galaxy_s24_ultra-12771.php	Available. Released 2024, January 24	6.8 inches, 113.5 cm	Li-Ion 5000 mAh	200 MP, f/1.7, 24mm (wide), 1/1.3", 0.6µm, multi-directional PDAF, OIS	$ 574.90 / € 705.34 / £ 579.95 / ₹ 79,999	12GB	256GB, 512GB
SamsungGalaxy S24	https://www.gsmarena.com/samsung_galaxy_s24-12773.php	Available. Released 2024, January 24	6.2 inches, 94.4 cm	Li-Ion 4000 mAh	50 MP, f/1.8, 24mm (wide), 1/1.56", 1.0µm, dual pixel PDAF, OIS	$ 289.95 / € 430.00 / £ 368.00 / ₹ 41,560	8GB, 12GB	128GB, 256GB, 512GB
SamsungGalaxy S24 FE	https://www.gsmarena.com/samsung_galaxy_s24_fe-13262.php	Available. Released 2024, October 03	6.7 inches, 110.2 cm	4700 mAh	50 MP, f/1.8, 24mm (wide), 1/1.57", 1.0µm, dual pixel PDAF, OIS	$ 250.00 / € 391.90 / £ 364.00 / ₹ 30,999	8GB	128GB, 256GB, 512GB
SamsungGalaxy A55	https://www.gsmarena.com/samsung_galaxy_a55-12824.php	Available. Released 2024, March 15	6.6 inches, 106.9 cm	Li-Ion 5000 mAh	50 MP, f/1.8, (wide), 1/1.56", 1.0µm, PDAF, OIS	$ 382.50 / € 310.00 / £ 240.00 / ₹ 20,399	6GB, 8GB, 12GB	128GB, 256GB
SamsungGalaxy A26	https://www.gsmarena.com/samsung_galaxy_a26-13679.php	Available. Released 2025, March 19	6.7 inches, 110.2 cm	5000 mAh	50 MP, f/1.8, 27mm (wide), 1/2.76", 0.64µm, PDAF, OIS	$ 180.49 / € 198.69 / £ 167.51 / ₹ 23,999	4GB, 6GB, 8GB	128GB, 256GB
SamsungGalaxy A16 5G	https://www.gsmarena.com/samsung_galaxy_a16_5g-13346.php	Available. Released 2024, October 25	6.7 inches, 110.2 cm	5000 mAh	50 MP, f/1.8, (wide), 1/2.76", 0.64µm, AF	$ 129.99 / € 159.00 / £ 129.50 / ₹ 18,999	4GB, 6GB, 8GB	128GB, 256GB
SamsungGalaxy S22 Ultra 5G	https://www.gsmarena.com/samsung_galaxy_s22_ultra_5g-11251.php	Available. Released 2022, February 25	6.8 inches, 114.7 cm	Li-Ion 5000 mAh	108 MP, f/1.8, 23mm (wide), 1/1.33", 0.8µm, PDAF, OIS	$ 273.27 / € 424.50 / £ 303.40 / ₹ 65,999	8GB, 12GB	128GB, 256GB, 512GB
SamsungGalaxy A16	https://www.gsmarena.com/samsung_galaxy_a16-13383.php	Available. Released 2024, November 20	6.7 inches, 110.2 cm	5000 mAh	50 MP, f/1.8, (wide), 1/2.76", 0.64µm, AF	$ 123.75 / € 122.00 / £ 99.49	4GB, 6GB, 8GB	128GB, 256GB
SamsungGalaxy A06	https://www.gsmarena.com/samsung_galaxy_a06-13265.php	Available. Released 2024, August 22	6.7 inches, 108.4 cm	Li-Po 5000 mAh	50 MP, f/1.8, (wide), 1/2.76", 0.64µm, PDAF	$ 102.00 / € 85.12 / £ 67.00 / ₹ 7,599	4GB, 6GB	64GB, 128GB
SamsungGalaxy S23 Ultra	https://www.gsmarena.com/samsung_galaxy_s23_ultra-12024.php	Available. Released 2023, February 17	6.8 inches, 114.7 cm	Li-Ion 5000 mAh	200 MP, f/1.7, 24mm (wide), 1/1.3", 0.6µm, multi-directional PDAF, OIS	$ 470.00 / € 442.57 / £ 439.00 / ₹ 78,399	8GB, 12GB	256GB, 512GB
SamsungGalaxy A35	https://www.gsmarena.com/samsung_galaxy_a35-12705.php	Available. Released 2024, March 15	6.6 inches, 106.9 cm	Li-Ion 5000 mAh	50 MP, f/1.8, (wide), 1/1.96", PDAF, OIS	$ 119.00 / € 199.99 / £ 214.99 / ₹ 17,999	4GB, 6GB, 8GB, 12GB	128GB, 256GB
SamsungGalaxy S23	https://www.gsmarena.com/samsung_galaxy_s23-12082.php	Available. Released 2023, February 17	6.1 inches, 90.1 cm	Li-Ion 3900 mAh	50 MP, f/1.8, 24mm (wide), 1/1.56", 1.0µm, dual pixel PDAF, OIS	$ 229.85 / € 330.00 / £ 253.25 / ₹ 46,990	8GB	128GB, 256GB, 512GB
SamsungGalaxy S22 5G	https://www.gsmarena.com/samsung_galaxy_s22_5g-11253.php	Available. Released 2022, February 25	6.1 inches, 90.1 cm	Li-Ion 3700 mAh	50 MP, f/1.8, 23mm (wide), 1/1.56", 1.0µm, dual pixel PDAF, OIS	$ 163.04 / € 234.66 / £ 184.00	8GB	128GB, 256GB
SamsungGalaxy S25 Edge	https://www.gsmarena.com/samsung_galaxy_s25_edge-13506.php	Available. Released 2025, May 29	6.7 inches, 110.2 cm	Li-Ion 3900 mAh	200 MP, f/1.7, 24mm (wide), 1/1.3", 0.6µm, multi-directional PDAF, OIS	$ 539.94 / € 665.00 / £ 699.99 / ₹ 101,999	12GB	256GB, 512GB
SamsungGalaxy Z Fold7	https://www.gsmarena.com/samsung_galaxy_z_fold7-13826.php	Available. Released 2025, July 25	8.0 inches, 204.2 cm	Li-Po 4400 mAh	200 MP, f/1.7, 24mm (wide), 1/1.3", 0.6µm, multi-directional PDAF, OIS	$ 1,599.99 / € 1,275.00 / £ 1,575.66 / ₹ 174,999	12GB, 16GB	256GB, 512GB
SamsungGalaxy A15	https://www.gsmarena.com/samsung_galaxy_a15-12637.php	Available. Released 2023, December 16	6.5 inches, 103.7 cm	5000 mAh	50 MP, f/1.8, 26mm (wide), 1/2.8", 0.64µm, PDAF	$ 169.99 / € 174.99 / £ 101.02	4GB, 6GB, 8GB	128GB, 256GB
SamsungGalaxy S21 5G	https://www.gsmarena.com/samsung_galaxy_s21_5g-10626.php	Available. Released 2021, January 29	6.2 inches, 94.1 cm	Li-Ion 4000 mAh	12 MP, f/1.8, 26mm (wide), 1/1.76", 1.8µm, dual pixel PDAF, OIS	$ 149.77 / € 198.99 / £ 153.50	6GB, 8GB	128GB, 256GB
SamsungGalaxy S21 Ultra 5G	https://www.gsmarena.com/samsung_galaxy_s21_ultra_5g-10596.php	Available. Released 2021, January 29	6.8 inches, 112.1 cm	Li-Ion 5000 mAh	108 MP, f/1.8, 24mm (wide), 1/1.33", 0.8µm, PDAF, OIS	$ 249.00 / € 267.99 / £ 205.29	8GB, 12GB, 16GB	128GB, 256GB, 512GB
SamsungGalaxy A54	https://www.gsmarena.com/samsung_galaxy_a54-12070.php	Available. Released 2023, March 24	6.4 inches, 100.5 cm	5000 mAh	50 MP, f/1.8, 23mm (wide), 1/1.56", 1.0µm, PDAF, OIS	$ 119.11 / € 213.00 / £ 174.99 / ₹ 28,999	4GB, 6GB, 8GB	128GB, 256GB
SamsungGalaxy M17	https://www.gsmarena.com/samsung_galaxy_m17_5g-14221.php	Available. Released Exp. release 2025, October 13	6.7 inches, 110.2 cm	5000 mAh	50 MP, f/1.8, (wide), 1/2.76", 0.64µm, AF, OIS	N/A	4GB, 6GB, 8GB	128GB
SamsungGalaxy S25+	https://www.gsmarena.com/samsung_galaxy_s25+-13609.php	Available. Released 2025, February 03	6.7 inches, 110.2 cm	Li-Ion 4900 mAh	50 MP, f/1.8, 24mm (wide), 1/1.56", 1.0µm, dual pixel PDAF, OIS	$ 899.99 / € 815.00 / £ 803.00	12GB	256GB, 512GB
SamsungGalaxy S21 FE 5G	https://www.gsmarena.com/samsung_galaxy_s21_fe_5g-10954.php	Available. Released 2022, January 07	6.4 inches, 100.5 cm	Li-Ion 4500 mAh	12 MP, f/1.8, 26mm (wide), 1/1.76", 1.8µm, dual pixel PDAF, OIS	$ 136.77 / € 256.00 / £ 189.00	6GB, 8GB	128GB, 256GB
SamsungGalaxy A05	https://www.gsmarena.com/samsung_galaxy_a05-12583.php	Available. Released 2023, October 15	6.7 inches, 108.4 cm	Li-Po 5000 mAh	50 MP, f/1.8, (wide),  1/2.8", 0.64µm, AF	$ 84.99 / € 96.07 / £ 69.70 / ₹ 8,949	3GB, 4GB, 6GB	32GB, 64GB, 128GB
\.


--
-- PostgreSQL database dump complete
--

\unrestrict s7o5vl5DeFdIH7NFHRpTVd6YUWwEyJwLhwXTaeLyQ60aeddqUb3Gnon3ZcdqmgT

