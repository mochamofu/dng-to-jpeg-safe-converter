# Contributing

Bug reports, camera compatibility reports, translations, and pull requests are welcome.

## Before opening an issue

- Never attach private photos unless you intentionally want to publish them.
- Remove GPS and personal metadata from any sample file you share publicly.
- Include the app version, Windows version, camera model, and the exact log message.
- State whether the issue reproduces in the 10-file test.

## Development

1. Install Python 3.9 or newer.
2. Run `scripts/run.bat` once to create the local environment.
3. Run tests with `.venv\Scripts\python.exe -m unittest discover -s tests -v`.
4. Keep source DNG handling read-only and never add automatic source deletion.
5. Do not add telemetry, cloud upload, or metadata transmission without an explicit opt-in design discussion.

By submitting a contribution, you agree that it may be distributed under GPL-3.0-only.

