# Current hardware

## Observed on 2026-10-11

- USB device: RP2350 Boot; USB VID 2E8A, PID 000F.
- BOOTSEL volume: F:, label RP2350.
- INFO_UF2.TXT: Model Raspberry Pi RP2350; Board-ID RP2350.
- User identifies the board as a Pico 2 with a Waveshare Pico-LCD-1.3 attached.
- User confirms no microSD adapter is connected.
- Native firmware loaded successfully; running USB CDC device is VID 2E8A, PID 0009, COM3.
- User confirmed the menu looks right and the physical joystick works.
- The curated pack uses shared game RAM and scanline output; current count and USB results are in docs/NATIVE_PACK.md.
- Full physical gameplay, every individual button and actual flash capacity have not been verified.

The bootloader confirms RP2350, but does not by itself identify the exact carrier or flash
capacity. Plan for the official Pico 2's 4 MiB flash / 520 KiB RAM until read out.
The bootloader's approximately 128 MB virtual drive does not represent physical flash.

## Waveshare Pico-LCD-1.3 wiring

From the downloaded manufacturer's
`upstream/waveshare-pico-code/python/Pico-LCD-1.3/Pico-LCD-1.3.py`.
GPIO numbers below are **GP numbers**, not physical header numbers.

| Function | GPIO |
|---|---:|
| ST7789 SCK, SPI1 | GP10 |
| ST7789 MOSI, SPI1 | GP11 |
| ST7789 CS | GP9 |
| ST7789 DC | GP8 |
| ST7789 reset | GP12 |
| Backlight PWM | GP13 |
| Joystick up | GP2 |
| Joystick down | GP18 |
| Joystick left | GP16 |
| Joystick right | GP20 |
| Joystick press | GP3 |
| A | GP15 |
| B | GP17 |
| X | GP19 |
| Y | GP21 |

Display: 240 x 240, ST7789, RGB565 over SPI. Inputs: active low with pull-ups.
One RGB565 frame occupies 115,200 bytes (112.5 KiB); two occupy 225 KiB.
Use a single buffer, dirty regions or scanline output where emulator memory requires it.
Start with conservative SPI speed and the Pico 2's normal 150 MHz clock; upstream
overclock settings are not automatically suitable for this board.

Suggested GB/NES mapping: joystick directions = D-pad, A/B = A/B, X = Start,
Y = Select, joystick press = menu. Require a long press or chord for exit to avoid
accidental loss of gameplay. Native games can use all four face buttons.

This display board provides no SD slot or speaker. A battery/charging circuit is also
needed for untethered use later; USB power is sufficient for initial development.

Primary references:
- https://www.waveshare.com/product/pico-lcd-1.3.htm
- https://github.com/waveshare/Pico_code
- https://www.raspberrypi.com/products/raspberry-pi-pico-2/
