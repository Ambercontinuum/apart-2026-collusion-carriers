# LaTeX paper source

## Local Windows build

From the project terminal run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File output/pdf/source/build.ps1
```

The script locates the project's downloaded Tectonic compiler and sets the correct
working directory for the fonts. No global TeX installation is needed. Output is
`output/pdf/paper.pdf`. With the project folder open in VS Code and the LaTeX
Workshop extension installed, select the **Project Tectonic** recipe.

Do not use pdfLaTeX: `fontspec` requires XeLaTeX (or the supplied Tectonic).

Open `paper.tex` as the main file. In Overleaf select **XeLaTeX**, then compile
twice. Locally run `xelatex paper.tex` twice, or `tectonic paper.tex`.
Keep the adjacent `fonts/` directory: the supplied template uses Old Standard TT.
The included font files are distributed under `fonts/OFL.txt`.

The paper uses US Letter, one-inch margins, 11-point body text, 14-point section
headings, single-column layout, and the template's ruled title/author/affiliation/
Apart attribution block. Its organization follows the supplied PDF's adaptable
section guidance. Template guidance boxes and placeholders are removed.

The compiled artifact has exactly four paper-content pages, including ethics,
contributions and LLM disclosure; page five is references only. Explicit page
breaks preserve this division. Recheck pagination after any edits.

This is an author-review candidate, not an externally submitted artifact.
Repository publication is owner-authorized; external submission is separate.
No new model inference or scratchpad publication accompanies this update. The project repository and pinned final experiment folder returned HTTP 200
without authentication on October 25, 2026. The cited scratchpad stop-log page
returned HTTP 404. Its citation now identifies author-held records without a broken public hyperlink. Git confirms the file exists in the cited local snapshot.

Inputs: the supplied PDF template in `docs/`, Claude's supplied draft, published
research report and experiment evidence, and the local stop-event audit. The
larger human-coupled case is summarized only as an exploratory observation.

Literature metadata and abstract-level characterizations were checked against
the primary arXiv records for 2402.07510, 2410.03768 and 2602.15198. Other unverified
bibliography entries from the preceding draft were not carried forward.
