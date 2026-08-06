# Binary safety: why this needed a real fix, not a workaround

The rewrite backend transforms a `git fast-export` stream, applies
identity/trailer changes, and feeds the result to `git fast-import`. A
fast-export stream is not text. A `data <N>` block — a blob, a commit
message, a tag message — is exactly N raw bytes, and for a blob that can
be arbitrary binary content: not guaranteed valid UTF-8, not guaranteed to
respect anything that looks like a line boundary.

## What actually broke, twice, in this exact order

**First**: decoding the whole stream as UTF-8 text. Crashes
(`UnicodeDecodeError`) the instant a repo has real binary content in it —
a `.skill` zip archive, an image, anything. Fixed by switching the entire
pipeline to operate on `bytes` end to end.

**Second**, after the bytes fix, on a real 93-commit repository with real
binary archives: `fast-import: Unsupported command`. The bytes fix wasn't
enough by itself. The original code (both before and immediately after
the bytes conversion) read a blob's `data <N>` content by pre-splitting
the whole stream into "lines" and then scanning forward until it hit
something that looked like a blank line, treating that as the end of the
block. That works by luck on small text content and is wrong by
construction for binary content: a blob's own bytes can easily contain a
sequence that looks like a blank line, which truncates the blob early and
desynchronizes every byte that follows it for the rest of the stream.

The fix was architectural, not a patch: the parser now walks the stream
with an explicit byte cursor (`_take_line`, `_peek_line`,
`_take_data_block`) instead of pre-splitting into lines at all. A `data
<N>` block is *always* consumed by exactly N bytes from the cursor, never
by scanning for a stop condition. This is the only way to make the
byte-exact contract `fast-import` depends on actually hold.

A related, more subtle version of the same class of bug: a "courtesy"
extra newline appended after content that didn't already end in one, on
the theory that it made the output tidier. It doesn't — it silently
changes what follows the declared byte count by one byte, without
updating the count. Removed entirely. A `data <N>` header's declared
length is the whole contract; nothing gets padded onto it, ever.

## How this is actually tested, not just asserted

1. **Empty-plan passthrough**: transforming a real repo's full
   `fast-export` stream through a plan with zero merges and zero removals
   must produce output byte-identical to the input. This is the strongest
   possible check — any difference at all, in an operation that's
   supposed to change nothing, is a bug.
2. **Tree-hash sequence**: `git log --topo-order --format='%T|%s'` before
   and after a real (non-empty) rewrite must match exactly. Tree/blob
   content is independent of commit metadata, so an identity-only rewrite
   changing anything here means content was touched when it shouldn't
   have been.
3. **Per-file content hash across all of history**: every historical
   version of every binary file, hashed and compared before and after,
   independent of commit SHA (which legitimately changes when author
   metadata is rewritten).
4. **`git fsck --full`**: zero errors.
5. Tested first against a synthetic repo built specifically to contain
   binary content likely to break a line-based parser (byte sequences
   matching Python's/YAML's extended line-boundary set: `\x0b`, `\x0c`,
   `\x1c`-`\x1e`), then against a disposable clone of a real repository
   with real `.skill` zip archives across 93 real commits, before ever
   running against the real repository itself.

If you're extending the rewrite pipeline: any change to how a `data <N>`
block is read or written needs to re-run check #1 above at minimum. It's
cheap, it's the strongest signal available, and it would have caught both
bugs described here immediately.
