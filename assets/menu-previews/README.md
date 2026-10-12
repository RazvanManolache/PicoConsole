# Menu preview artwork

Editable 112 x 32 monochrome PNGs derived only from the games in the curated
catalog. These are game-rendered graphics, not commercial cover art. Each image
retains the corresponding game's copyright and licence terms: see
`THIRD_PARTY_NOTICES.md`, `LICENSES`, and the per-game catalog records.

`provenance.json` records the selected capture, its SHA-256, source viewport,
framing method, tint, and PNG SHA-256. Captures are local development inputs;
the editable PNGs are the artwork sources included in the release archive.
Normal builds run `tools/prepare_previews.py` to losslessly pack these images.
They do not require a Pico, local screenshots, or an image-generation service.

The right side retains the complete playfield at its original aspect ratio.
A supplementary close-up emphasizes foreground detail when space allows.
Per-game capture/viewport choices avoid title screens, score-only regions,
and cropped-off boards. The artwork is tinted and darkened behind outlined
white game names by the launcher.

To import replacement development captures, run `prepare_previews.py --capture`.
Review the resulting artwork and provenance before committing it. The desktop
capture tools are development utilities and do not validate Pico hardware.
