# CLI_REFERENCE

## Command Structure
Primary entrypoint: `python -m cli.main` (or project wrapper script).

Top-level command groups include:
- `install`
- `status`
- `policy`
- `personal`
- `backup`
- `claude`
- `aion` (service-oriented subcommands)

## Usage
```bash
python -m cli.main --help
python -m cli.main status --help
python -m cli.main backup --help
```

## Flags and Examples
```bash
python -m cli.main install --help
python -m cli.main policy --help
python -m cli.main aion --help
```

## Debug Mode
Use environment verbosity flags/log-level options supported by each command group and service.

## Development Commands
- run help per command for exact options
- pair CLI actions with control-plane health checks
- use local compose profiles for integration testing
