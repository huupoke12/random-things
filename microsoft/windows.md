Open `cmd`: `Shift + F10`
# Windows 11

## Bypass system requirements
Set `DWORD` values at `HKEY_LOCAL_MACHINE\SYSTEM\Setup\LabConfig`:
* `BypassTPMCheck = 1`
* `BypassSecureBootCheck = 1`
* `BypassRAMCheck = 1`

## Bypass account requirement
Run `oobe\bypassnro`
