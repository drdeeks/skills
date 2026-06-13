# Debug Tracer Tools

## Built-in Debuggers

| Tool | Language | Usage |
|------|----------|-------|
| pdb | Python | `python -m pdb script.py` |
| node inspect | Node.js | `node inspect script.js` |
| gdb | C/C++ | `gdb ./program` |

## IDE Debuggers

| IDE | Debugger | Features |
|-----|----------|----------|
| VS Code | Built-in | Breakpoints, watches, call stack |
| PyCharm | Professional | Remote debugging, profiling |
| Chrome DevTools | Browser | DOM inspection, network |

## Logging Frameworks

| Framework | Language | Features |
|-----------|----------|----------|
| Python logging | Python | Levels, handlers, formatters |
| Winston | Node.js | Transports, formatting |
| Serilog | .NET | Structured logging |

## Performance Profiling

```bash
# Python cProfile
python -m cProfile -s time script.py

# Node.js profiling
node --prof script.js
node --prof-process isolate-*.log
```
