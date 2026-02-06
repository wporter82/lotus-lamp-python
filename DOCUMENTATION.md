# Documentation Guide

This document provides an overview of all documentation in the Lotus Lamp project.

## Quick Start

New to Lotus Lamp? Start here:
1. Read [README.md](README.md) - Overview and basic usage
2. Run `python -m lotus_lamp.setup` - Configure your lamp
3. Try the examples in [examples/README.md](examples/README.md)

## User Documentation

### Getting Started
- **[README.md](README.md)** - Main project documentation
  - Installation
  - Quick start
  - Basic usage examples
  - API reference
  - Troubleshooting

### Configuration
- **[CONFIGURATION.md](CONFIGURATION.md)** - Advanced configuration guide
  - Configuration file format
  - Multiple device management
  - Search order customization
  - Verbose mode
  - Project-specific configs
  - Environment variables

## Technical Reference

### Mode Reference
- **[docs/MODES.md](docs/MODES.md)** - Complete mode reference
  - All 213 animation modes
  - Mode categories
  - Mode numbers and names
  - Category organization

### Protocol Documentation
- **[docs/PROTOCOL.md](docs/PROTOCOL.md)** - BLE protocol specification
  - Command structure
  - UUIDs and services
  - Message formats
  - Response handling

### Examples
- **[examples/README.md](examples/README.md)** - Example scripts guide
  - Running examples
  - Example descriptions
  - Common patterns
  - Creating your own examples

## Developer Documentation

### Testing
- **[TESTING.md](TESTING.md)** - Testing guide
  - Running tests
  - Writing tests
  - Coverage reporting
  - Test organization
  - CI/CD setup


## Documentation Structure

```
lotus_lamp/
├── README.md                # Start here - main documentation
├── CONFIGURATION.md         # Advanced configuration
├── TESTING.md               # For contributors
├── DOCUMENTATION.md         # This file
│
├── docs/                    # Technical reference
│   ├── MODES.md            # Mode reference
│   └── PROTOCOL.md         # Protocol details
│
└── examples/                # Example scripts
    └── README.md           # Examples guide
```

## Finding What You Need

### "How do I...?"

**Get started?**
→ [README.md](README.md)

**Install and set up my lamp?**
→ [README.md#quick-start](README.md#quick-start-)

**Configure multiple lamps?**
→ [CONFIGURATION.md#managing-multiple-devices](CONFIGURATION.md#managing-multiple-devices)

**Use a specific animation mode?**
→ [docs/MODES.md](docs/MODES.md)

**Control brightness and speed?**
→ [README.md#api-reference](README.md#api-reference-)

**Run the tests?**
→ [TESTING.md](TESTING.md)

### "What is...?"

**The BLE protocol?**
→ [docs/PROTOCOL.md](docs/PROTOCOL.md)

**Mode 143?**
→ [docs/MODES.md](docs/MODES.md) (it's "W-R-W Flow")

**The configuration search order?**
→ [CONFIGURATION.md#search-order](CONFIGURATION.md#search-order)

### "I'm having issues with...?"

**Connection problems**
→ [README.md#troubleshooting](README.md#troubleshooting-)

**Configuration not loading**
→ [CONFIGURATION.md#troubleshooting](CONFIGURATION.md#troubleshooting)

**Tests failing**
→ [TESTING.md#troubleshooting-tests](TESTING.md#troubleshooting-tests)

**My lamp isn't listed**
→ Run `python -m lotus_lamp.advanced_scanner`

## Documentation Maintenance

### For Documentation Updates

When updating documentation:
1. **User docs** (README, CONFIGURATION, etc.) - Keep focused and practical
2. **Technical docs** (docs/) - Keep accurate and detailed
3. Update this file if structure changes

### Cross-References

When linking between documents:
- Use relative paths: `[link](../folder/file.md)`
- Include section anchors when helpful: `[link](file.md#section)`
- Test all links after major reorganizations

### Document Templates

**User Documentation:**
- Clear, concise language
- Practical examples
- Common use cases first
- Troubleshooting section

**Technical Documentation:**
- Precise, complete information
- Code examples
- Reference format
- Technical accuracy

## Contributing to Documentation

Documentation improvements are welcome!

### Types of Contributions
- Fixing typos and errors
- Clarifying confusing sections
- Adding examples
- Improving organization
- Translating to other languages

### Documentation Guidelines
1. **Be clear**: Use simple, direct language
2. **Be complete**: Include necessary context
3. **Be practical**: Show real examples
4. **Be current**: Keep information up-to-date
5. **Be organized**: Use logical structure

### Submitting Changes
1. Fork the repository
2. Make your documentation changes
3. Test all code examples
4. Check all links work
5. Submit a pull request

## Version History

This documentation structure established: 2026-02-06

Major updates:
- 2026-02-06: Consolidated user documentation
- 2026-02-06: Enhanced README with quick start
- 2026-02-06: Added comprehensive testing guide

## Questions?

- **Usage questions**: See [README.md](README.md) or open a discussion
- **Bug reports**: Open an issue
- **Documentation feedback**: Open an issue or pull request
