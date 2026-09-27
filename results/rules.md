# lexilint rule catalog

## LL101
- why: Long lines do not fit in side-by-side diffs, review panes, or terminals, which hides surrounding context from the reader.
- fix: Break the line at a natural boundary, extract a variable, or use parenthesized continuation lines.

## LL102
- why: TODO/FIXME markers are promises that live forever once committed. Anything worth doing should be a tracked task, not a comment.
- fix: Resolve it now, or move it to your issue tracker and delete the marker.

## LL201
- why: print() in library code sends output to stdout even when the module is imported by another program, corrupting pipelines and CLI output.
- fix: Use the logging module (logger.info/debug) or return the value to the caller.

## LL202
- why: A bare 'except:' also catches KeyboardInterrupt and SystemExit, and hides real bugs like NameError, making failures invisible.
- fix: Catch the specific exception you can handle, e.g. 'except ValueError:'.

## LL203
- why: A mutable default (list/dict/set) is created once at function definition and shared between every call, so state leaks between calls.
- fix: Use None as the default and create the container inside the body: 'def f(items=None): items = items or []'.

## LL204
- why: 'x == None' uses value equality; a class can override __eq__ and make the comparison lie. Identity (is) is the correct test for None.
- fix: Write 'x is None' or 'x is not None'.

## LL205
- why: Shadowing builtins like 'list' or 'sum' disables them for the rest of the scope, causing confusing TypeErrors far from the cause.
- fix: Rename the variable/function to something descriptive: 'items', 'total', ...

## LL206
- why: Concatenating strings with + creates an intermediate object per pair and reads poorly once more than two pieces are involved.
- fix: Use an f-string: f"hello {name}, you are {age}".
