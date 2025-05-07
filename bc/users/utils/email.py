from django.conf import settings
from django.contrib import messages

from bc.users.types import EmailType, MessageType

emails: dict[str, EmailType] = {
    "account_deleted": {
        "subject": "User deleted their account on Bots.law!",
        "body": "Sad day indeed. Somebody deleted their account completely, "
        "blowing it to smithereens. The user that deleted their "
        "account was: \n\n"
        " - %s\n\n"
        "Can't keep 'em all, I suppose.\n\n",
        "from_email": settings.DEFAULT_FROM_EMAIL,
        "to": [a[1] for a in settings.MANAGERS],
    },
    "take_out_requested": {
        "subject": "User wants their data. Need to send it to them.",
        "body": "A user has requested their data in accordance with GDPR. "
        "This means that if they're a EU citizen, you have to provide "
        "them with their data. Their username and email are:\n\n"
        " - %s\n"
        " - %s\n\n"
        "Good luck getting this taken care of.",
        "from_email": settings.DEFAULT_FROM_EMAIL,
        "to": [a[1] for a in settings.MANAGERS],
    },
    "email_changed_successfully": {
        "subject": "Email changed successfully on Bots.law",
        "body": "Hello %s,\n\n"
        "You have successfully changed your email address at "
        "Bots.law. Please confirm this change by clicking the "
        "following link within five days:\n\n"
        "  https://bots.law/email/confirm/%s\n\n"
        "Thanks for using our site,\n\n"
        "The Free Law Project Team\n\n"
        "------------------\n"
        "For questions or comments, please see our contact page, "
        "https://free.law/contact/.",
        "from_email": settings.DEFAULT_FROM_EMAIL,
    },
    "notify_old_address": {
        "subject": "This email address is no longer in use on Bots.law",
        "body": "Hello %s,\n\n"
        "A moment ago somebody, hopefully you, changed the email address on "
        "your Bots.law account. Previously, it used:\n\n"
        "    %s\n\n"
        "But now it is set to:\n\n"
        "    %s\n\n"
        "If you made this change, no action is needed. If you did not make "
        "this change, please get in touch with us as soon as possible by "
        "sending a message to:\n\n"
        "    security@free.law\n\n"
        "Thanks for using our site,\n\n"
        "The Free Law Project Team\n\n",
        "from_email": settings.DEFAULT_FROM_EMAIL,
    },
    "confirm_your_new_account": {
        "subject": "Confirm your account on Bots.law",
        "body": "Hello, %s, and thanks for signing up for an account on "
        "Bots.law.\n\n"
        "To send you emails, we need you to activate your account with "
        "Bots.law. To activate your account, click this link "
        "within five days:\n\n"
        "    https://bots.law/email/confirm/%s/\n\n"
        "Thanks for using Bots.law and joining our community,\n\n"
        "The Free Law Project Team\n\n"
        "-------------------\n"
        "For questions or comments, please see our contact page, "
        "https://free.law/contact/.",
        "from_email": settings.DEFAULT_FROM_EMAIL,
    },
    "confirm_existing_account": {
        "subject": "Confirm your account on Bots.law",
        "body": "Hello,\n\n"
        "Somebody, probably you, has asked that we send an email "
        "confirmation link to this address.\n\n"
        "If this was you, please confirm your email address by "
        "clicking the following link within five days:\n\n"
        "https://bots.law/email/confirm/%s\n\n"
        "If this was not you, you can disregard this email.\n\n"
        "Thanks for using our site,\n"
        "The Free Law Project Team\n\n"
        "-------\n"
        "For questions or comments, please visit our contact page, "
        "https://free.law/contact/\n"
        "We're always happy to hear from you.",
        "from_email": settings.DEFAULT_FROM_EMAIL,
    },
    # Used both when people want to confirm an email address and when they
    # want to reset their password, with one small tweak in the wording.
    "no_account_found": {
        "subject": "Password reset and username information on Bots.law.com",
        "body": "Hello,\n\n"
        ""
        "Somebody — probably you — has asked that we send %s "
        "instructions to this address. If this was you, "
        "we regret to inform you that we do not have an account with "
        "this email address. This sometimes happens when people "
        "have have typos in their email address when they sign up or "
        "change their email address.\n\n"
        ""
        "If you think that may have happened to you, the solution is "
        "to simply create a new account using your email address:\n\n"
        ""
        "    https://bots.law%s\n\n"
        ""
        "That usually will fix the problem.\n\n"
        ""
        "If this was not you, you can ignore this email.\n\n"
        ""
        "Thanks for using our site,\n\n"
        ""
        "The Free Law Project Team\n\n"
        "-------\n"
        "For questions or comments, please visit our contact page, "
        "https://free.law/contact/\n"
        "We're always happy to hear from you.",
        "from_email": settings.DEFAULT_FROM_EMAIL,
    },
    "new_account_created": {
        "subject": "New user confirmed on Bots.law: %s",
        "body": "A new user has signed up on Bots.law and they'll be "
        "automatically welcomed soon!\n\n"
        "  Their name is: %s\n"
        "  Their email address is: %s\n\n"
        "Sincerely,\n\n"
        "The Bots.law Bots",
        "from_email": settings.DEFAULT_FROM_EMAIL,
        "to": [a[1] for a in settings.MANAGERS],
    },
}

message_dict: dict[str, MessageType] = {
    "email_changed_successfully": {
        "level": messages.SUCCESS,
        "message": "Your settings were saved successfully and you have been "
        "logged out. To sign back in and continue using "
        "Bots.law, please confirm your new email address by "
        "checking your email within five days.",
    },
    "settings_changed_successfully": {
        "level": messages.SUCCESS,
        "message": "Your settings were saved successfully.",
    },
    "pwd_changed_successfully": {
        "level": messages.SUCCESS,
        "message": "Your password was changed successfully",
    },
}
