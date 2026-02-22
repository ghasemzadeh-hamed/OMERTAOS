CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL
);

CREATE TABLE tools (
  id SERIAL PRIMARY KEY,
  name TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  category_id INT REFERENCES categories(id),
  pypi_name TEXT,
  repo_url TEXT,
  docs_url TEXT,
  description TEXT,
  latest_version TEXT,
  license TEXT,
  stars INT DEFAULT 0,
  tags TEXT[] DEFAULT '{}',
  config_schema JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tool_versions (
  id SERIAL PRIMARY KEY,
  tool_id INT REFERENCES tools(id) ON DELETE CASCADE,
  version TEXT NOT NULL,
  released_at TIMESTAMPTZ,
  yanked BOOLEAN DEFAULT FALSE,
  meta JSONB
);

CREATE TABLE installations (
  id SERIAL PRIMARY KEY,
  tool_id INT REFERENCES tools(id) ON DELETE CASCADE,
  env TEXT NOT NULL,
  status TEXT NOT NULL,
  version TEXT,
  editable BOOLEAN DEFAULT FALSE,
  last_log TEXT,
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(tool_id, env)
);

CREATE TABLE jobs (
  id SERIAL PRIMARY KEY,
  kind TEXT,
  payload JSONB,
  status TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ
);
