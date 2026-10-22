# Subtitles

Subtitles are read in a second, over a moving picture, sometimes from across the
room. They are plain and steady: the same look for every title, covering as
little of the picture as they can, and only one at a time. The web, the TV and
the phone apps show them the same way.

## The look

- **White text with a black outline**, with no box behind it.
- **Its size follows the picture**: 5.33% of the picture's height.
- **The device's own sans-serif font**, so every language has its letters,
  Chinese, Japanese and Korean included.
- **Centred at the bottom**, inside the picture, 8% above its bottom edge; at
  most two lines where the text allows, within 80% of the picture's width. On a
  TV, it stays inside the safe area.
- **One look for every title.** Colours, sizes, boxes, fonts and positions that
  come inside a file are ignored. Italics stay, because they mean something: a
  voice from off screen, a song, a thought. Ruby, the small readings above
  Japanese and Chinese characters, stays too.
- **One subtitle at a time.**
- **Out of the controls' way**: while the player's controls show, the line moves
  up above them, and back down when they hide, at the controls' own pace.

When someone has set caption preferences on the device, under accessibility,
those win over this look: for example a box behind the text. The TV and the
phone apps read them; a web page can't, so the web app always shows this look.

## The menu

The menu is headed “subtitles”. It is a menu of one choice, like the player's
[other menus](./playback.md#the-players-menus). In this order:

1. **off**
2. **the person's preferred subtitle language**, when the title has it
3. **the server's other subtitle languages**, read from its configuration
4. **more languages**, when the file brings others; it opens the rest

When the server names no subtitle languages, all of the title's tracks are
listed directly, without “more languages”: the preferred language first, then
the others in the file's order. A language's tracks stay together, AI ones
included, and a language with its region or script counts as that language:
“Chinese (Simplified) · AI” follows “Chinese”.

Within a language: the plain track first, then “for deaf and hard of hearing”,
then “foreign-language parts only”, then “AI”. Names follow the [word
list](./words.md):

- “English · for deaf and hard of hearing”
- “German · foreign-language parts only”
- “Chinese (Simplified) · AI”

Tracks that would read the same show once: one inside the file before one the
server adds, otherwise the first in the file. They are never numbered, as in
“English (2)”. Words in a file's label that only name the language again (“Deutsch”, “中文”) are
dropped; words that add something stay (“English · Commentary”). Subtitles
stored as pictures inside a file aren't offered.

## What switches on by itself

- **The preferred subtitle language**, when the audio is in another language.
- **“foreign-language parts only” in the audio's language**, because it
  translates the lines the audio doesn't.
- **Nothing else.** Subtitles in the audio's own language are the person's
  choice, made in the menu.

The rule compares with the audio that is playing, never with the preferred audio
language. A choice in the menu lasts for what is playing now; the next title
follows the setting again.

## The setting

Settings has one subtitle language, “Off” or a language, with this text under
it, the same in every app:

> Subtitles in the language you pick here come on when a title's audio is in
> another language. Otherwise, only the foreign-language parts get subtitles,
> where a title has them. A choice in the player applies only to what's playing
> now.

## For the builders

- Android (Media3): a subtitle view with embedded styles and embedded font sizes
  switched off, a fractional text size of 0.0533, and a caption style of white
  text, a black outline, and a transparent background and window. When the
  system's caption settings are switched on, it takes the user's style and text
  size instead. The safe area comes from a bottom margin and the 80% width, not
  from padding the view. Switching embedded styles off also drops italics, so
  the apps keep italic spans themselves; ruby survives the switch.
- Web: an overlay the app draws instead of the browser's own captions, one track
  at a time: white, no background, an outline drawn with text shadows in eight
  directions, a font size relative to the picture's height. It keeps `<i>` and
  `<ruby>` from the cue and drops every other style.
- Language names come from the platform in their standard form, the language
  first and the region or script in brackets: “Portuguese (Brazil)”, “English
  (Guam)”, “Chinese (Simplified)”. On the web that is `Intl.DisplayNames` with
  `languageDisplay: 'standard'`; its default gives “Brazilian Portuguese”.
