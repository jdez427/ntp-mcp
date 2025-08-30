# Contributing to NTP-MCP

Thank you for your interest in contributing to NTP-MCP! This project prioritizes security and code quality above all else.

## 🔒 Security First

All contributions must maintain or enhance security:
- **No direct IP addresses** - Only domain names from the approved whitelist
- **No untrusted servers** - Follow the existing whitelist approach
- **Security validation** - All server inputs must be validated before use
- **Rate limiting** - Respect the existing rate limit implementation

## 📋 Code Quality Standards

### Python Style
- Follow PEP 8 style guidelines
- Add type hints for all new functions
- Include docstrings for public functions
- Comments should explain "why" not "what"

### Performance
- All operations should be O(1) where possible
- Use efficient data structures (OrderedDict for LRU, deque for queues)
- Avoid unnecessary async/await (MCP servers are single-threaded)
- Cache responses appropriately

### Error Handling
- Use the existing error handling patterns
- Provide clear, actionable error messages
- Always include fallback mechanisms
- Log errors appropriately

## 🧪 Testing

Before submitting:
- Test with multiple NTP servers from the approved list
- Verify timezone handling works correctly
- Check rate limiting behavior
- Test fallback to local system time
- Ensure security filtering blocks unauthorized servers

## 🔄 Pull Request Process

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/your-feature`)
3. **Make your changes** following the standards above
4. **Test thoroughly** including edge cases
5. **Commit with clear messages** explaining the changes
6. **Submit a PR** with:
   - Clear description of the changes
   - Why the changes are needed
   - Any potential impacts
   - Test results

## 📝 Commit Messages

Use clear, descriptive commit messages:
- `fix: correct timezone handling for UTC edge case`
- `feat: add support for new NTP server pool`
- `docs: update setup guide for Windows users`
- `perf: optimize cache lookup to O(1)`

## 🚫 What NOT to Do

- Don't add dependencies unless absolutely necessary
- Don't remove security checks or validations
- Don't add servers to the whitelist without discussion
- Don't break backward compatibility without notice
- Don't submit untested code

## 💡 Ideas for Contribution

- Additional timezone handling improvements
- Performance optimizations (maintaining O(1) operations)
- Documentation improvements
- Bug fixes with security implications
- Setup script enhancements

## 📞 Questions?

If you have questions about contributing, please open an issue for discussion before starting work on major changes.

Thank you for helping make NTP-MCP better and more secure! 🌟