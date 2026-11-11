# BillKarta: build and publish guide

## 1. Build the app
1. Install Android Studio (free) and open this `BillKarta` folder.
2. Wait for Gradle sync. Accept any "upgrade plugin" prompt.
3. Plug in a phone (USB debugging on) or use an emulator, then press Run.
4. Test: front page, both tabs, add a duty, make a PDF (it should save to
   Downloads/BillKarta and open), backup export and import, WhatsApp button, Back button.

## 2. Update pages later
Pull the latest page code from GitHub, then run:

    ./sync-pages.sh /path/to/folder/containing/frontpage-Work-forall

Raise `versionCode` in `app/build.gradle.kts` by 1 for every Play Store update.

## 3. Sign and create the Play Store file (.aab)
1. Android Studio: Build > Generate Signed App Bundle / APK > Android App Bundle.
2. Create a new keystore. KEEP IT AND ITS PASSWORDS SAFE. Losing it can block updates.
   (Or use Play App Signing, which Google recommends.)
3. Output: `app/release/app-release.aab`. Upload this file to Play Console.

## 4. Play Console steps
- Create a developer account (one-time fee, identity verification).
- Create app: name BillKarta, free, app (not game).
- Store listing: short description, full description, 512x512 icon
  (`store/icon-512.png`), feature graphic 1024x500, at least 2 phone screenshots.
- Privacy policy: host `PRIVACY_POLICY.md` as a web page (a GitHub Pages page works)
  and paste the link.
- Data safety form: the app collects no data on its own servers. Data stays on the phone.
- Content rating questionnaire, target audience (18+), ads: none.
- New personal developer accounts must run a closed test with testers for a set
  period before production. Check Play Console for the current requirement.

## Notes
- The app works fully offline and asks for no permissions. The Poppins font is bundled inside it.
- Data is stored inside the app. It is separate from data in your github.io pages. Users
  moving from the website should use Backup > Export there and Import in the app.
- If the user clears app data or uninstalls, saved duties are lost. Remind users to back up.
