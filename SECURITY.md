# Security and privacy

- Attachment uses the upstream extension's loopback-only desktop debugging transport. Do not bind it to a LAN/public interface or forward it remotely. A debugging transport grants substantial local-client access; this addon is intended for a trusted local account.
- No authentication file, API key, access token, private key, or conversation snapshot is packaged or uploaded.
- The event reader reads local task metadata and recent event records. It classifies event types and tool names; raw arguments and conversation bodies are not emitted or logged by the bridge.
- Normalized task names can still be personal. The bridge is a local child-process stream, not a public API.
- Automatic upstream updates validate download metadata and archive contents, then preflight the local patch. A checksum is not a guarantee that every future behavior is safe; opt in only if you trust the named upstream project.
- The launcher refuses to quit an active client. Recovery never disables signing, authentication, sandboxing, or OS access controls.

Report suspected leaks privately through GitHub's private vulnerability reporting if enabled. Do not paste credentials or private rollouts into public issues.
