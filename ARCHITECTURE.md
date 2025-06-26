# Architecture of Big Cases Bot 2

## CourtListener API

Big Cases Bot 2 uses [CourtListener's REST API][api] to receive news about new filings. It does this via [webhooks][wh]. When CourtListener learns about a new docket entry in a followed case, CourtListener will POST a webhook to BCB2 with information about the docket entry and documents associated with it.


## Database

BCB2 uses a [Postgres](https://www.postgresql.org/) database to keep track of cases and documents it knows about.


## Posting

BCB2 posts to Mastodon ([@big_cases@law.builders](https://law.builders/@bigcases)) and Bluesky ([@bigcases.bots.law](https://bsky.app/profile/bigcases.bots.law)).


## Interacting via social media

- For now, you can't @-mention the bots, but it's being tracked in issue [#28][mention].


### Developer Installation

To set up a development machine, do the following:

1. Clone the [bigcases2](https://github.com/freelawproject/bigcases2) repository.

1. Create a personal settings file. To do that, copy-paste the `.env.example` file to `.env.dev`.

1. Modify your new `.env.dev` file and uncomment the line `ALLOWED_HOSTS="*"`

1. Next, create the bridge network that docker relies on:

    `docker network create -d bridge --attachable bc2_net_overlay`

    This is important so that each service in the compose file can have a hostname.

1. `cd` into bigcases2/docker/bigcasesbot, then launch the server by running:

    `docker compose up -d --build`

1. Once that's done, it'll be up at http://localhost:8888 (note the port; it's different than normal)


## Command Line Interface

1. Generate some dummy data for your database:

        docker exec -it bc2-django python manage.py bootstrap-dev

1. Post something manually in the registered channels:

        docker exec -it bc2-django python manage.py post

## Server

### What does the server do?

- Receives webhooks from CourtListener and Mastodon
- Processes new documents from CourtListener (generate thumbnails, create posts, post)

## Incoming webhooks

- `/webhooks/docket-[secret]`: From CourtListener, delivered when there is a new document in a followed case. The full URL is secret.
- `/webhooks/mastodon`: From Mastodon instance, Web Push API

## Images

BCB2 generates images of the first few pages of a document by using [Doctor][dr].

## Key Dependencies

- [Django](https://www.djangoproject.com/)
- [Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/)
- [Doctor][dr]
- [rq][rq] (soon, see [#35][soon])

### External Packages

- Nginx: web proxy/server
- Docker (for [Doctor](https://github.com/freelawproject/doctor))


[wh]: https://www.courtlistener.com/help/api/webhooks/
[api]: https://www.courtlistener.com/help/api/rest/
[mention]: https://github.com/freelawproject/bigcases2/issues/28
[dr]: https://free.law/projects/doctor
[rq]: https://python-rq.org/
[soon]: https://github.com/freelawproject/bigcases2/issues/35
