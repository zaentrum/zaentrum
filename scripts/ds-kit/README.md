# The design system in the spec's drawings

The chino specification's drawings (`spec/chino/img/ch*.html`) draw the nalet
design system's components exactly as the package renders them. Two files carry
the package into the drawings, and this folder makes both from the package
itself:

- `spec/chino/img/ds/nalet-<version>.css`: the package's tokens and component
  stylesheet, copied unchanged. `spec/chino/img/screens.css` imports it.
- `spec/chino/img/ds.js`: the short `<ds-*>` tags the drawings write
  (`<ds-button variant="primary" icon="play">play</ds-button>`), each expanded
  to the markup the package's React component renders. Its header lists every
  tag. `frame.js` expands them before it draws the frame.

## Making them again, for a new release

1. Put the release's tarball URL in `package.json`, as the design system's
   releases are installed (never from a registry).
2. Install and capture. `capture.cjs` renders every component of `catalog.jsx`
   with the real package and React 18 in a browser, opens the menus, and saves
   the markup to `out/catalog-markup.json` and a picture of all of it to
   `out/catalog.png`; it also writes the stylesheet's copy.

   ```sh
   cd scripts/ds-kit
   npm install
   PLAYWRIGHT=<path to an installed playwright> node capture.cjs
   ```

3. Make ds.js from what was captured, then draw every figure again and compare
   them with `out/catalog.png`:

   ```sh
   python3 gen-ds.py out/catalog-markup.json ../../spec/chino/img/ds.js
   cd ../.. && node scripts/render-mockups.mjs chino
   ```

`gen-ds.py` holds the templates. The fixed pictures (chevrons, check marks,
state glyphs, illustrations) are copied byte for byte from the capture, and the
loader is drawn by the package's own formula. A component the catalog doesn't
render yet goes into `catalog.jsx` first, so its markup is always the
package's, never a guess.

## What isn't the design system's

Two parts of the drawings are chino's additions, until the design system has
them: an empty state's **details** (the banner's own toggle and block, class
`kit-details` in screens.css), and the frame of chapter 2. Chapter 1 of the
specification lists what is chino's own and what the design system doesn't
have yet.
