# Architecture of Big Cases Bot 2

## CourtListener API

Big Cases Bot 2 uses [CourtListener's REST API](https://www.courtlistener.com/api/rest-info/) to receive news about new filings. It does this via [webhooks](https://www.courtlistener.com/profile/webhooks/), which are a new feature of the API. When CourtListener learns about a new docket entry in a followed case, CourtListener will POST a webhook to BCB2 with information about the docket entry and documents associated with it.

## Database

BCB2 uses a [Postres](https://www.postgresql.org/) database to keep track of cases and documents it knows about. The original BCB1 used MySQL.

## Posting

BCB2 posts to both Twitter ([@big_cases](https://twitter.com/big_cases)) and Mastodon ([@big_cases@law.builders](https://law.builders/@big_cases)).

## Interacting via social media

- `hey @big_cases, follow nysd 22-cv-12345`

## Command Line Interface

- `big_cases init`: Initialize BCB2 (create database, check environment, etc.)
- `big_cases init-db`: Re-initialize database
- `big_cases backup`: Save a snapshot of the database with current timestamp
- `big_cases empty-db`: Delete all rows in database, but leave structure intact
- `big_cases restore-db`: Restore database from a saved snapshot
- `big_cases load-bcb1-json`: Import cases from Big Cases Bot 1's JSON file
- `big_cases load-bcb1-db`: Import more data from Big Cases Bot 1's MySQL database
- `big_cases search nysd 22-cv-12345`: Search for a case and add it
- `big_cases post`: Post a message
- `big_cases list`: List subscribed cases

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

- [ ] How do we receive messages from Mastodon?
  - [Web Push API](https://docs.joinmastodon.org/methods/push/)
    - Set `data[alerts][mention]` to `true`
    - [In Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/#push-subscriptions)
- [ ] How do we receive messages from Twitter?
  - [Webhooks via Account Activity API](https://developer.twitter.com/en/docs/twitter-api/enterprise/account-activity-api/guides/getting-started-with-webhooks) (application pending)
- [ ] Is an admin page needed? (Will require further locking down the server (nginx).)
- [ ] How does BCB1 generate images?
- [ ] How does CL generate thumbnail images? (e.g., [this one](https://storage.courtlistener.com/recap-thumbnails/gov.uscourts.cand.297616/2176640.thumb.1068.jpeg))
  - [Doctor](https://github.com/freelawproject/doctor) microservice, [`/convert/pdf/thumbnails/`](https://github.com/freelawproject/doctor#endpoint-convertpdfthumbnails) endpoint
- [ ] Are Celery tasks needed?
  - Image generation: Probably
- [ ] How do we pick up or get a callback when the thumbnails are done?

## Key Dependencies

### Python Packages

- [Flask](https://flask.palletsprojects.com/en/2.2.x/)
- [Mastodon.py](https://mastodonpy.readthedocs.io/en/stable/)

### External Packages

- Nginx: web proxy/server
- Docker (for [Doctor](https://github.com/freelawproject/doctor))
