# 18 Words

The words chino uses for its own things. Each means one thing, in every app.
The general rules for writing are in the design system's [meaningful
text](https://nalet.github.io/design-system/foundations/meaningful-text/) and
[content & voice](https://nalet.github.io/design-system/foundations/content-voice/).

These are the target's words. Where an app says something else today, the
chapter of that screen says so in its section “As deployed” and lists the new
words as a numbered change: the subtitle and audio tags are change 12.C3 of
[chapter 12](./subtitles.md), the notifications' words change 15.C1 of
[chapter 15](./notifications.md).

## 18.1 The word list

| Use | For | Not |
|---|---|---|
| “(CC)” | Subtitles that also describe sounds and name who speaks, a tag after the language: “English (CC)” ([chapter 12](./subtitles.md)) | “SDH”, “for deaf and hard of hearing”, “hearing impaired” |
| “(AI)” | Subtitles made by the platform, a tag after the language: “German (AI)”; two tags share one bracket, “English (CC, AI)”, and a language's own bracket stays, “Chinese (Simplified) (AI)” | “auto”, “generated”, “· AI” |
| “foreign-language parts” | The lines in another language that come on by themselves, with the audio's language; they are never a row of the panel ([chapter 12](./subtitles.md)) | “forced”, “foreign-language parts only” as a track's name |
| “(audio description)” | An audio track with a voice that describes the picture: “English (audio description)” | “AD”, “described video”, “visually impaired” |
| “(5.1)”, “(stereo)” | An audio track's channels, a tag only where two tracks of one language would read the same without it: “English (5.1)”, “English (stereo)” | a codec, “AAC”, “MP4A.40.2”, “6 channels” |
| “audio and subtitles” | The player's panel that picks both, and its button ([chapter 12](./subtitles.md)) | “languages”, “tracks”, “audio & subtitles” |
| “subtitle timing” | Moving the subtitles earlier or later, in the player's settings menu: “+0.25s”, “−0.50s” | “subtitle delay”, “offset”, “sync” |
| “Portuguese (Brazil)” | A language with its region or script in brackets: “Chinese (Simplified)” | “Brazilian Portuguese”, “pt-BR” |
| “movies” | Films, as the app's tab says | “films” |
| “account” | Who is watching, as the account picker says | “profile”, “user” |
| “downloads”, “on this phone” | What is stored on the device (“on this tablet” on a tablet) | “offline mode”, “sync”, “cache” |
| “finished” | Watched to the end, or into its last minutes ([chapter 11](./playback.md)) | “completed” |
| “Medium (720p)” | A quality: its name and its height, from the table in [chapter 11](./playback.md) | “adaptive streaming”, a height or a bitrate alone, “High (source)” |
| “notifications” | What the bell holds ([chapter 15](./notifications.md)) | “notices”, “alerts” |
| “Original” (a quality) | The file a title was packaged from, played as it is: the quality “Original” in the player's settings menu ([chapter 11](./playback.md)) | “source”, “High (source)” |
| “Original”, “(original)” (audio) | The language a title was made in: the audio setting's “Original” ([chapter 16](./settings.md)), and the tag on that language's audio rows, “English (original)” ([chapter 12](./subtitles.md)) | “default”, “native” |
| “settings” | In the player, the menu of this playback's quality and subtitle timing ([chapter 11](./playback.md)); elsewhere the view that holds the account's settings ([chapter 16](./settings.md)) | “options”, “preferences” |
| “Watchlist” | The list every account has; it keeps its name, and the view that holds it with the other lists is “watchlist” ([chapter 8](./watchlist.md)) | “favourites”, “my list” |
| “list” | A named list of titles that an account made; making one is “create list” | “collection”, “playlist”, “new list” |
| “specials” | A show's episodes outside its numbered seasons ([chapter 6](./title-actions.md)) | “season 0”, “extras” |
| “cast & crew” | The people of a title, on its page | “credits” |
| “in the library” | What of a person's work the library holds, on their page ([chapter 7](./person.md)) | “filmography” |
| “the people who run this server” | Who receives a bug report | “the dev backlog” |

“Original” names two things, told apart by where it stands: in the player's
settings menu it is the file, in the audio setting and on an audio row the
language. They never share a list.

### Open

- **shows or series.** Every app's navigation says shows, and so do the
  drawings in this specification; the web's title badge says series.
  Recommendation: shows everywhere, and “series” nowhere on a screen.
