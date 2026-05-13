# DIAGRAM FORMAT SUPPORT

## 1. Purpose

This document defines the supported diagram/code/artifact format contour for the current assisted bounded operating model.

It clarifies:
- which formats are supported as editable sources;
- which formats are supported as export/render/presentation artifacts;
- how Google Slides should be interpreted;
- what is not implied by current support.

## 2. Supported format families

The repository now recognizes the following diagram-related format families:

- Mermaid
- draw.io / `.drawio`
- SVG
- PNG
- PDF
- Google Slides

## 3. Canonical editable sources

The preferred editable/source-of-truth formats are:

- Mermaid text
- draw.io / `.drawio` XML

These formats should be treated as the main semantic/editable forms for diagram work.

## 4. Derived / render / publish artifacts

The following should be treated primarily as derived or publish artifacts:

- SVG
- PNG
- PDF

Interpretation:
- SVG is the preferred vector render/export artifact;
- PNG is the preferred broad-compatibility image artifact;
- PDF is the preferred review/export artifact.

## 5. Google Slides interpretation

Google Slides is supported as a presentation/publishing layer.

Interpretation:
- Google Slides is a target presentation format;
- diagram content may be prepared for Slides publication flow;
- Google Slides should not be treated as the canonical editable source for diagram logic/layout unless a later wave explicitly defines that contour.

## 6. Practical source-of-truth rule

For diagram tasks, source-of-truth should remain in one of these forms:

- Mermaid
- draw.io / `.drawio`

Slides, PNG, and PDF should not replace canonical diagram sources by default.

## 7. Working model for the current contour

Recommended working model:

1. create or update the diagram in Mermaid or `.drawio`
2. validate semantic/visual intent in the source format
3. export/render into SVG or PNG
4. optionally produce PDF for review/distribution
5. optionally place rendered output into Google Slides presentation flow

## 8. What current support does not mean

Current support does not mean:

- full autonomous round-trip editing across all supported formats
- treating every downstream export format as a canonical editable source
- broad automated conversion guarantees between every format pair
- automatic guarantee that Google Slides is a lossless diagram-authoring environment

## 9. Relation to the bounded release

This format support model is compatible with the current assisted bounded release.

It does not expand release scope to:
- full autonomous all-file-operations mode
- broad autonomous multi-format diagram mutation
- universal format-conversion guarantees
