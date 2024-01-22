from django.conf import settings

from bc.users.types import EmailType

emails: dict[str, EmailType] = {
    "low_funds_alert": {
        "subject": "Please re-up your funding of {bot_name}",
        "body": "Hello,\n\n"
        "I am writing because the bot you sponsor on bots.law, {bot_name}, is "
        "running low on funding.\n\n"
        "It currently has ${amount_remaining}, and you originally funded it "
        "with ${original_amount}.\n\n"
        "Thank you for your sponsorship of this bot! We firmly believe that "
        "the support you provide contributes important records to our shared "
        "cultural history.\n\n"
        "To continue sponsoring this bot, please do two things:\n\n"
        "   1. Make a payment to Free Law Project at:\n\n"
        "   https://donate.free.law/forms/pay\n\n"
        "   2.Forward your payment receipt to info@free.law so the money can "
        "be allocated to your bot (unfortunately this isn't automated yet!).\n\n"
        "Thank you for your continued support of our bots! Bringing this kind "
        "of vital information to everybody is an important way to fight "
        "misinformation and educate the public.\n\n"
        "Sincerely,\n\n"
        "The Free Law Project Team.",
        "from_email": settings.DEFAULT_FROM_EMAIL,
    }
}
