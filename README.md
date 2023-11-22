# Enable NFC on Dell ControlVault2 and ControlVault3

## Introduction

Recent Dell laptops - i.e. E7470 - contain integrated Broadcom NFC (contactless), (contacted) chip card and fingerprint reader (USB 0a5c:5834 - Broadcom BCM5880 USH).

The contacted card reader works out of the box on Linux, yet NFC reader does not - no RF field is present.

Instructions from [blog.g3rt.nl](https://blog.g3rt.nl/enable-dell-nfc-contactless-reader.html) are not applicable: the ushdiag.exe does not recognize the device at all.

This project aims to enable Linux to read NFC cards the same way Windows does.

## Usage

1. Clone the repository.
1. Install python3 and python3-usb.
1. Run: `./nfc.py on` (use `sudo` if necessary).
1. Run `pcsc_scan` or whatever you prefer.
1. Enjoy!

To disable the reader replace `on` with `off`.

## Supported devices

Currently only the following devices were tested and are known to work:

* `0a5c:5832` (ControlVault 2),
* `0a5c:5834` (ControlVault 2),
* `0a5c:5842` (ControlVault 3).
* `0a5c:5843` (ControlVault 3).

Firmware update (done during driver installation on Windows) may be required.

## Tested on

* Dell Latitude 5310 2-in-1
* Dell Latitude 5480
* Dell Latitude 5491
* Dell Latitude 7280
* Dell Latitude 7290
* Dell Latitude 7390
* Dell Latitude 7400
* Dell Latitude E5270
* Dell Latitude E5570
* Dell Latitude E7470
* Dell Latitude E7490
* Dell Latitude Rugged 5414
* Dell Latitude Rugged 5420

## How it works?

Python script sends the same sequence of commands the Windows driver does. The traffic was sniffed using USBPcap and Wireshark (kudos to [~jkramarz](https://github.com/jkramarz) and [~lgarbarini](https://github.com/lgarbarini) and for that).

The data is sent as-is and responses are read, but no error-checking is done.

The semi-annotated traffic dumps are available as [traffic_cv2.txt](traffic_cv2.txt) and [traffic_cv3.txt](traffic_cv3.txt) - feel free to decode it further!

The communication protocol is based on NCI (NFC Controller Interface). Unfortunately the specs are not freely available and some proprietary extensions are used. libnfc-nci and kernel sources were used to decode vendor-independent structs.

## References

* https://android.googlesource.com/platform/external/libnfc-nci/ - the driver of NFC component (BCM 20795),
* https://blog.g3rt.nl/enable-dell-nfc-contactless-reader.html - this does not work on E7470.
