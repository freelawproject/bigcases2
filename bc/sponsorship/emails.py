from django.conf import settings

from bc.users.types import EmailType

emails: dict[str, EmailType] = {
    "low_funds_alert": {
        "subject": "Bot's sponsorship funds are running low!",
        "body": "Dear curator,\n\n"
        "I'm writing to you today with an exciting update about the %s, "
        "Thanks to your efforts and the generosity of our current sponsors, "
        "we've purchase %s documents so far, which is incredible. But as we "
        "look toward the future, there's one area where we'd appreciate your "
        "help: securing additional sponsorships.\n\n"
        "Remember, even small contributions can make a big difference. By "
        "working together, we can not only keep our current momentum going "
        "but also expand our reach and impact to an even greater extent.\n\n"
        "We're confident that with your help, we can find incredible new partners "
        "who share our vision and commit to supporting the Bot's long-term success.\n\n"
        "Thank you for your dedication and passion. Let's keep the momentum going!\n\n"
        "The Free Law Project Team",
        "from_email": settings.DEFAULT_FROM_EMAIL,
    }
}
