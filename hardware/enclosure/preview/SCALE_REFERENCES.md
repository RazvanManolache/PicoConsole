# Everyday size references

`size-and-depth.png` combines `everyday-scale.png` and `depth-scale.png`.
Each view uses one orthographic camera and one shared physical scene scale;
objects are never independently resized to make the console look smaller.
The two views have different camera framing. These images are not intended
to appear at actual physical size on an uncalibrated screen.

| Object | Model's outer dimensions | Reference |
|---|---|---|
| Pebble Mini | 64 × 34 × 22.8 mm body; 27.5 mm including joystick cap | Supplied STL geometry and [design dimensions](../dimensions.json) |
| Generic bank-card / ID-1 size reference | 85.60 × 53.98 × 0.76 mm; 3.18 mm corner radius | [Published ISO 7810 card specification, section 3.1.4](https://www.runt.gov.co/sites/default/files/normas/Resoluci%C3%B3n%201940%20de%202009%20MT%20adopta%20Ficha%20T%C3%A9cnica%20para%20elaboraci%C3%B3n%20de%20LT.pdf) |
| Stylised €1 coin | 23.25 mm diameter × 2.33 mm thickness | [European Central Bank coin specifications](https://www.ecb.europa.eu/euro/coins/common/html/index.en.html) |
| Generic AA battery | Maximum envelope 50.50 mm overall × 14.50 mm diameter | [Energizer E91 datasheet](https://data.energizer.com/pdfs/e91_max_na.pdf); actual cells vary within the listed limits |

The card, coin and battery are original simplified models created by
`render_scale.py`, without downloaded meshes, brand logos or copied coin face
artwork. Only their outer dimensions serve as measurement references. The
console uses the actual printable exterior meshes. Internal clearance helpers
are concealed; no exploded view is published.

The scale models are illustrative and are not included in the printable plates.
The AA battery does not fit inside this shell and is not its installed power
source. The hardware remains USB powered. The shell has not been printed or
physically fitted. Geometry and render composition are GPL-3.0-or-later;
the screen capture retains the credits linked in [reference/README.md](reference/README.md).
