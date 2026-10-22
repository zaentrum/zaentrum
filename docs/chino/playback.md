# Playback

What a title offers when people come back to it, when it counts as finished,
what the player says when it changes the quality by itself, and what a page
says when it couldn't load. Every app follows the same rules, so a title
resumes and finishes the same way everywhere.

## Play, resume and a finished title

- A title people stopped part way shows **resume 1:43**, with **start over**
  beside it.
- A title stopped within its last 5% or its last 2 minutes, whichever is
  longer, counts as **finished**: it shows **play**, from the start, and the
  watched mark. For a short title, finished never starts before its second
  half.
- The server decides finished, once, so every app agrees. Continue watching
  drops a finished movie and moves a finished episode on to the next one.
- Removing a title from continue watching doesn't mark it as watched.

## Quality names

The server names every quality, by one fixed table of heights, so a name means
the same height on every title and every installation. The apps show the name as
the server gives it.

| Height | Name |
|---|---|
| 2160p and up | “Ultra (2160p)” |
| 1080p | “High (1080p)” |
| 720p | “Medium (720p)” |
| 480p | “Low (480p)” |
| below 480p | “Lowest (360p)” |
| the original, played as it is | “Original” |

A height between two steps takes the lower step's name with its own height:
“Medium (900p)”. A re-encode at the original's size is named by its height like
any other step.

## The player's menus

- Subtitles, audio, quality and speed are menus of one choice each. They show
  no checkboxes and no check marks: the picked row is in the accent blue, with a
  small filled square before it, square like every shape in the design system.
  Every row keeps the square's column, so the names line up whether picked or
  not.
- An audio track names its channels in words: “Stereo”, “5.1”, “7.1”, “Mono”,
  never “2ch”.
- Their headers are lowercase: “subtitles”, “audio”, “quality”, “speed”, and
  “timing” for the subtitles' timing, whose button is “reset”.
- Controls over the picture, such as a chip, sit on a solid surface, never on a
  see-through one.

## When the quality changes by itself

When playback has to step down, the player says what it did and why. {label}
is the quality's name from the table above: “Medium (720p)”, “Low (480p)”.

- From the original, when the connection is too slow: “Switched to {label}
  quality: the connection can't keep up with the original.”
- When the original can't be streamed: “Switched to {label} quality: the
  original couldn't be streamed.”
- One step down between qualities: “Switched to {label} quality: the
  connection can't keep up.”
- When a quality between can't be streamed: “Switched to {label} quality:
  {previous} couldn't be streamed.”, {previous} named from the same table:
  “Switched to Low (480p) quality: Medium (720p) couldn't be streamed.”

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
