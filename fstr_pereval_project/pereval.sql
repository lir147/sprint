-- -------------------------------------------------------------
-- Database: pereval (Updated with status field)
-- Generation Time: 2022-02-22 14:19:15.6730
-- -------------------------------------------------------------

-- Sequences
CREATE SEQUENCE IF NOT EXISTS pereval_id_seq;
CREATE SEQUENCE IF NOT EXISTS pereval_areas_id_seq;
CREATE SEQUENCE IF NOT EXISTS pereval_added_id_seq;
CREATE SEQUENCE IF NOT EXISTS untitled_table_200_id_seq;


CREATE TABLE IF NOT EXISTS "public"."pereval_added" (
    "id" int4 NOT NULL DEFAULT nextval('pereval_id_seq'::regclass),
    "date_added" timestamp DEFAULT now(),
    "raw_data" json,
    "images" json,
    "status" varchar(50) DEFAULT 'new' CHECK ("status" IN ('new', 'pending', 'accepted', 'rejected')),
    PRIMARY KEY ("id")
);


CREATE TABLE IF NOT EXISTS "public"."pereval_areas" (
    "id" int8 NOT NULL DEFAULT nextval('pereval_areas_id_seq'::regclass),
    "id_parent" int8 NOT NULL,
    "title" text,
    PRIMARY KEY ("id")
);


CREATE TABLE IF NOT EXISTS "public"."pereval_images" (
    "id" int4 NOT NULL DEFAULT nextval('pereval_added_id_seq'::regclass),
    "date_added" timestamp DEFAULT now(),
    "img" bytea NOT NULL,
    PRIMARY KEY ("id")
);


CREATE TABLE IF NOT EXISTS "public"."spr_activities_types" (
    "id" int4 NOT NULL DEFAULT nextval('untitled_table_200_id_seq'::regclass),
    "title" text,
    PRIMARY KEY ("id")
);


INSERT INTO "public"."pereval_added" ("id", "date_added", "raw_data", "images", "status")
VALUES (1, '2022-02-21 14:14:00.720184',
    '{"beautyTitle": "пер. ", "title": "Пхия", "other_titles": "Триев", "connect": "", "add_time": "2021-09-22 13:18:13",
     "user": {"email": "user@email.tld", "phone": "79031234567", "fam": "Пупкин", "name": "Василий", "otc": "Иванович"},
     "coords": {"latitude": "45.3842", "longitude": "7.1525", "height": "1200"},
     "level": {"winter": "", "summer": "1А", "autumn": "1А", "spring": ""}}',
    '{"images": [{"id": 1, "title":"Седловина"}, {"id": 2, "title":"Подъём"}]}',
    'new'
) ON CONFLICT ("id") DO NOTHING;

INSERT INTO "public"."pereval_areas" ("id", "id_parent", "title") VALUES
(0, 0, 'Планета Земля'),
(1, 0, 'Памиро-Алай'),
(65, 0, 'Алтай'),
(66, 65, 'Северо-Чуйский хребет'),
(88, 65, 'Южно-Чуйский хребет'),
(92, 65, 'Катунский хребет'),
(105, 1, 'Фанские горы'),
(106, 1, 'Гиссарский хребет (участок западнее перевала Анзоб)'),
(131, 1, 'Матчинский горный узел'),
(133, 1, 'Горный узел Такали, Туркестанский хребет'),
(137, 1, 'Высокий Алай'),
(147, 1, 'Кичик-Алай и Восточный Алай'),
(367, 375, 'Аладаглар'),
(375, 0, 'Тавр'),
(384, 0, 'Саяны'),
(386, 65, 'Хребет Листвяга'),
(387, 65, 'Ивановский хребет'),
(388, 65, 'Массив Мунгун-Тайга'),
(389, 65, 'Хребет Цаган-Шибэту'),
(390, 65, 'Хребет Чихачева (Сайлюгем)'),
(391, 65, 'Шапшальский хребет'),
(392, 65, 'Хребет Южный Алтай'),
(393, 65, 'Хребет Монгольский Алтай'),
(398, 384, 'Западный Саян'),
(399, 384, 'Восточный Саян'),
(402, 384, 'Кузнецкий Алатау'),
(459, 65, 'Курайский хребет');


INSERT INTO "public"."spr_activities_types" ("id", "title") VALUES
(1, 'пешком'), (2, 'лыжи'), (3, 'катамаран'), (4, 'байдарка'), (5, 'плот'), (6, 'сплав'),
(7, 'велосипед'), (8, 'автомобиль'), (9, 'мотоцикл'), (10, 'парус'), (11, 'верхом');