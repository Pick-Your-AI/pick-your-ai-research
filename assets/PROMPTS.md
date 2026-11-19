## assets/icon.png
- Date: 2026-10-30
- Tool and model: Codex CLI 0.164.0 image_generation (model id not reported by the tool)
- Seed: not supported
- Reference images: none
- Prompt: (verbatim)

```text
Use your image generation capability to create ONE image. Do not modify any other files.

NEON NIGHT REPO ICON Â· Pick-Your-AI/pick-your-ai-research

Create one square 1024 Ã— 1024 px image of a single repository glyph.
Use a simple geometric silhouette with a luminous outline and one accent spark.
Keep the background empty and the glyph inside the central 688 Ã— 688 px square.
Size class SQUARE: a squarish glyph about 600 to 660 px on each side.

GLYPH: Contract stack. Three flat rounded rectangular slabs stacked vertically with a small even gap, each slab slightly offset sideways, like layered component records. A thin vertical connector line runs down the left edge through all three slabs, ending in a small hollow circle node at the bottom. Geometric, simple, no inner detail.
SPARK PLACEMENT: One small filled spark at the top-right corner of the top slab.
PALETTE: outline #0F766E, glow #14B8A6; one spark in #FBBF24.
The spark is the only filled shape and the only element in #FBBF24; keep the
glyph outline in #0F766E so the spark remains distinct at small sizes.

No text, letters, numbers, words, logos, brand marks, human figures or third-party IP.

The lock pass renders assets/icon.png as a flat glyph in the family's light-surface
inks, without a tile or glow. Do not render the repository name in the image.

Extra constraints: square 1:1 aspect ratio, 1024x1024. Perfectly flat plain white (#FFFFFF) background, no gradient, no floor, no shadow, no texture. Flat vector look with clean uniform-width outlines. Palette strictly: outline #0F766E, optional soft glow #14B8A6, one spark #FBBF24. NEGATIVE: no text, letters, numbers, words, logos, brand marks, UI chrome, people, hands, photorealism, extra objects, borders, frames, tiles, watermarks, signatures, blue colors. Every surface stays blank. Report the full path of the generated image file.
```

- Candidates: 2 generated (the second was a bolder-stroke retry after an icon-budget art-fail that was really the auto ground mode, not the image); selected: 1 (reason: first in generation order, passes icon QA with --ground transparent and the manual no-text review)
- Post-processing: showcase.py 1.0.0 content icon normalize --option A --ground transparent; output sha256 1c85656b6c379e85728069f711dca36fc332d286575dfd2325de4d7cad77bcb6; 111.2 KB
