# Big Cases Bot 2

Big Cases Bot 2 is the sequel to Brad Heath's excellent Big Cases Bot
for Twitter.

The goals of Big Cases Bot 2 are:

- First and foremost, to bring the bot back!
- Expand the bot to Mastodon

Further development is intended, and all contributors, corrections and additions are welcome.

## Background

Free Law Project built this ...  This project represents ...  
We believe to be the ....

## What does it need to do?

- Store cases, documents, and posting criteria in a database (SQLite)
- Process incoming new-document webhooks from CourtListener (`/webhooks/cl`)
  - Look up case
  - Save to DB
  - Decide if it's worth posting
  - Construct a message
  - Construct any media attachments
  - Post
    - To Mastodon
    - To Twitter
- Process incoming messages from Mastodon or Twitter
  - Mastodon: check notifications ([Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/#reading-data-notifications) or [ananas](https://github.com/chr-1x/ananas#decorators))
  - Twitter: check notifications/stream
  - Is the user authorized to instruct the bot?
  - Parse message
    - Read up-thread if necessary to find what case is being discussed
  - Respond
    - Follow a case
      - POST to CL API?
      - Send reply message confirming case followed
    - Send a RECAP docket link (construct from case ID)
    - Send a RECAP document link
  - Check dockets for updates
    - Original bot did this via polling court RSS feeds
    - Decide if a new entry looks like it's worth downloading
    - If yes, download the new document. (Webhook will fire at that point, so this is as far as the bot's checking needs to go.)

## Dependencies

- Flask
- Free Law Project's [`courts-db`](https://github.com/freelawproject/courts-db)

## Quickstart

You can feed in a X as ... .. ...

```
IMPORTS

CALL EXAMPLE

returns:
  ""EXAMPLE OUTPUT
```



## Some Notes ...
Somethings to keep in mind as ....

1. ...
2. ...


## Fields

1. `id` ==> string; Courtlistener Court Identifier
2. `court_url` ==> string; url for court website
3. `regex` ==>  array; regexes patterns to find courts


## Installation

Installing Big Cases Bot 2 is easy.

```sh
pip install bigcases2
```


Or install the latest dev version from GitHub

```sh
pip install git+https://github.com/freelawproject/bigcases2.git@master
```

## Future

1) Continue to improve ...
2) Future updates

## Deployment

If you wish to create a new version manually, the process is:

1. Update version info in `setup.py`

2. Install the requirements using `poetry install`

3. Set up a config file at `~/.pypirc`

4. Generate a universal distribution that works in py2 and py3 (see setup.cfg)

```sh
python setup.py sdist bdist_wheel
```

5. Upload the distributions

```sh
twine upload dist/* -r pypi (or pypitest)
```

## License

This repository is available under the permissive BSD license, making it easy and safe to incorporate in your own libraries.

Pull and feature requests welcome. Online editing in GitHub is possible (and easy!)
