[简体中文](RELEASE_v0.3.3-ai-dev1.zh_CN.md) · **English**

# NABO Toolkit v0.3.3-ai-dev1

This experimental candidate adds a default AI assistant shortcut group immediately before Typeless. UP sends F13 for Codex, DOWN sends F14 for Claude, and OK sends F15 for Grok Bot. The badge is a keyboard: install and run the [desktop bridge](../desktop-bridge/README.md) to open those apps. Confirm the chat input has focus, hold OK to switch to Typeless, and trigger your own Typeless shortcut manually. Hold DOWN to return to AI助手. The first long OK on a dark screen wakes it without changing groups.

The firmware ZIP includes the bridge source and bilingual setup instructions in `desktop-bridge/`, as well as the offline configurator. No account, personal configuration, compiled desktop executable or device data is included.

Existing saved shortcut groups and cards are not replaced by a firmware upgrade. Read the badge's configuration in the updated configurator and explicitly add AI助手; a full six-group configuration must be adjusted manually. The original five groups, NABO artwork, offline voice navigation and other tools remain.

The exact new application was installed and verified on the author's badge. With the retained personal configuration, the user confirmed all three Mac assistant launches, a Typeless input and returning to the assistant group. Fresh-install defaults have host coverage but were not separately tested on a reset badge. The Windows bridge has not been run or device-tested; automatic focus depends on the target application's accessibility support.

## Exact candidate

- Application: 2,031,008 bytes; SHA256 `b86665d923123d7d88470cc099637cf2afd61a76f3e0776d92560a4f4d956906`.
- Merged image: 2,096,544 bytes; SHA256 `8f189aa0272dee08342bb37f6379821a730efe665e2e1e1174b81641903b66a3`.
- ESP-IDF 6.0.2; host suite and archive verification passed. The 1,984 KiB legacy application partition has only 608 bytes remaining.

The community merged image is a **full installation at 0x0**, replacing the partition table and potentially resetting settings, bonds and personal templates. Its full-install path has not been tested on hardware. For retaining data use only a separately authorized guarded application-only upgrade to `0x10000`, after checking device identity, security state, the exact partition table and erase boundary. The guarded installer recognizes the project's default layout, the measured legacy Adventure layout, and the exact Words layout with separate `record` and `assets` partitions; it rejects other layouts. An application-only install must not be flashed at `0x0`.
