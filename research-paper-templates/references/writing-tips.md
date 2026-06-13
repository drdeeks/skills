# Research Paper Templates - Writing Tips

## General Writing Guidelines

### Structure
- Follow the conference template exactly
- Use provided macros and environments
- Keep main text within page limits
- Move detailed proofs to appendix

### Citations
- Never hallucinate citations
- Verify every citation programmatically
- Use `[CITATION NEEDED]` for unverifiable claims
- Organize related work by methodology, not paper-by-paper

### Figures and Tables
- Use vector graphics (PDF) for all plots
- Colorblind-safe palettes (Okabe-Ito or Paul Tol)
- Self-contained captions
- Bold best values in tables
- Include direction symbols (↑/↓)

### LaTeX Best Practices
- Balance `$` signs for math mode
- Match `\ref` with `\label`
- No fabricated citations
- Every `\begin{env}` has matching `\end{env}`
- Escape underscores outside math: `\_`
- No duplicate labels or section headers
- Numbers in text must match actual results

## Conference-Specific Tips

### NeurIPS/ICML
- 9/8 page limit + unlimited appendix
- Broader impact statement required
- Reproducibility checklist

### ICLR
- OpenReview format
- Mandatory LLM disclosure
- Strong emphasis on reproducibility

### ACL
- 8 page limit + unlimited appendix
- Ethics statement required
- Datasheets for datasets

### AAAI
- 7 page limit + unlimited appendix
- Highlights required
- Supplementary material separate
