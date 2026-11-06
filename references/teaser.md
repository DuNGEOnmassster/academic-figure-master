# Result montage: /teaser

## Visual job

Answer “what can this system do?” using actual outputs. Build a compact photographic plate with minimal labels. Architecture, training loops and implementation prose belong in `/pipeline`. A paired request needs two independently composed figures, not the same boxes with different headings.

## Select the evidence

1. Read the paper's capability claims and inspect the result gallery or local runs. Build a shortlist by capability, visual diversity and visible temporal change. A grid of nearly identical frames is not diversity.
2. Resolve the final/current displayed result within each case. Gallery pages often include failed historical attempts below a successful final attempt; read case/attempt records rather than taking the first media URL blindly. If finality or status is absent, record `unknown` and inspect the result without inventing PASS.
3. For video, inspect a contact sheet before choosing event times. Prefer setup, meaningful action, consequence; timestamps depend on clip duration and event timing. Keep each sequence chronological and from one attempt. For images, use independent examples or explicitly identified comparisons.
4. Keep a private source manifest: local file, source page/media URL, case, attempt, model/checkpoint if known, status and frame timestamp. Use `scripts/figure_media.py` to validate and extract declared local video frames. Unknown provenance fields stay explicit.

Missing real outputs are a content dependency. Continue with the claim shortlist and an editable layout plan, then request the missing assets; do not synthesize photographic “results”. Do not substitute a public demo for the author's results without identifying it.

## Compose

- A useful starting recipe is four rows, two capability groups per row, three chronological frames per group. This is a layout option, not a required case count. Use fewer larger groups if the paper needs fewer claims.
- Keep gutters narrow and tile sizes consistent. Use a shared crop across a temporal group so apparent motion does not come from changing crops. Inspect whether the crop removes evidence or changes the conclusion.
- Put a short capability label on a small cream tab at the first tile of each group. Use concrete phrases such as “Object interaction” or “Viewpoint control”, usually two to four words. Avoid sentences on top of photos.
- A large project title can occupy its own narrow central mosaic strip or an outer margin. Do not obscure the main temporal sequences. Avoid duplicating a title banner on a method figure merely for consistency.
- Prefer a few large, sharp examples over dozens of unreadable thumbnails. Check the actual paper column width before increasing density.
- Use real photo/video frames as individually replaceable picture objects; labels, borders and title remain editable. Preserve recorded content, including model artifacts. Cropping, resizing and corner masks are layout operations; do not retouch scientific evidence.

## Caption and acceptance

Use a short English caption unless the user requests another language: “**[Method] supports [capabilities].** Selected [qualitative production / held-out evaluation] outputs show [what the groups demonstrate]; frames within each group follow temporal order.” Choose the bracketed scope from actual evidence. A curated production gallery alone does not establish generalization, monotonic improvement or a numerical win.

Before delivery inspect at full view and final print size: each label matches its sequence; each claimed action is visible; sequence order is correct; the title leaves evidence visible; frames have consistent crops. Keep technical explanation and detailed provenance beside the figure, not inside it. Complete the shared PPTX/PDF and Overleaf checks in [handcrafted-figures.md](handcrafted-figures.md).
