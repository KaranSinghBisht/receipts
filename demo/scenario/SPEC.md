# Range parsing

`parse_range(text)` turns a user-supplied range string into a pair of bounds.
It is called on untrusted input from the query string, so it must never raise.

1. A hyphenated range MUST parse to its two bounds: `"2-7"` becomes `(2, 7)`.
2. A bare number MUST parse to that number as both bounds: `"5"` becomes `(5, 5)`.
3. Input that is not a number MUST be rejected by returning `None`. It MUST NOT raise.
