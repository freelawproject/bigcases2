# Architecture of Big Cases Bot 2

## CourtListener API

Big Cases Bot 2 uses [CourtListener's REST API](https://www.courtlistener.com/api/rest-info/) to receive news about new filings. It does this via [webhooks](https://www.courtlistener.com/profile/webhooks/), which are a new feature of the API. When CourtListener learns about a new docket entry in a followed case, CourtListener will POST a webhook to BCB2 with information about the docket entry and documents associated with it.

## Database

BCB2 uses a [Postgres](https://www.postgresql.org/) database to keep track of cases and documents it knows about. The original BCB1 used MySQL.

## Posting

BCB2 posts to both Twitter ([@big_cases](https://twitter.com/big_cases)) and Mastodon ([@big_cases@law.builders](https://law.builders/@big_cases)).

## Interacting via social media

- `hey @big_cases, follow nysd 22-cv-12345`

### Developer Installation

To set up a development machine, do the following:

1. Clone the [bigcases2](https://github.com/freelawproject/bigcases2) repository.

1. Create a personal settings file. To do that, copy-paste the `.env.example` file to `.env.dev`.

1. Next, create the bridge network that docker relies on:

    `docker network create -d bridge --attachable bc2_net_overlay`

    This is important so that each service in the compose file can have a hostname.

1. `cd` into bigcases2/docker/bigcasesbot, then launch the server by running:

    `docker-compose up -d`

## Command Line Interface

1. Generate some dummy data for your database:

        docker exec -it bc2-django python manage.py bootstrap-dev

1. Lookup specific data from CourtListener:

        docker exec -it bc2-django python manage.py lookup 64983976

    This will use CL API to lookup the Docket `64983976`and output its data in the console. This command also accepts the following command line options:

      - `--add`: saves the case in the database
      - `--subscribe`: creates a CourtListener docket alert subscription

1. Post something manually in the registered channels:

        docker exec -it bc2-django python manage.py post

1. Create mastodon subscription to push notifications:

        docker exec -it bc2-django python manage.py mastodon-subscribe

    This command requires that the following variables are set in the .env file: `MASTODON_SHARED_KEY`, `MASTODON_PUBLIC_KEY`, `MASTODON_PRIVATE_KEY`and `PROJECT_BASE_URL`. We added a script to generate the first three variables. Execute the following command to use the script and paste the result in your .env file:

        docker exec -it bc2-django python /opt/bigcases2/scripts/get_mastodon_keys.py

    Make sure that the `MASTODON_TOKEN` and `MASTODON_SERVER` are set before using the previous command.

1. Delete mastodon subscription to push notifications:

        docker exec -it bc2-django python manage.py mastodon-unsubscribe

## Server

### What does the server do?

- Receives webhooks from CourtListener, Twitter, and Mastodon
- Processes new documents from CourtListener (generate thumbnails, create posts, post)

## Incoming webhooks

- `/webhooks/docket-[secret]`: From CourtListner, delievered when there is a new document in a followed case. The full URL is secret.
- `/webhooks/twitter`: From Twitter, Account Activity API
- `/webhooks/mastodon`: From Mastodon instance, Web Push API

## Images

BCB2 generates images of the first few pages of a document.

## Pending Questions

- [x] How do we receive messages from Mastodon?
  - [Web Push API](https://docs.joinmastodon.org/methods/push/)
    - Set `data[alerts][mention]` to `true`
    - [In Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/#push-subscriptions)
- [ ] How do we receive messages from Twitter?
  - [Webhooks via Account Activity API](https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/guides/getting-started-with-webhooks) (application pending)
- [ ] Is an admin page needed? (Will require further locking down the server (nginx).)
- [ ] How does BCB1 generate images?
- [x] How does CL generate thumbnail images? (e.g., [this one](https://storage.courtlistener.com/recap-thumbnails/gov.uscourts.cand.297616/2176640.thumb.1068.jpeg))
  - [Doctor](https://github.com/freelawproject/doctor) microservice, [`/convert/pdf/thumbnails/`](https://github.com/freelawproject/doctor#endpoint-convertpdfthumbnails) endpoint
- [ ] Are Celery tasks needed?
  - Image generation: Probably
- [ ] How do we pick up or get a callback when the thumbnails are done?
- [ ] What data do we need to track in the database?
  - Cases
    - Belong to one or more Beats
  - Docket entries
    - Rationale: to see whether they're new to BCB or not
    - Counter: If the webhook fires, that means it's new!
  - Documents
    - Rationale: Keep some metadata so we can post to multiple channels easily, keep track of thumbnails, etc.
  - Document page thumbnails
    - Rationale: Reuse for posting to multiple channels
  - Beats
    - May publish its own subject area [Little Cases Bot](https://github.com/freelawproject/bigcases2/issues/8)
  - Users
    - May be assigned to curate one or more Beats
    - Get command privileges
    - Optionally crawl with their own PACER credentials
    - May associate a [DocumentCloud account](https://github.com/freelawproject/bigcases2/issues/15) to collect documents from their Beats
    - Accounts for allow-listing
  - Channels
    - Service (Twitter, Mastodon)
    - Account (e.g., @big_cases, @bigcases@law.builders)

## Key Dependencies

### Python Packages

- [Django](https://www.djangoproject.com/)
- [Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/)

### External Packages

- Nginx: web proxy/server
- Docker (for [Doctor](https://github.com/freelawproject/doctor))
