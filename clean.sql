
TRUNCATE global_attributes;
TRUNCATE parameters;
TRUNCATE file CASCADE;
SELECT setval('file_id_sequence', 10000);
