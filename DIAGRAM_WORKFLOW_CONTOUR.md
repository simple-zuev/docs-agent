# DIAGRAM WORKFLOW CONTOUR

## 1. Purpose

This document defines the minimum supported diagram workflow contour for the current assisted bounded operating model.

It is intended to harden launch clarity for:
- Mermaid
- draw.io / `.drawio`
- SVG
- PNG
- PDF
- Google Slides

## 2. Minimum supported workflow

The current supported workflow is:

1. source intake
2. source review/validation
3. render/export package preparation
4. optional presentation/publication packaging
5. controlled operator-supervised downstream use

## 3. Source intake

Accepted source-first inputs:

- Mermaid text
- draw.io / `.drawio` XML

Accepted downstream/reference artifacts:

- SVG
- PNG
- PDF
- Google Slides-linked or Slides-target presentation context

Rule:
- prefer Mermaid or `.drawio` whenever the task requires future editing
- treat downstream artifacts as derived unless explicitly governed otherwise

## 4. Source review and validation

Before export/publication, review the source for:

- semantic correctness
- diagram completeness
- naming consistency
- layout clarity
- correspondence between source and intended publication target

Recommended principle:
- validate source before packaging exports
- do not treat export artifacts as a substitute for unresolved source issues

## 5. Render/export package

The preferred export package is one of:

### Minimal package
- source (`Mermaid` or `.drawio`)
- PNG

### Standard package
- source (`Mermaid` or `.drawio`)
- SVG
- PNG

### Review/distribution package
- source (`Mermaid` or `.drawio`)
- SVG or PNG
- PDF

Rule:
- keep canonical source together with rendered outputs whenever possible
- do not ship only PDF if future editing is expected
- do not rely only on PNG if high-fidelity vector reuse is expected

## 6. Google Slides publication path

Google Slides is treated as a publication/presentation target.

Preferred path:
1. prepare source in Mermaid or `.drawio`
2. export to PNG or SVG
3. place exported artifact into Google Slides
4. retain source separately as the canonical editable artifact

Interpretation:
- Slides is a presentation layer
- Slides does not replace the canonical diagram source
- a Slides-published diagram should still have retained Mermaid/`.drawio` source when future edits are likely

## 7. PDF usage rule

PDF is supported for:
- review
- distribution
- sign-off or circulation artifacts

PDF is not the preferred canonical editable diagram source.

## 8. Operator guardrails

Do:
- keep source-of-truth in Mermaid or `.drawio`
- export intentionally for the target channel
- retain editable source together with publish artifacts
- treat Slides as presentation layer by default

Do not:
- assume full autonomous round-trip editing across all formats
- treat PDF/PNG/Slides as the default editable source
- infer that all format-to-format conversions are guaranteed or lossless
- widen current release claims beyond assisted bounded use

## 9. Launch interpretation

This workflow contour is sufficient for today's assisted bounded launch when:
- source remains controlled
- exports are treated as derived artifacts
- operator supervision remains in place
- no claim is made about universal autonomous diagram tooling

This workflow contour does not imply:
- full autonomous diagram production across all formats
- lossless multi-format round-trip editing
- broad autonomous mutation across arbitrary slide/doc/file targets
