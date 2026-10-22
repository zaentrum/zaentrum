# Playback

## Play, resume and a finished title

- A title people stopped part way shows **resume 1:43**, with **start over**
  beside it.
- A title stopped within its last 5 % or its last 2 minutes, whichever is
  longer, counts as **finished**: it shows **play**, from the start, and the
  watched mark. For a short title, finished never starts before its second
  half.
- The server decides finished, once, so every app agrees. Continue watching
  drops a finished film and moves a finished episode on to the next one.
- Removing a title from continue watching doesn't mark it as watched.

## When the quality changes by itself

When playback has to step down, the player says what it did and why, with the
quality's name as the quality menu shows it:

- “Switched to Medium quality: the connection can't keep up with the original.”
- “Switched to Medium quality: the original couldn't be streamed.”
- “Switched to Low (480p) quality: the connection can't keep up.”

It keeps the position. Status codes go into the playback report, never into
the line.

## When a page couldn't load

The apps follow the design system's [cases by
cause](https://nalet.github.io/design-system/patterns/empty-states/#when-it-couldnt-load-say-why).
For chino:

- A removed title or person: “this title isn't in the library anymore” or “this
  person isn't in the library anymore”, with **back**.
- A list screen that gets “not found” means the app and the server don't match:
  “The server didn't accept the request. Check for an app update, then try
  again.”
- A sign-in that expired renews itself; only a refused one leads to sign-in.
