# ADR-0022: A cast starts chino on the TV, through the TV's own system, and plays as the person who sent it

**Status:** Proposed · 2026-11-15, for the owner's review. Design ahead of the code: nothing of it is built.

## Context

People expect to pick a title on the phone and have it play on the TV: the TV is on, nothing is open on it, and the title starts in the product's own TV app, as the person who picked it. Today chino cannot do that.

- Only the Android phone app casts. It uses Google Cast and sends the title to Google's default receiver, a page of Google's that plays a stream and draws text subtitles alone. The iOS app sends a title to a screen with AirPlay, from the player. The web does not cast.
- The TV apps take nothing from another device. The Android TV app has no cast library and no media session; the Samsung TV app has background support switched off and no second-screen library. No app and no service announces itself on the home network.
- A TV app is signed in to with a code shown on the TV and typed on another device. It then plays for that account until somebody signs out.
- chino-api gives a signed-in app a stream pass (`POST /api/v1/me/stream-token`): a value bound to the person, good for 6 hours, accepted on the media, artwork and playback-event routes alone. The phone puts it into the stream's address for the receiver. It opens the person's media; it does not let another device read a title's details or write the person's position.
- The server keeps no list of the screens that are on.

So a title cast from the phone plays on Google's page, not in chino: the picture is not fitted, subtitles made of pictures are missing, and a styled subtitle loses its styles ([chapter 14](../../spec/chino/casting.md), change 14.C4).

## Decision

1. **The TV's own system starts the app.** On Android TV and Google TV, the TV app is a receiver of Google Cast for the product's own Cast application. A sender asks the TV for that application; the TV's system starts the app when it is installed and loads the product's receiver page when it is not. The TV has to be on and on the same network as the sender. The app need not be open, and nobody need be signed in on it. Nothing of the platform has to find the TV: the system's own discovery does.
2. **One Cast application, two receivers.** The product registers one Cast application with Google. Its receiver page is the fallback for every Google Cast device without the app, and draws subtitles as the apps do (change 14.C4). The Android TV app is linked to the same application by its package name. A sender does not need to know which of the two answers.
3. **The TV plays as the person who sent the title, for that cast only.** The sender asks chino-api for a cast pass for the title: a value that can be used once, within 60 seconds. It hands the pass to the TV with the request to start. The TV app gives the pass to chino-api and gets a session of the sender's for that title alone: its details and tracks, its streams, the resume point, writing the position back, and the playback events. The sender's age-rating cap holds. The session ends when casting stops, and after 6 hours at most.
4. **A cast signs nobody in.** The TV app keeps the session in memory. It adds no account to the TV, shows nothing else of the sender's, and when casting stops it shows what it showed before: the screen of whoever is signed in on the TV, or its sign-in screen. A sender who wants the TV to stay signed in signs in on the TV, with a code, as today.
5. **Every sender the system offers.** The Android phone app first. The iOS app gets the cast button beside AirPlay, and the web gets it in the browsers that have Google Cast built in; both hand over a cast pass the same way.
6. **Samsung TVs are not started from the phone in this step.** Samsung TVs have no Google Cast. Samsung offers a second-screen mechanism of its own that can start a TV app from a phone; its documentation says several of its features have ended. A trial on a real TV comes before any promise.

## Consequences

- A title sent from the phone plays in chino's own player on the TV: the picture fitted, every subtitle, the remote working as in the app.
- The household needs nothing but the TV app from the store. Nothing is paired and nothing is typed.
- The sender's account never rests on a shared TV, so a guest can cast without leaving a sign-in behind, and a child's cap goes where the child casts.
- The product needs a Cast application registered with Google, once, by whoever publishes the apps, and the Android TV app has to come from Google Play or run on a device registered for testing: Google's system starts no other.
- chino-api gets a second kind of pass. It is narrower than a sign-in and wider than the stream pass: one title, one use, one device.

What it rules out:

- **A list of screens kept by the server**, with the TV apps holding a connection open and the phone choosing from the list. It needs the TV app to be open in front, which is the case people least expect to be necessary; and it adds a relay, across the server's instances, that the TV's system already is. It stays possible later as a help for TVs without a system of their own, never first.
- **The apps announcing themselves on the home network** by a protocol of the product's own. A browser cannot listen for it, each TV system needs its own, and none can start an app that is closed.
- **Signing the sender in on the TV by a cast.** A shared TV would collect accounts nobody meant to leave there, and the rating cap of the next person to pick up the remote would be the sender's.
- **Handing the TV the phone's own sign-in.** The TV would hold everything the phone may do, for as long as the phone's sign-in lasts.

## To prove first

- On a real Android TV with the app installed from Google Play's test track: a sender asks for the product's Cast application, the system starts the app, the app receives the value the sender handed over, and a sender on a TV without the app gets the receiver page. Google's documentation describes each step; none has been tried with chino.
- That the app, started this way while another account is signed in on the TV, can play and return without touching that account's state.
- If the system does not start the app in a case people meet often, such as a TV in standby, the changes stay as they are and the chapter says so under States; the receiver page remains the fallback.
- For Samsung TVs: a trial of the second-screen mechanism on a real TV decides whether a change is proposed at all.
