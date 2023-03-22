# Instructions to get Twitter tokens:
1. Log in to your bot's Twitter account.
2. Make sure you set the consumer key and secret in your .env file.
3. Run the script using the following command:

        docker exec -it bc2-django python /opt/bigcases2/scripts/get-twitter-keys.py

4. Click on the link that the script produces, then click "Authorize App" (Make sure you are logged in to your bot's Twitter account!).

5. Copy the code shown on the web browser and paste it into the console running the script and press enter.

6. The `access token` and `token secret` for your bot's account should be shown. Use them in your .env file.

7. The script should also show the `account name` and `account id`. Use the admin panel to create a new channel using the information about the authorized user.
