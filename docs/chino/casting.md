# Casting

Casting sends a title from the phone to a TV or a speaker on the same network.
The TV plays it, and the phone becomes the remote. People cast from many apps,
so they expect the same button and the same controls everywhere. chino uses
Google Cast's own widgets, in chino's colours.

## The cast button

- It appears only when a device that can play is on the network.
- It sits in the top bar of the player and of a title's page, on the right.
- Its look is Google's icon: outlined when nothing is connected, moving while it
  connects, filled while casting.

## While casting

- **The bar**, above the bottom navigation, never over it: the title, “playing
  on Living Room TV” with the device's own name, and play or pause. Tapping it
  opens the full controls.
- **The full controls**: the artwork, the title, the position with a seek bar,
  play or pause, back and forward 10 seconds, subtitles and audio when the TV
  offers them, and “stop casting”.
- **Outside the app**: Google's media notification and the lock screen show the
  title, the device, play or pause, and stop. While a TV plays, the phone keeps
  a quiet notification of its own, “Keeping your place while Living Room TV
  plays”, so it can save the position.
- **Handing over**: when casting starts, the title continues on the TV from
  where it was, and the phone's player closes. When people stop casting, the
  phone keeps the TV's position.
- **Changing accounts**: signing out, removing the account, changing the server
  or switching to another account saves the position and stops casting, so a
  title never keeps playing under the next person. The question before signing
  out, removing the account or changing the server says “Casting on Living Room
  TV stops.”; after a switch, a toast says “Stopped casting on Living Room TV.”
- **Downloads without the server**: a downloaded title plays on the phone, even
  while a TV is connected, and a toast says why: “Playing on this phone: the
  server can't be reached.”

## When the TV can't play a title

The app sends a version the TV can play whenever there is one. When there
isn't, a warning banner: “Living Room TV can't play this title.”, with the
reason under details, for example “the server no longer accepts this phone's
sign-in (HTTP 401)” or “the server doesn't let this account play it (HTTP
403)”. Casting stops, and the title stays where it was on the phone.

## Words

- The device's name comes from the network, as people named it. A device without
  a name is “the device”. Never “the TV” as a name, and never a product name the
  device didn't give itself.
- Our words are “playing on …” and “stop casting”; the device chooser's words
  are Google's.
- In the casting messages, the phone is “this phone” or “this tablet”, never
  “this device”: “the device” is the TV.

## For the builders

- Google's Cast library draws the button, the device chooser, the bar, the full
  controls and the notification, themed with the app's colours: the full
  controls on the background colour, the bar on the surface colour, the seek bar
  and the active controls in the accent blue. Labels and icons on blue are dark.
- The bar is part of the screen's layout, above the bottom navigation.
- The TV's default receiver shows Google's own screen while it loads.
- One media notification instead of two needs a real Cast device to test: later.
