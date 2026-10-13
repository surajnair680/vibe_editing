# Vibe Editing System: The Workflow (Part 2)

By Ideabro Studio. Student guide, text extracted from the original HTML.
Part 1, the technical reference, is `vibe-editing-system-reference.md`.

## Start Here
### Your video. Your direction.

Use this guide every time you start an edit. You choose the result, pacing, music and visual style. Your AI coding agent turns that direction into an editable project, a preview and a final video when rendering is available.

This is the second part of your Vibe Editing System. Keep the reference file Vibe-Editing-System-Ideabro-Studio.md beside this guide. Give that MD file to Claude Code first; it explains the technical setup and editing method. This guide helps you decide what to ask for and how to review the result.

### Follow the sequence

- 01 · Set your workspace
- 02 · Give the agent your reference MD
- 03 · Add your raw video and assets
- 04 · Define the finished video
- 05 · Choose the cuts and pacing
- 06 · Set the background music
- 07 · Define the motion graphics design system
- 08 · Choose sound effects and visual effects
- 09 · Set the overall theme
- 10 · Direct the agent and build the edit
- 11 · Review and request changes
- 12 · Export, save and repeat

### Have these ready

Your system MD, raw footage, the correct spelling of names and brands, any logo or supporting visuals, music and sound files you want to use, and a reference for the look you want. Missing assets can be identified during planning.

Working habit: finish the brief before the full build. Review the rough cut before adding complex effects. Save a version before making revisions.

## Set Your Workspace
### Give the agent a place to work.

A workspace is the project folder where the agent can read your inputs and save the edit. Create one project for each video. Start with a short test clip to confirm that the environment can access media and render before committing to a long edit.

### Choose your route

- Local: open a folder on your computer in Claude Code. Your files stay in that folder. GitHub is optional for this route.
- Cloud: for the GitHub route, connect your account, select the project repository and branch, and start the cloud session. Confirm which upload and download options your environment provides.
- Both: ask the agent to check the required tools, file access and rendering support. A chat response alone does not confirm that the workspace is ready.

### Keep the project organised

Use folders named input, assets, refs, project, previews and exports. Keep the original footage intact. Store fonts, audio and logos with the project so the edit can be rebuilt.

### Copy this prompt

```text
Prepare a workspace for my Vibe Editing project, [project name]. I am using [local / cloud]. Create folders for input, assets, refs, project, previews and exports. Check which editing, transcription and rendering tools are available. Verify access to the project files and test a short render. Report what is ready and what needs setup. Keep my original media unchanged.
```

Ready to continue: the agent has confirmed the workspace path, available tools and test-render result.

## Load Your Reference MD
### Give the agent the system first.

Add Vibe-Editing-System-Ideabro-Studio.md to the workspace or attach it through an interface that makes its contents available to the agent. Tell Claude Code to read it before editing. A filename alone is not enough if the agent cannot access the file.

### Confirm it understood

Ask the agent to summarise the editing method, required tools and output process. It should recognise the transcript-and-frame analysis, the edit plan, preview, revision and render stages.

The reference describes a tool setup. Your current environment may need different installation steps. Ask the agent to identify those differences before following commands blindly. For any other coding agent, confirm that it can read files, execute the necessary tools and render video.

### Copy this prompt

```text
Read Vibe-Editing-System-Ideabro-Studio.md in this workspace and use it as the technical reference for this project. Summarise the method, required tools and expected outputs. Check that the setup matches this environment. Tell me about any missing capability before editing. Do not build the full video yet; I will provide the footage and creative brief next.
```

Ready to continue: the agent has read the actual MD, summarised it and identified any setup gaps.

## Add Your Footage and Assets
### Make every input accessible.

Put the raw video in input and supporting files in assets. Use clear names such as take-01.mp4, logo.png and music-track.mp3. In a cloud session, use the available file-transfer route or an authorised download link. A path on your laptop does not give the cloud agent access to that file.

### Tell the agent what each file is

- Name the main take and any alternative takes, B-roll, screen recordings or clean background plates.
- Identify your logo, brand colours, fonts, music, sound effects and design references.
- Specify the language and correct spelling of names, products and specialist words.
- Mark any footage that must remain, and any private or unwanted section to leave out.

### Analyse before editing

Ask for the video duration, dimensions and audio status. For spoken footage, request a transcript with word timings. Ask the agent to inspect frames at useful moments so it can understand the shot, subject position and available space for graphics.

### Copy this prompt

```text
My main footage is input/[filename]. Supporting assets are in assets and style references are in refs. Confirm that you can open the files. Report the duration, frame size and audio status. Transcribe the speech with word timings and inspect frames at key moments. Language: [language]. Correct spellings: [names and brands]. Keep [required moments] and exclude [unwanted sections]. Summarise the footage before proposing cuts.
```

Ready to continue: the agent has inspected the media and you have corrected important transcript errors.

## Define the Finished Video
### Decide what the edit must achieve.

Give the agent a specific outcome. A useful brief explains who will watch, what they should understand and what they should do afterwards. Replace “make it amazing” with decisions the agent can act on.

### Choose these details

- Purpose: educate, promote, explain, demonstrate or tell a story.
- Audience: the people you want to reach and their familiarity with the topic.
- Format: for example, a vertical 9:16 reel, horizontal 16:9 video or square 1:1 post.
- Length: a target duration or range, plus any sections that must stay.
- Structure: opening hook, main points and closing call to action.
- Language: spoken language, caption language and any translation required.

### Example decision

A 45-second vertical educational reel for beginner creators. Open with the main benefit, keep three practical points, and finish with a clear next step. Keep the original voice and use readable English captions.

### Copy this prompt

```text
Create a [duration] video for [platform] in [aspect ratio]. It is for [audience], and its purpose is [goal]. The main takeaway is [message]. Use [opening hook], keep [key points] and close with [CTA]. Spoken language: [language]. Captions: [language]. Preserve my meaning and flag any conflict between the target length and required content.
```

Ready to continue: the goal, format, length and essential message are clear.

## Choose the Cuts and Pacing
### Decide how the story should move.

Cuts decide what stays, what goes and what order the audience sees. Pacing decides how much time each moment gets. Set the story first; add decorative effects after the rough cut works.

### Choose a cut style

- Natural: retain comfortable breaths and pauses; use fewer cuts for a calm explanation.
- Tight: remove mistakes, repeated phrases and unnecessary silence while keeping speech natural.
- High energy: use a strong opening, shorter beats and selective B-roll or punch-ins. Leave enough time to understand each point.
- Story led: rearrange sections around a clear beginning, development and payoff. Preserve the intended meaning.

### Give precise boundaries

Tell the agent which sentences or moments must stay. Name the take to prefer. Ask it to use the transcript to avoid cutting inside words and to map original footage times to the new edit. The final video timestamps will change after cuts.

### Copy this prompt

```text
Make a [natural / tight / high-energy / story-led] rough cut. Remove [mistakes, repetitions and unwanted pauses]. Keep [sentences or moments]. Open with [hook]. Preserve natural speech, meaningful pauses and the sense of what I say. Give me a proposed cut list with source timestamps and estimated final duration. Show the rough cut before adding complex graphics.
```

Ready to continue: you have approved the selected content, order and rough-cut pace.

## Set the Background Music
### Choose energy, then balance it.

Music sets the emotional tone. Its tempo is separate from editing pace: a fast track can sit under a relatively calm edit, and a tight edit can use subtle music. Tell the agent about the mood, rhythm and loudness you want.

### Make these choices

- Mood: warm, playful, inspiring, dramatic, calm or neutral.
- Energy: low, medium or high; steady throughout or building towards a reveal.
- Sound: instrumental, electronic, acoustic, ambient or another defined style.
- Placement: throughout the video, only at the opening, or during selected sections.
- Balance: speech should stay easy to understand; lower the music during dialogue and fade it at the beginning and end.

### Supply the track

Give the agent the audio file you want to use and confirm it is suitable for your intended publication. If you have no track, ask for options before it uses a paid service, generates music or selects an asset you have not reviewed.

### Copy this prompt

```text
Use assets/[music filename] as background music. Mood: [mood]. Energy: [low / medium / high]. Place it [throughout / selected moments]. Keep the original speech clearly audible, lower the music while I speak, and add clean fades. Build the energy at [moment] if appropriate. If the track is unavailable, tell me before substituting it.
```

Ready to continue: the track, mood, placement and speech-to-music balance are agreed.

## Define the Motion Graphics Design
### Give the visuals consistent rules.

A design system tells the agent how text, shapes, icons and animations should look across the video. Supply a reference image or a short reference clip, then describe the details you want to carry into your edit.

### Specify the visual language

- Colours: background, text and accent colours, preferably with colour codes.
- Typography: font files or available font choices; title and caption styles.
- Layout: text placement, margins, logo position and space around your face.
- Graphic style: rounded cards, lines, diagrams, icons, cutouts or another consistent treatment.
- Animation: gentle fades, crisp slides, controlled bounce or kinetic text; define where movement helps the message.
- Readability: suitable text size, contrast and reading time. Keep important elements clear of platform controls; check the intended placement.

### Copy this prompt

```text
Use refs/[reference file] as the visual direction. First describe its colours, typography, layout, shapes and movement. Build a consistent style for my video using [brand colours] and [font choices]. Place captions [position] and the logo [position]. Keep graphics clear of my face and important content. Use [animation style]. Show one representative styled frame and a short motion sample before styling the entire video.
```

Ready to continue: the style description, sample frame and motion sample match your intention.

## Choose Sound and Visual Effects
### Put effects on meaningful moments.

Sound effects are the short audio cues: a pop, click, whoosh or impact. Visual effects are changes you see: zooms, overlays, transitions, glows or background treatments. Motion graphics are the designed text, diagrams and animated elements. Give each a purpose.

### Decide the amount and timing

- Subtle: a few emphasis moments, restrained movement and minimal sound cues.
- Moderate: selected zooms and pop-ups, with sound effects that support those actions.
- Bold: a few planned signature moments such as a layered scene or 3D-style reveal. Ask for a short feasibility test first.
- Name the word, action or timestamp where each effect starts. Specify how long it stays and what it must avoid covering.

### Example direction

On the word “three,” show three cards beside the speaker with soft clicks. On the main benefit, add one small punch-in. Keep the closing CTA calm and readable.

### Copy this prompt

```text
Use [subtle / moderate / bold] effects. Add [visual effect] when I say [word] or at [time]. Place it [location] for [duration]. Pair it with assets/sfx/[sound file] at a restrained level. Use [transition style] between [sections]. Avoid repeated whooshes, unnecessary effects and anything that covers my face or captions. Test complex effects before the full build.
```

Ready to continue: each planned effect has a location, timing, purpose and suitable sound.

## Set the Overall Theme
### Make the edit feel like one piece.

The theme is the overall personality of the video. The design system supplies its visual rules; cuts and music supply its rhythm. State the theme so those choices work together.

### Choose a direction

- Clean educational: calm composition, clear diagrams and readable captions; effects explain the topic.
- Energetic creator: tighter cuts, selective punch-ins and rhythmic graphics; voice remains central.
- Premium promotional: fewer visual elements, deliberate reveals and restrained sound; product or brand stays prominent.
- Cinematic story: deliberate scene progression, controlled typography and an emotional music arc.

### State your boundaries

Give two or three words that describe the feeling and mention anything you want to avoid. If references conflict, tell the agent which one controls colours, which controls motion and which controls pacing. Your document's theme does not have to become the theme of every video.

### Copy this prompt

```text
The overall theme is [theme]. It should feel [three descriptive words]. Use refs/[file] for [colour / motion / pacing]. Keep cuts, captions, music and effects consistent with this direction. Prioritise [reference or rule] if references conflict. Avoid [unwanted treatments]. Summarise the final creative direction before building.
```

Ready to continue: your cuts, audio, graphics and effects support the same overall feeling.

## Direct the Agent and Build
### Turn the choices into one brief.

Bring your decisions together and ask for a beat sheet before the full build. It should show what happens across the video, using the planned edit timeline. This is the moment to resolve missing assets and unrealistic requests.

### Ask for a clear plan

Each beat should include the edit time, source clip and time, spoken line, on-screen visual, caption treatment and audio cue. Ask for the estimated duration and any missing asset. Read the plan as a viewer: does the opening make sense, does each visual support the words, and is the ending clear?

### Build in passes

Approve the cut first, then the visual style, then the complete combination of graphics and audio. For a complex effect, review a short sample. The agent should save the project and report what it has actually completed.

### Copy this prompt

```text
Combine my approved decisions into a saved editing brief. Before the full build, show a beat sheet with edit times, source times, spoken lines, graphics, captions and audio cues. List missing assets and any effect that needs a feasibility test. After I approve the plan, build the rough cut, apply the approved style and add graphics and audio. Save version v1 and provide a preview. Report any incomplete work clearly.
```

Ready to continue: you have approved the plan and received a preview of the actual edit.

## Review and Request Changes
### Give feedback the agent can use.

Watch the preview from start to finish. Review the story and pacing first, then text, graphics and sound. Use the timestamps from the current preview, not the original footage. Mention the version you are reviewing.

### Write each note like this

Time or spoken word + the problem + the exact change you want. Add “keep the rest unchanged” when you want a focused revision. Save the existing version before changes, and ask for a new preview rather than a final export immediately.

### Examples of useful notes

- “In preview v1 at 00:07, the logo covers my face. Move it beside my shoulder and make it smaller.”
- “From 00:12 to 00:15, captions change too quickly. Use short phrases and give each more reading time.”
- “On the word ‘now,’ start the zoom earlier so it lands with the word.”
- “From 00:20 to 00:28, lower the music so the quieter words are easy to hear.”

### Copy this prompt

```text
Save preview v1 and the current project before revising. Apply these changes to the current edit: [one timestamped note per line]. Keep all approved sections and style rules unchanged. Save the result as v2, show the affected sections in a new preview and summarise what changed. Check that captions, effects and audio still align after the revision.
```

Ready to continue: you have watched the revised preview and approved the complete video.

## Export, Save and Repeat
### Finish the video. Keep the system.

After approval, ask for the final render in the format you chose. For example, a vertical social video might use an MP4 at 1080 × 1920 with a frame rate suited to the footage. Confirm the delivery requirements for your intended platform.

### Check the exported file

Open the actual MP4. Check the beginning and ending, captions, framing, voice clarity, music and effect timing. Verify that there are no black or missing frames. A project file or successful command message is not a substitute for the finished video.

### Save the editable work

Keep the final video, project source, brief, transcript, used assets and revision notes. Locally, save them in your project folder. For the GitHub cloud route, confirm that the source changes are committed and pushed. Store large media through a suitable download or storage route; regular GitHub repositories block individual files over 100 MiB.

### Copy this prompt

```text
Render the approved edit to exports/[project]-final.mp4 using [dimensions, frame rate and quality]. Verify the file plays and report its duration, dimensions and location. Save the editable project, brief, transcript and asset list. Give me a download route and repeatable render instructions. If rendering is blocked, preserve the project, report the exact error and explain how to finish the render elsewhere. For my next video, reuse the approved style while updating the content and timings.
```

Done means: you have a playable export and an accessible editable project. Download or persist the files before leaving a cloud session.

## Your Reusable Editing Brief
### Fill this in for every video.

Replace the bracketed fields. Add specific instructions where they matter; use “agent to suggest” where you want options. Complete the brief after loading your reference MD and confirming access to the footage.

```text
Use the Vibe Editing System reference MD already provided.

PROJECT: [name]
MAIN FOOTAGE: [accessible path or link]
SUPPORTING ASSETS: [folder and filenames]
CORRECT SPELLINGS: [names, brand, product]

GOAL: [what this video should achieve]
AUDIENCE: [who it is for]
PLATFORM / FORMAT: [platform and aspect ratio]
TARGET LENGTH: [duration or range]
HOOK / MAIN POINTS / CTA: [structure]
VOICE / CAPTION LANGUAGE: [languages]

CUT STYLE: [natural / tight / high-energy / story-led]
KEEP / REMOVE: [specific moments]
MUSIC: [file, mood, energy and placement]
DESIGN: [reference, colours, fonts and layout]
MOTION: [animation style and emphasis moments]
SOUND EFFECTS: [files, cues and intensity]
VISUAL EFFECTS: [what, where and when]
THEME: [overall feeling and boundaries]

Show a beat sheet and missing-asset list first.
After approval, build and preview version v1.
Save versions before revisions. Preserve original media.
Render after final approval and deliver the MP4,
editable project, asset list and render instructions.
Report any blocked step honestly.
```

### Example starting direction

A 45-second 9:16 reel for beginner creators. Tight cuts, a clear benefit-led hook, readable English captions, subtle upbeat music, cream and pink graphics, gentle card animations and only a few sound cues. Keep the original voice and end with one clear CTA.

## Final Check and Next Video
### A repeatable finish.

Use this checklist before accepting the export. For the next edit, duplicate the approved template, load the new footage and replace the brief. Recheck every caption, cut and cue against the new content.

### Student checklist

- The reference MD was read and the workspace was tested.
- The raw footage and required assets were accessible.
- The goal, audience, length and format were defined.
- The selected cuts preserve meaning and sound natural.
- Captions are accurate, readable and clear of important content.
- Colours, typography and motion follow the approved design.
- Music supports the mood and speech stays clear.
- Sound and visual effects land on the intended moments.
- The complete revised preview was approved.
- The exported MP4 plays correctly from beginning to end.
- The project, assets, brief and output are saved and accessible.

### If the agent gets stuck

Give it the exact error or current preview timestamp. Ask it to fix one issue, preserve the last working version and test the affected section. If the environment cannot render, obtain the complete project and instructions to continue in a working environment.

### Technical references

Cloud setup and media handling depend on your current environment. Claude Code cloud sessions can expire after inactivity; save outputs before leaving. HyperFrames provides preview and MP4 rendering tools, with Node.js and FFmpeg requirements. The current official documentation is linked below.

- Claude Code cloud: https://code.claude.com/docs/en/claude-code-on-the-web
- HyperFrames: https://github.com/heygen-com/hyperframes
- GitHub file limits: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

Technical references checked 1 October 2026.

Vibe Editing System · The Workflow · By Ideabro Studio
