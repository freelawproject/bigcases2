from django.shortcuts import render

# Create your views here.

# @bp.route("/webhooks/mastodon", methods=["POST"])
# def receive_push():
#     logger.debug("Received a push webhook from Mastodon.")
#     logger.debug(f"Request: {request}")
#     logger.debug(f"Request headers: {request.headers}")
#     logger.debug(f"Request data: {request.data}")
#
#     m = get_mastodon()
#     priv_dict, pub_dict = get_keys()
#     push = m.push_subscription_decrypt_push(
#         data=request.data,
#         decrypt_params=priv_dict,
#         encryption_header=request.headers.get("Encryption"),
#         crypto_key_header=request.headers.get("Crypto-Key"),
#     )
#     logger.debug(f"push: {push}")
#
#     return {
#         "status": "ok",
#     }
