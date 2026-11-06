# 4 Home

> **Not in the new form yet.** This chapter's figures show the target, not
> what is deployed today. Where today's apps differ, its “Today's apps”
> section says so. The screens as deployed and the numbered changes follow,
> as [chapter 11](./playback.md) already has them.

This chapter specifies home, the first screen after signing in. The frame
around it, the top bar with the phone's tabs and the TV's rail, is specified in
[chapter 2](./frame.md).

## 4.1 Purpose

Home offers one title to start right away, then what the person is in the
middle of, then what's new in the library. Every app opens on home after
signing in, and the **home** view in the frame brings it back from anywhere.

## 4.2 Home on a computer

Figure 4.1 shows home on a computer. The hero takes the top of the page, and
the rows follow under it, each scrolling sideways.

![Figure 4.1: Home on a computer, at 1280 × 800](./img/home-computer.png)

Figure 4.1: Home on a computer, at 1280 × 800.

1. **The hero.** One title over its artwork: its name, then its year, length
   and genre, then a short description. The artwork fills the right side and
   fades into the page on the left, so the words always stand on the page's
   own colour, never on the picture. Section 4.5 says which titles the hero
   shows.
2. **play**, **see details** and **trailer.** play starts the title, see
   details opens its title page ([chapter 6](./title-actions.md)), and trailer
   plays its trailer. trailer is there only when the title has one.
3. **The squares.** Eight titles take turns in the hero. The square of the one
   showing is blue, and choosing another square brings that title.
4. **continue watching.** What the person stopped in the middle of. Each card
   shows the artwork with a bar for how far the person got, the title's name,
   and the time left. An episode puts its code first: “S01E03 · 24 min left”.
5. **next up.** The next episode of a show whose last episode the person
   finished. The rows that follow it are listed in section 4.5.

## 4.3 Home on a phone

Figure 4.2 shows the same screen on a phone. The parts are the same as in
figure 4.1; the numbers mark where the phone differs.

![Figure 4.2: Home on a phone, at 360 dp](./img/home-phone.png)

Figure 4.2: Home on a phone, at 360 dp.

1. **The hero** leaves out the description, which the title page has. The
   artwork fills the width and fades into the page below the name.
2. **play** and **see details** share the width; **trailer** is its icon only.
3. **The squares**, as on a computer. A swipe on the hero brings the next
   title as well.
4. **zap** opens zap ([chapter 10](./zap.md)). The phone app has no zap tab
   (section 2.3), so zap starts here, right under the hero.
5. **The rows** show one card and a part of the next, so it's plain that a row
   goes on sideways.

The web on a phone has the layout of figure 4.2 with one difference: zap is
its fifth tab, in place of downloads, so the web leaves out part 4.

## 4.4 Home on a TV

Figure 4.3 shows home on a TV. The rail is on the left, and the page keeps to
the TV's safe area, the dashed outline in the figure.

![Figure 4.3: Home on a TV, at 960 × 540 dp](./img/home-tv.png)

Figure 4.3: Home on a TV, at 960 × 540 dp.

1. **The hero**, as on a computer, with the description.
2. **The focus.** Home opens with the focus on **play**: the ring sits 2 dp
   outside the button, and the button grows by 5 %, as the design system's
   [TV focus](https://nalet.github.io/design-system/patterns/tv-focus/) sets
   out. Down moves the focus into the rows, up from the rows back to the hero.
3. **The squares** show which title is showing. Left and right on the hero's
   buttons move between the buttons, not between titles.
4. **A row runs past the safe area** to the edge of the screen. Only the
   artwork goes beyond the outline; the focus never does, because the row
   scrolls when the focus reaches the outline.

## 4.5 What home shows

### 4.5.1 The hero

The hero takes eight titles from the newest ones the person hasn't watched,
and only titles that have a trailer: first those whose trailer this server
plays, then those with a trailer elsewhere, each group in a new random order
every time home loads. Each title stays 20 seconds and then gives way to the
next. The hero doesn't move on while the pointer or the focus is on it, and
with reduced motion it changes without sliding.

### 4.5.2 The rows

| Row | What it holds | Order |
|---|---|---|
| continue watching | Titles and episodes the person watched for more than 30 seconds and hasn't finished | Last watched first |
| next up | The next episode of each show whose last episode the person finished | Last watched first |
| recently added movies | Movies the person hasn't watched | Newest first |
| recently added shows | Shows the person hasn't finished | Newest first |
| top rated | Movies rated 8 or higher that the person hasn't watched | Highest rated first |

When the server counts a title as finished ([chapter 11](./playback.md)), a
movie leaves continue watching and an episode makes way for the next one in
next up. A card's menu in continue watching has **remove from continue
watching**, which takes the card off without changing what was watched.

A row holds up to 20 titles. recently added movies, recently added shows and
top rated end with a **see all** card, which opens movies or shows in that
row's order ([chapter 5](./browse.md)); continue watching and next up hold
everything they have and end without one. A row with nothing in it is left
out, and the rows keep their order when one is missing.

## 4.6 States

Home is drawn in figures 4.1 to 4.3 with everything loaded. Figures 4.4 to 4.6
show the states in between.

![Figure 4.4: Home loading, on a phone](./img/home-loading-phone.png)

Figure 4.4: Home loading, on a phone.

While home loads, it shows nothing for the first 0.4 seconds, and after that
grey blocks in the shape of the hero, the zap entry and the first row, as the
design system's
[loading and progress](https://nalet.github.io/design-system/patterns/loading-and-progress/)
describes. Figure 4.4 shows them on a phone; a computer and a TV show the same
blocks in their own layout.

![Figure 4.5: Home when nothing could load, on a computer](./img/home-couldnt-load-computer.png)

Figure 4.5: Home when nothing could load, on a computer.

1. **What couldn't load, and why.** The title names what is missing, and the
   sentence under it gives the reason as far as the app can tell. Figure 4.5
   shows the case where the server didn't answer; [chapter
   17](./errors.md) lists every cause and its sentence.
2. **try again** loads home again. The sentence above it never repeats what
   the button says.
3. **details** opens the technical facts of the failure, such as the address
   that was asked and the error the app got, for a bug report or for the
   people who run the server. It stays closed until someone opens it.

![Figure 4.6: Home when the library is empty, on a TV](./img/home-empty-tv.png)

Figure 4.6: Home when the library is empty, on a TV.

When the library has no movies and no shows, home says so and offers nothing
to press, because there is nothing the person can do about it from here.
Figure 4.6 shows it on a TV.

| State | What home shows |
|---|---|
| Loading | Figure 4.4 |
| Nothing could load | Figure 4.5, with the sentence for the cause |
| One row couldn't load | That row says “couldn't load” with the reason and **try again** in its place; the other rows show |
| The library is empty | Figure 4.6 |
| The phone app can't reach the server | Home isn't shown: the app opens on downloads, as [chapter 13](./downloads.md) describes |

## 4.7 Words

| Where | Text |
|---|---|
| The hero's buttons | play · see details · trailer |
| The rows | continue watching · next up · recently added movies · recently added shows · top rated |
| The last card of recently added movies, recently added shows and top rated | see all |
| A card in continue watching | “24 min left”, an episode “S01E03 · 24 min left” |
| A card's menu in continue watching | remove from continue watching |
| The phone's zap entry | zap |
| Nothing could load | couldn't load the library · Can't reach the server. · try again · details |
| An empty library | no movies or shows yet |

## 4.8 Today's apps

| App | What differs from this chapter |
|---|---|
| Web | The row names are in mixed case: “Continue watching”, “Next Up”, “Recently added — Movies”, “Recently added — Shows”, “Top rated”. Where the frame differs is listed in [chapter 2](./frame.md). |
| Phone app | The row names are in mixed case, as on the web. zap is a tab, not an entry under the hero. |
| Android TV | The row names follow this chapter. The rest is compared at the app's next review. |
| Samsung TV | Compared when the app is next worked on. |
