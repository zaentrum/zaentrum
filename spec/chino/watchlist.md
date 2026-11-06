# 8 Watchlist and lists

> **Not in the new form yet.** This chapter's figures show the target, not
> what is deployed today. Where today's apps differ, its “Today's apps”
> section says so. The screens as deployed and the numbered changes follow,
> as [chapter 11](./playback.md) already has them.

This chapter specifies the watchlist: the Watchlist, the list every account
has, and the lists people make of their own, with how a list is created,
renamed and deleted. A title goes into a list on its page, with the add-to-list
control of [chapter 6](./title-actions.md). The frame around the view is
specified in [chapter 2](./frame.md).

## 8.1 Purpose

The watchlist keeps what people mean to watch, and lets them sort it into
lists of their own, such as one for Sunday nights or one for the kids.
**watchlist** in the frame opens it. The view is named after the list it
starts with, the Watchlist, and shows every list as a row; a list opens on its
own with all of its titles.

## 8.2 The watchlist on a computer

Figure 8.1 shows the watchlist on a computer, with the Watchlist and a list
called Sunday nights.

![Figure 8.1: The watchlist on a computer, at 1280 × 800](./img/watchlist-computer.png)

Figure 8.1: The watchlist on a computer, at 1280 × 800.

1. **create list** starts a list of the person's own (section 8.6.1).
2. **The row's name**: the list's name and how many titles it holds,
   “Watchlist · 5”. Choosing it opens the list (section 8.5).
3. **A card**, as in movies and shows ([chapter 5](./browse.md)), with its
   status marks. An episode shows as its show's card, with the episode under
   the name: “S01E03 · Llamigos”. Choosing it opens the show's page on that
   episode ([chapter 6](./title-actions.md)).
4. **see all**, the row's last card, opens the list, as the row's name does.
5. **A list of the person's own** follows the Watchlist, in a row of its own.
   The bookmark on a card means the Watchlist in every row, so Elephants Dream
   carries it in Sunday nights too.

The Watchlist's row comes first, then the person's lists in the order they
were created. A row holds the 12 titles added last, the newest first.

## 8.3 The watchlist on a phone

Figure 8.2 shows the same view on a phone. The parts are those of figure 8.1;
the numbers mark where the phone differs.

![Figure 8.2: The watchlist on a phone, at 360 dp](./img/watchlist-phone.png)

Figure 8.2: The watchlist on a phone, at 360 dp.

1. **create list** stays at the end of the heading's line, in reach without
   scrolling past the lists.
2. **The rows** come one under the other, as on a computer.
3. **A row** shows two cards and a part of the next, so it's plain that it
   goes on sideways.

The web on a phone has the layout of figure 8.2, with its own tabs
([chapter 2](./frame.md)).

## 8.4 The watchlist on a TV

Figure 8.3 shows the watchlist on a TV, with the focus on the first card.

![Figure 8.3: The watchlist on a TV, at 960 × 540 dp](./img/watchlist-tv.png)

Figure 8.3: The watchlist on a TV, at 960 × 540 dp.

1. **The focus** on a card, the ring 2 dp outside the poster and the card 5 %
   larger. Right from the rail lands on the first card of the Watchlist's row.
   Left and right move along a row, up and down from row to row; a row's name
   takes the focus too, and OK on it opens the list.
2. **A row runs past the safe area** to the edge of the screen, as home's rows
   do ([chapter 4](./home.md)). The row scrolls when the focus reaches the
   outline, so the focus never leaves it.
3. **create list**, at the top inside the safe area. Up from the first row
   reaches it.

## 8.5 A list

Figure 8.4 shows one of the person's lists, Sunday nights, opened from its
row.

![Figure 8.4: A list on a computer: Sunday nights](./img/watchlist-list-computer.png)

Figure 8.4: A list on a computer: Sunday nights.

1. **The back arrow** returns to the watchlist. The heading is the list's name
   as the person wrote it, and the line under it counts its titles:
   “4 titles”, “1 title”.
2. **rename list** and **delete list** (section 8.6). delete list has the
   design system's amber outline, as every action that deletes has.
3. **The grid** holds all of the list's titles, the one added last first, laid
   out as the grid of movies ([chapter 5](./browse.md)).

The Watchlist opens the same way, without rename list and delete list. It is
the list every account has, and the bookmark on every title's page and every
card's mark refer to it by name ([chapter 6](./title-actions.md)), so it
keeps its name and can't be deleted.

A title leaves a list on its page: the bookmark takes it out of the
Watchlist, and the list picker out of the person's own lists
([chapter 6](./title-actions.md)). Back from the page, the list shows without
it, scrolled as it was.

## 8.6 Creating, renaming and deleting a list

### 8.6.1 Creating a list

Figure 8.5 shows the dialog that **create list** opens, after the person tried
a name they already use.

![Figure 8.5: Creating a list, with a name already taken, on a computer](./img/watchlist-create-computer.png)

Figure 8.5: Creating a list, with a name already taken, on a computer.

1. **Name** takes the list's name. It is checked when the person presses
   create list, not while they type. A name already in use gets “You already
   have a list called Sunday nights.” under the field, in red, and an empty
   one “Give the list a name.”; the field keeps what was typed, and the focus
   goes back to it.
2. **create list** creates the list and closes the dialog, and the list's row
   appears at the end of the watchlist, empty. Enter in the field does the
   same. **cancel**, Esc or a press beside the dialog closes it, and nothing is
   created.

The list picker on a title's page ([chapter 6](./title-actions.md)) starts a
list with the same dialog, and the title goes into the new list at once. On a
TV, the name is typed on the keyboard that search uses ([chapter 9](./search.md)),
under the field.

### 8.6.2 Renaming a list

**rename list** opens the same dialog, headed **rename list**, with the list's
name in the field and **rename list** to confirm. The new name shows at once,
in the list's row and in the list picker.

### 8.6.3 Deleting a list

Deleting asks first, because a deleted list can't be brought back. Figure 8.6
shows the question.

![Figure 8.6: Deleting a list, on a computer](./img/watchlist-delete-computer.png)

Figure 8.6: Deleting a list, on a computer.

1. **What goes, and what stays**: “This deletes Sunday nights and can't be
   undone. Its 4 titles stay in the library and in your other lists.” A list
   of one title says “Its title stays in the library and in your other
   lists.”, and an empty list leaves the second sentence out.
2. **delete list**, with the amber outline, repeats the dialog's title.
   **cancel** comes first and takes the focus, so a stray Enter or OK deletes
   nothing.

After the delete, the watchlist shows again without the list's row, and on a
TV the focus is on **create list**.

### 8.6.4 Names and limits

- A name has 1 to 60 characters, and spaces at its ends are left out. The
  field takes no more than 60.
- No two of an account's lists share a name, whatever the capitals:
  “sunday nights” is taken while there is a Sunday nights.
- An account has at most 50 lists, the Watchlist among them. Past that, the
  dialog says so at its top: “You have as many lists as an account can have.
  Delete one first.”
- A save that fails for another reason keeps the dialog open with what was
  typed, and says why at its top: “Couldn't create the list.” or “Couldn't
  rename the list.”, then the cause's sentence of [chapter 17](./errors.md).

### Open

- **Renaming the Watchlist.** The server lets the Watchlist be renamed, and the
  web and both TV apps offer it, while this chapter and the phone app keep its
  name, because the bookmark and its names for screen readers, “add to
  Watchlist” and “in your Watchlist”, call it so. Recommendation: keep the
  name, and have the server refuse to rename the Watchlist.

## 8.7 What a list holds

- A list holds movies, shows and episodes, the one added last first, and a
  title can be in several lists at once.
- The count beside a row's name and under a list's heading counts the titles
  the list holds.
- The lists belong to the account, so they are the same in every app: a title
  added on a phone is in the watchlist on the TV.

## 8.8 States

The watchlist is drawn in figures 8.1 to 8.4 with everything loaded. Figures
8.7 and 8.8 show two of the states in between.

![Figure 8.7: An empty watchlist, on a phone](./img/watchlist-empty-phone.png)

Figure 8.7: An empty watchlist, on a phone.

1. **nothing in your Watchlist yet**: the design system's nothing-yet state,
   when the Watchlist is empty and the person has no list of their own.
2. **Where titles come from.** The sentence names the bookmark on a title's
   page. There is nothing to press here, because a title is added on its
   page; **create list** stays, for a list of the person's own.

![Figure 8.8: The watchlist when the lists couldn't load, on a TV](./img/watchlist-couldnt-load-tv.png)

Figure 8.8: The watchlist when the lists couldn't load, on a TV.

1. **What couldn't load, and why.** “couldn't load your watchlists”, and the
   reason under it; here the server didn't answer. [Chapter 17](./errors.md)
   lists every cause and its sentence.
2. **try again** takes the focus first and loads the lists again. create list
   comes back with them.

| State | What the watchlist shows |
|---|---|
| Loading | Nothing for the first 0.4 seconds, then grey blocks in the shape of two rows, a name over a line of posters, like the blocks of figure 5.5 ([chapter 5](./browse.md)) |
| The Watchlist empty, and no list of the person's own | Figure 8.7 |
| The Watchlist empty beside other lists | Its row says “Add titles with the bookmark on a title's page.” in place of its cards |
| A list of the person's own that is empty | Its row says “Add titles with the arrow beside the bookmark on a title's page.” in place of its cards; opened, the list shows “nothing in Sunday nights yet” over the same sentence |
| The lists couldn't load | Figure 8.8, with the sentence for the cause |
| One row couldn't load | That row says “couldn't load this list”, the reason and **try again** in place of its cards; the other rows show |
| An opened list couldn't load | “couldn't load this list”, the reason and **try again** under the heading |
| Asking again failed | The watchlist stays as it was, under the warning banner of [chapter 17](./errors.md): “Couldn't refresh your watchlists; it shows what was loaded 4 minutes ago.”, with **try again** |
| The list was deleted on another device | The list's view goes back to the watchlist, which no longer has its row |
| The phone app can't reach the server | The banner of [chapter 13](./downloads.md), with the lists the phone loaded under it as they were; with none, figure 8.8 without the sentence, which the banner already says |

## 8.9 Words

| Where | Text |
|---|---|
| The view | watchlist · create list |
| A row's name | Watchlist · 5 · Sunday nights · 4 |
| The last card of a row | see all |
| A card | the name and the year; an episode: the show's name and “S01E03 · Llamigos” |
| An empty row | Add titles with the bookmark on a title's page. · Add titles with the arrow beside the bookmark on a title's page. |
| A list | the back arrow, named “back” for screen readers · Sunday nights · 4 titles · 1 title · rename list · delete list |
| Creating and renaming | create list · rename list · Name · cancel |
| A name the dialog can't take | Give the list a name. · You already have a list called Sunday nights. |
| At the dialog's top | You have as many lists as an account can have. Delete one first. · Couldn't create the list. · Couldn't rename the list. · and the cause's sentence |
| Deleting | delete list · This deletes Sunday nights and can't be undone. Its 4 titles stay in the library and in your other lists. · Its title stays in the library and in your other lists. · cancel |
| Empty | nothing in your Watchlist yet · Titles you add with the bookmark on a title's page show up here. · nothing in Sunday nights yet |
| Couldn't load | couldn't load your watchlists · couldn't load this list · Can't reach the server. · try again |
| Asking again failed | Couldn't refresh your watchlists; it shows what was loaded 4 minutes ago. · try again |

## 8.10 Today's apps

| App | What differs from this chapter |
|---|---|
| Web | “new list” follows the rows and opens a name field in place of a dialog, with “List name” as its placeholder and icon buttons to create and to cancel; an empty name says “Enter a name”, and a name the server refuses says “request failed (409)”. A list has icon buttons to rename it in place, the Watchlist too, and to delete it; deleting asks with the browser's own question, “Delete "Sunday nights"? Its items will be removed from the list.” A saved episode's card is named after the episode, not its show. An empty row says “Save titles with the + button on any movie or show.”, an empty list “This list is empty.” and “Add titles from a movie or show page to see them here.” While the lists load, a spinner turns. |
| Phone app | The heading is “Watchlist”, and “New list” follows the rows. The dialogs are “New list” with “Create” and “Rename list” with “Save”, the field's placeholder “List name”, the confirming button greyed out until the name fits. A refused name says “A list with that name already exists.”, “You've reached the maximum number of lists.” or “Enter a name between 1 and 60 characters.”, any other failure “Couldn't save the list. Try again.” Deleting asks “Delete “Sunday nights”?” with “This removes the list and everything in it. Titles stay in your other lists.” and a red “Delete”. A list counts its titles as “· 4” beside its name, and an empty one says only “Add titles with the bookmark on a movie's or a show's page.”, or for a list of the person's own “Add titles with the arrow beside the bookmark on a movie's or a show's page.” An empty row says “Save titles with the + button on any movie or show.” A spinner turns while the lists load. |
| Android TV | The heading is “your lists”, with “new list” beside it. A list has “back”, “· 4” beside its name, and “rename list” on every list, the Watchlist too. The name dialog is “new list” or “rename list”, with “List name…” in the field, “Press the on-screen Done key to save, BACK to cancel.” under it and the system's keyboard; a name the server refuses closes the dialog with nothing said. Deleting says ““Sunday nights” is deleted, with the 4 titles saved in it. They stay in the library and in your other lists.” An empty list says ““For the kids” is empty. Save titles with the + button on any movie or show.”, and “4 saved” stands under a list's grid. While the lists load, “Loading your lists…” stands in the middle. |
| Samsung TV | The heading is “Your lists”, with “New list” beside it, and the Watchlist's row carries a “DEFAULT” label. Names are typed on a keyboard that covers the screen, headed “New list” or “Rename list”. A list has “Back”, “Rename”, the Watchlist too, and “Delete”, which deletes at once without asking. Failures say “Couldn't create that list.”, “Couldn't rename that list.”, “Couldn't delete that list.” and “Couldn't load your lists.” Empty rows say “Save titles with the + button on any movie or show.”, an empty list ““For the kids” is empty. Save titles with the + button on any movie or show.” |
