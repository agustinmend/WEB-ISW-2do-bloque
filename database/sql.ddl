CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE content.conference (
    id UUID PRIMARY KEY,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,

    location VARCHAR(255),

    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE content.track (
    id UUID PRIMARY KEY,

    conference_id UUID NOT NULL,

    name VARCHAR(255) NOT NULL,
    description TEXT,

    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_track_conference
        FOREIGN KEY (conference_id)
        REFERENCES content.conference(id)
        ON DELETE CASCADE
);

CREATE TABLE content.session (
    id UUID PRIMARY KEY,

    track_id UUID NOT NULL,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,

    capacity INTEGER NOT NULL,
    room VARCHAR(255),

    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_session_track
        FOREIGN KEY (track_id)
        REFERENCES content.track(id)
        ON DELETE CASCADE
);

CREATE TABLE content.registration (
    id UUID PRIMARY KEY,

    session_id UUID NOT NULL,

    user_email VARCHAR(255) NOT NULL,
    user_name VARCHAR(255) NOT NULL,

    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_registration_session
        FOREIGN KEY (session_id)
        REFERENCES content.session(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_registration_email
        UNIQUE(session_id, user_email)
);

CREATE TABLE content.speaker (
    id UUID PRIMARY KEY,

    name VARCHAR(255) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE content.session_speaker (
    session_id UUID NOT NULL,
    speaker_id UUID NOT NULL,

    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_session_speaker_session
        FOREIGN KEY (session_id)
        REFERENCES content.session(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_session_speaker_speaker
        FOREIGN KEY (speaker_id)
        REFERENCES content.speaker(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_session_speaker
        UNIQUE(session_id, speaker_id)
);

CREATE INDEX idx_track_conference
ON content.track(conference_id);

CREATE INDEX idx_session_track
ON content.conference_session(track_id);

CREATE INDEX idx_registration_session
ON content.registration(session_id);

CREATE INDEX idx_session_speaker_session
ON content.session_speaker(session_id);

CREATE INDEX idx_session_speaker_speaker
ON content.session_speaker(speaker_id);