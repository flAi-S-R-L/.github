# .github

Public profile of the flAi organization: the page
[github.com/flAi-S-R-L](https://github.com/flAi-S-R-L) shows `profile/README.md`.

## Logos

- `assets/flai-logo.png` and `assets/flai-logo-dark.png`: logo at the top of the profile, for
  light and dark theme.
- `assets/avatar.png`: the organization avatar. GitHub has no API for it: upload it by hand in
  Settings → Profile → Profile picture.

## Partner carousel

`profile/partners.svg` is generated, do not edit it by hand. To add or change a partner:

1. Put the logo PNG in `assets/partners/`.
2. Add it to `PARTNERS` in `scripts/build_partners_carousel.py`.
3. Run `python scripts/build_partners_carousel.py` (needs Pillow) and commit the new SVG.
