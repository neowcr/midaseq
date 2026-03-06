# midaseq 
Converts a common MIDI file, to PS1 SEQ format! \
Essentially being a "midi2seq".

## Features
- Converts from multi-track MIDI file to PsyQ SEQ format
- Includes standard optimizations for reduced file size
- Lightweight and configurable settings

(DISCLAIMER: Midaseq only handles sequence data, not instruments or samples)

## Usage
1. First download the script or .exe version in the [Releases](https://github.com/neowcr/midaseq/releases) page.
2. If you're using the executable version, you can drag and drop a .mid file and it will automatically run the script with that file. /
If using the .py script, you first need [Python 3.0+](https://www.python.org/downloads) to be installed. Then you can either specify a file path when running the script, or put a file named "input.mid" in the same folder and it will detect automatically.
3. Before the conversion begins, you can specify certain configurations to customize the output, if desired.
4. You can then use the .seq file in many ways, including homebrew games using PsyQ, or generating a PSF file.

Some example guides can be found in the [wiki](https://github.com/neowcr/midaseq/wiki).

## Building from Source

If you have Python 3.0+ installed, get [PyInstaller](https://pyinstaller.org/en/stable/installation.html) and run build.bat if on Windows.
You can use PyInstaller to compile an executable on other platforms, since I don't have access.

## Credits
Thanks to these resources for SEQ format documentation:
- [LoveEmu](https://loveemu.hatenablog.com/entry/20060630/PSX_SEQ_Format)
- [VGMTrans](https://github.com/vgmtrans/vgmtrans)
