# Input and output contract

Supply a local non-link directory, an image reference ending @sha256: plus 64 lowercase hexadecimal characters, and an explicit command JSON array. The returned argv is inert data. It does not install Docker, pull the image, launch a process, collect a filesystem diff, or capture egress. An operator must run any approved plan in their own disposable, isolated environment with a watchdog. Do not mount home directories or host sockets.

Exit codes: 0 scoped PASS or generated data; 1 FIX; 2 BLOCKED; 3 PARTIAL. Static audits deliberately return PARTIAL. Reports retain the same schema across hosts.
