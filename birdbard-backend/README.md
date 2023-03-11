# auto-sensemaker
Twitter auto sense-maker with LLMs

> Picture this:

> Automatic clustering of "topics you're on about on twitter", with one ongoing summary for each topic, that gets updated based on loose tweets and replies. A sort of rolling compiler of your oeuvre, 100% emergent from your twitter activity

> It can also find holes in your reasoning, or parts of it that need detailing and expanding

> Or the topics people engage with the most! And new topics or ways of presenting them that will engage more people!

> Compile a knowledge garden from your chaotic web activity! A labor-free showcase of your personality and interests and aesthetic sensibilities!

> Tweets -> embeddings -> clustering -> hierarchical summaries -> entity detection -> semantic links -> knowledge graph -> inference of missing links and expansion vectors

Based on this twitter [thread](https://twitter.com/exGenesis/status/1625829266624593920)


Features

- clustering and topic modeling tweets
- completing twitter archive by looking up tweets and users from the api
- storing the archive in a postgres db

Requirements:
- python and its requirements
- postgresql:
  - [install postgres on mac](https://gist.github.com/ibraheem4/ce5ccd3e4d7a65589ce84f2a3b7c23a3)
  - To start postgresql@14 now and restart at login: `brew services start postgresql@14`
  - To stop brew services stop postgresql@14
  - list dbs: `psql -U <user> -l`
  - `createdb <database_name>`
  - `dropdb <database_name>`
- surrealdb: 
  - brew install surrealdb/tap/surreal
- We're using poetry to manage build and dependencies.
  - `poetry config virtualenvs.in-project true`
  - `poetry shell` to enter the virtual environment
  - or `source $(poetry env info --path)/bin/activate`