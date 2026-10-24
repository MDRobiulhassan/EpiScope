# Team Roles and Presentation Split (Draft)

The nine-slide presentation gives Robiul the core technical section in about four minutes, while Samin and Mahafujul each speak for about five minutes. The work areas below are a proposed division for preparing the final handover. They are not evidence of past contribution; the signed contribution matrix must describe the work each person actually completed.

| Member | ID | Proposed lead/support work area | Slides | Target speaking time |
|---|---|---|---:|---:|
| Robiul Hassan | 0222220005101043 | Lead the core pipeline walkthrough: architecture, batch processing, and the incremental inventory implementation. | 1-4 | About 4 minutes, including the Colab cue |
| Md Samin Osman | 0222220005101042 | Explain data quality, detection/forecast evaluation, and the meaning of the measured results. | 5-6 | About 5 minutes |
| Md Mahafujul Alam | 0222220005101066 | Present the dashboard, privacy/limitations, team handover, and recommendations. | 7-9 | About 5 minutes |

## Proposed project work areas

- **Robiul (lead):** architecture and integration; generator and pipeline changes; Colab workflow; end-to-end run coordination; core report content.
- **Samin (support):** review generator/data-quality behavior; organize evaluation evidence and explain metric interpretation; review limitations and references.
- **Mahafujul (support):** prepare the dashboard walkthrough; review serving/privacy explanations; help prepare the policy brief, slides, and video edit.

This split gives Robiul the main technical narrative while giving the other two members clear sections to own. Adjust it to match the actual work and commits before signing the matrix.

## Contribution-share note

As a starting point only, the user reports that Robiul completed most of the work. A draft contribution split could therefore be **Robiul 60%, Samin 20%, Mahafujul 20%**. These values are not confirmed. The three members must agree on and sign the percentages based on their actual contributions; do not submit the draft percentages unchanged if they are inaccurate.

## Recording guidance

- Target a 15-minute presentation with a short live dashboard/Colab demonstration. Robiul has a shorter section because he completed most of the technical work.
- Show each member's name and their lead area on screen during their section.
- During Robiul's incremental-feed slide, run the two Colab pipeline passes and show the actual output. The first clean run should add one row per facility; replaying it should add zero.
- Do not claim the inventory feed changes the optimizer; the current code keeps that feed as a parallel Bronze–Silver–Gold demonstration.
- Replace historical or expected values with the exact output from the final run where the video claims a fresh measurement.
