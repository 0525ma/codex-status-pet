# Architecture and operational boundaries

1. **Existing upstream agent** obtains quota via the locally authenticated Codex app server and attaches to the existing local desktop transport.
2. **Patch adapter** adds an original renderer and the status companion to that agent. The patch checks expected anchors before writing an output. Unknown upstream layouts are rejected.
3. **Event bridge** reads the local `state_5.sqlite` and bounded JSONL tails. Only normalized chat names, event classification, and timestamps are emitted. The original-message field is never used as a display title.
4. **Guardian** checks background jobs, installed resources, and loopback transport. `transport_ready` is distinct from a visually confirmed mount. It never quits the active Codex client to repair a missing port.
5. **Optional updater** uses the existing upstream verifier. The downloaded release is verified before local customization is applied in a staging directory. Only a preflighted candidate is passed to the upstream installer; a backup is retained.

Quota percentages are account-window values, not per-chat token usage. The guardian does not call a model, purchase credits, or consume quota reset credits. Automatic upgrades are opt-in and limited to compatible stable upstream badge releases. No real-time webhook or guaranteed instant feature notification is provided.

Supported baseline: upstream macOS 0.9.4, Node 24+, Python 3.9+. Installation refuses an already-customized private Grok agent. The public installer does not replace the user's native ChatGPT Pets selection.

The UI uses host DOM selectors and a local attachment channel rather than a stable official sidebar SDK. Client upgrades may require a new adapter. Preserve fail-closed patch behavior and report missing transport instead of reporting a healthy UI from a live process alone.
