# PicoDash Development Guidelines

## Commands
- `make help` - Display available commands
- `make install-tools` - Install required Python tools
- `make upload PORT=/path/to/port` - Upload all files to Pico
- `make upload-main PORT=/path/to/port` - Upload only main files
- `make upload-lib PORT=/path/to/port` - Upload only library files
- `make list PORT=/path/to/port` - List files on the Pico
- `make connect PORT=/path/to/port` - Connect to the Pico REPL
- `make reset PORT=/path/to/port` - Reset the Pico

## Code Style
- Use docstrings (""") for module/function documentation
- Follow PEP 8 naming conventions (snake_case for variables/functions)
- Group imports: standard library first, then third-party, then local
- Use constants for configuration values at the top of the file
- Use meaningful variable names and avoid abbreviations
- Handle exceptions with specific error messages
- Implement proper error handling and display error messages on screen
- Use classes for organizing related data and functionality
- Add comments for complex logic but avoid redundant comments

## Development Practices
- Test changes in the emulator before uploading to hardware
- Minimize memory usage (free memory with gc.collect() when possible)
- Use global constants for hardware pins and configuration values
- Keep power consumption in mind (use sleep to save power)
- Format all string output with f-strings
- Handle WiFi connectivity issues gracefully
- Follow existing module structure in lib/ directory