# Flawed-source lint reports

## C1 — The Chatty Ingestor
- line 7: LL202 bare except: catches KeyboardInterrupt/SystemExit and hides bugs
- line 8: LL201 print() call in library code; use logging or return values
- line 8: LL206 string built with +; prefer an f-string for clarity and speed
- line 9: LL201 print() call in library code; use logging or return values
- line 9: LL206 string built with +; prefer an f-string for clarity and speed

## C2 — The Shared Basket
- line 1: LL203 mutable default for parameter 'items': the object is shared across all calls
- line 2: LL204 comparison to None with ==; use 'is  None'

## C3 — The Broken Aggregator
- line 1: LL205 assignment shadows builtin 'sum'
- line 3: LL102 unresolved TODO/FIXME marker left in source
- line 8: LL206 string built with +; prefer an f-string for clarity and speed

## C4 — The Wild Formatter
- line 2: LL102 unresolved TODO/FIXME marker left in source
- line 5: LL101 line is 123 characters (max 88)
- line 5: LL206 string built with +; prefer an f-string for clarity and speed
- line 5: LL206 string built with +; prefer an f-string for clarity and speed
- line 5: LL206 string built with +; prefer an f-string for clarity and speed
