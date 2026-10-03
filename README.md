# Robot Arm and AI Control

Year2 source archive by dinhtri-dev. Original workspace files are unchanged.

## Contents and status

The Flask interface detects objects but its movement handlers update in-memory coordinates; they do not send a hardware command. ESP32/UNO firmware is a separate experiment. Network motor control is disabled by default until authorization and transport security are designed.

## Run / inspect

From application: python app.py. It starts on 127.0.0.1:5000. Camera/model availability is optional for viewing the UI; real inference needs the documented model.

Install only this project's listed dependencies in a separate virtual environment. Model binaries, large datasets, private configuration and generated output are excluded. Check DATA_AND_MODELS.md when present.

## Archive validation

See ARCHIVE_STATUS.md and SECURITY_REVIEW.md for the exact publication scope, tests and remaining limitations. A successful source-archive check does not certify production deployment, firmware flashing, model accuracy or CAD geometry.

## Future work

The consolidated Google document records project-specific fixes, missing functions and suggested features. This commit focuses on reproducible archiving, not implementing that roadmap.

## Directory guide

- `application`
- `firmware`
- `training`

## Python environment

Use Python 3.12 on Windows, from the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

`constraints.txt` pins the complete dependency resolution checked by OSV. Training dependencies are separate when `training/requirements.txt` is present. No model training is performed by archive checks. Other operating systems need their own dependency resolution and audit.

Place the optional detector at `application/models/best.pt`. The UI can display without a model; no motor command is sent by Flask.

## Local web scope

The demonstration binds only to `127.0.0.1:5000`. A per-process control token protects Socket.IO connections; local Host/Origin checks, validation and single-process rate limits are enforced. This is not a multi-user login service or production deployment. Changing the host or introducing a reverse proxy requires a new security review.

## Archived Wi-Fi firmware

The default firmware does not connect Wi-Fi or start HTTP. Network control is blocked at compile time when enabled: the prototype lacks deployment authorization/transport security, and older Arduino-ESP32 dependencies must be upgraded before enabling network code. See SECURITY_REVIEW.md. Serial experiments remain separate and have not been flashed or connected to hardware by archive QA.

## Tests actually run

Python source compiled without executing model training. app.py renders UI; app.py headers and nonce; app.py blocks foreign origin; app.py blocks nonlocal IP; app.py blocks rebinding host; app.py emits no session cookie; app.py rejects invalid socket token; app.py accepts local socket token; app.py rejects malformed socket payload; simulated coordinate movement; app.py socket rate limit; app.py HTTP rate limit.
4 complete firmware targets compiled with PlatformIO (build only, never upload).
