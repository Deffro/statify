# Statify

## How to run
- Create an app in [spotify](https://developer.spotify.com/dashboard/applications) and generate your client id and client secret.
- Copy and paste them in server.py
- Run ngrok.exe and type ngrok http 8080
- Copy and paste the ngrok url in CLIENT_SIDE_URL in server.py
- From terminal run: python server.py
- In a browser visit the ngrok url

**Known Bugs**
- If the message "error loading dependencies" appears, it is a [known bug](https://github.com/plotly/dash/issues/125) and just refresh the page.
- If you visit the site and after you another person in the world also visits the site, then if you refresh the "/app/" page you will see his statistics and not yours. If you want to see your statistics refresh the index page. The current state of the app is not to be refreshed. 
