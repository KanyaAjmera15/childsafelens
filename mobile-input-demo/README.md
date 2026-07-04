# ChildSafeLens Demo Input App (B)

Expo app: a text input, a Send button, and the pre-emptive nudge overlay.
This is the "child types a message" side of the demo.

## 1. Set up a fresh Expo project and drop these files in

Easiest path — create a new Expo app, then replace its default files with
the ones here:

```bash
npx create-expo-app childsafelens-input
cd childsafelens-input
```

Copy `App.js` and `api.js` from this folder into the new project, replacing
the generated `App.js`. No extra native dependencies are needed — this uses
only core React Native components (`View`, `TextInput`, `Modal`, etc.), so
there's nothing else to install.

## 2. Point it at the backend

Open `api.js` and set:

```js
export const API_BASE_URL = "https://<the-url-C-gives-you>.onrender.com";
```

While C's backend isn't deployed yet, you can test against it running
locally on a laptop on the same wifi network — use the laptop's LAN IP
(e.g. `http://192.168.1.23:8000`), not `localhost` (a phone's `localhost`
means the phone itself, not your laptop).

## 3. Run it

```bash
npx expo start
```

Scan the QR code with Expo Go on your phone (Android or iOS), or press `a`
for an Android emulator / `i` for an iOS simulator if you have one set up.

## 4. What to check works before the demo

- Typing a normal message and hitting Send: no nudge, message logs as
  `low_risk` in the "Recent activity" list.
- Typing something from your risky test set: the nudge modal appears with
  "Edit message" / "Send anyway".
- Tapping "Send anyway" logs the event and clears the input.
- Tapping "Edit message" closes the nudge and keeps your text in the box
  so you can change it live during the demo.

## 5. If C's backend isn't ready yet

You don't have to wait — temporarily point `API_BASE_URL` at
`http://localhost:8000` and run C's backend locally on your own machine
(see `backend/README.md`) to keep testing the UI end-to-end.
