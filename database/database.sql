DROP TABLE IF EXISTS public.ballcoordinates;

CREATE TABLE ballcoordinates (
	id bigserial NOT NULL,
	x float NOT NULL,
	y float NOT NULL,
	angle float NULL,
    magnitude float NULL,
	PRIMARY KEY (id)
);
