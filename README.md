**A system that will display your most recent played (or currently playing) Youtube Music song in your GitHub profile!**
<p align="center"> <img src="https://yt-music-readme.vercel.app/" alt="Imagen"></p>
<p>The design is not the best in the world, I'm stil working on it xD</p>

## Setup/Deployment
#### 1. Creating the credentials

- Head over to <a href="https://console.cloud.google.com">Google Cloud Console</a>.
- Create a new Google Cloud project and select it.
- Go to **Api and Services** and then click on **Credentials**. Select option that contains "**OAuth**".
  - Follow the necessary steps to set up a welcome page (make sure to select the **external users** option).
    - When you finish, click on **Public** and on **Test users** add your own mail.
    - Reload the page and click on **Clients**.
      - Select the **TV devices** (Or something similar) option.
      - **TAKE NOTE OF THE ```Client ID``` AND ```Client Secret```**.
     
#### 2. Setting up the app
- Make sure to have Python installed.
- Install "ytmusicapi" package:
 ```bash
  pip install ytmusicapi
  ```
- Execute "ytmusicapi browser" in the terminal.
  - Follow [this tutorial](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html) from the official documentation. Use Firefox if possible.
  - Once you are done, you will create a .json file. Save it.
 
#### 3. Final step before hosting
- Download this repo as a .zip and create a new **private GitHub repo** with the content of it (it can't be forked because it'll contain sensible data, so it must be private).
- Edit the **.gitignore**, remove line that says ***.json*** and add ***browser.json*** to the repo.
- Save the changes.

#### 4. Hosting on ~~PythonAnywhere~~ Vercel✅
**I tried hosting it on PythonAnywhere, but for free users it blocks the access to every page that isn't in their whitelist, and Youtube is one of them. I also tried Koyeb, Render and Railway, but they didn't convince me. *If you now any other free page that works fine, please let me now*.**
- Create a Vercel account and select "Add New... > Project"
- Give it access to the repo you created in step 3.
- Click on **Environment Variables**
  - Create two environment variables: ```CLIENT_ID``` and ```CLIENT_SECRET```, each one containt their respective info, which you already have.
- Click on **Deploy**.

AND THAT'S ALL :D<br>
**Now you can copy the URL from Vercel and paste it into your GitHub README with a *img* tag**

## Known issues
### The song I'm listening to is not the same as the one shown in Github
This is normal. <br>
On the one hand, Youtube Music sucks and sometimes doesn't update your history (you can verify this yourself by listening to something and sometimes you'll notice that it doesn't appear on your history). <br>
On the other, GitHub needs to upload the image in their own domain before showing the image. In additions, your browser saves cache. Give it time and, after a few reloads, the image will appear (I hope so)😎.

### Nothing is shown on the Readme
Click the image link and then reload GitHub. Vercel issues, idk.

### Nothing is shown on the Readme, and if I try to access the website, it says *Internal Server Error*
Go to Vecel and then "Logs". **If it says something related to Youtube Authorization, repeat everything from step 2**.

## FAQ
### Why have you decided to include a modified version of YTMusicAPI? (credits below)
Vercel readonly filesystem seems to have problems with the way the API stores the YT Music token, so I needed to change some things and therefore ship the entire library instead of a reference in "requirements.txt". I already opened a Pull Request to see if my solution can be included in the official package, and if that ends up happening, I will remove the modified library.

## Special thanks to
- @tthn0 for making something similar for Spotify, which inspired me.
- @sigma67 for making the *ytmusicapi* package.