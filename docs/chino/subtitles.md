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
  come inside a file are ignored.
- **One subtitle at a time.**

When someone has set caption preferences on the device, under accessibility,
those win over this look: for example a box behind the text.

## The menu

The menu is headed “subtitles”. In this order:

1. **off**
2. **the person's preferred subtitle language**, when the title has it
3. **the server's other subtitle languages**, read from its configuration
4. **more languages**, when the file brings others; it opens the rest

When the server names no subtitle languages, all of the title's tracks are
listed directly, the preferred language first, without “more languages”.

Within a language: the plain track first, then “for deaf and hard of hearing”,
then “foreign-language parts only”, then “AI”. Names follow the [word
list](./words.md):

- “English · for deaf and hard of hearing”
- “German · foreign-language parts only”
- “Chinese (Simplified) · AI”

Two tracks of the same language and kind show once, the file's own first. Words
in a file's label that only name the language again (“Deutsch”, “中文”) are
dropped; words that add something stay (“English · Commentary”). Subtitles
stored as pictures inside a file aren't offered.

## What switches on by itself

- **The preferred subtitle language**, when the audio is in another language.
- **“foreign-language parts only” in the audio's language**, because it
  translates the lines the audio doesn't.
- **Nothing else.** Subtitles in the audio's own language are the person's
  choice, made in the menu.

## For the builders

- Android (Media3): a subtitle view with embedded styles and embedded font sizes
  switched off, a fractional text size of 0.0533, and a caption style of white
  text, a black outline, and a transparent background and window. When the
  system's caption settings are switched on, it takes the user's style and text
  size instead. The safe area comes from a bottom margin and the 80% width, not
  from padding the view.
- Web: the same through `::cue` (white, no background, an outline drawn with text
  shadows, a font size relative to the video's height), one active track.
