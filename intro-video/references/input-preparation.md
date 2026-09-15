# Input preparation and limits

Sources: the [Video Agent guide](https://developers.heygen.com/docs/video-agent), [uploads](https://developers.heygen.com/docs/upload-assets), [usage limits](https://developers.heygen.com/docs/usage-limits), and the [official OpenAPI](https://developers.heygen.com/openapi/external-api.json). Check the endpoint's current schema if a requested option is absent here; general limits pages can be less specific than the endpoint schema.

## Inspect once before routing

Prompt-only is a fast path: fill the [brief](brief.md) directly and skip attachment inspection and preparation. Otherwise read `okou web download-file --help` once, then download each attachment once with bounded parallelism. Cache each stable local file and cheap probe result. Inspect real content and intended role, not only suffixes, and keep a lightweight inventory of source name, role, cached path, MIME type, bytes, and only the page, track, dimension, or duration metadata needed to choose the route.

Start with metadata and targeted text/media inspection. Render pages, transcode media, transcribe audio, or extract assets before routing only when that minimum work is what identifies the content, its role, or a real preservation conflict.

## Prepare only the selected route

Preparation does not select the route. File extensions, MIME types, and source metadata determine how to read or convert material; only an explicit preservation or editing-control requirement selects controlled composition. After route selection, derive only artifacts consumed by that route and run independent preparation with bounded parallelism.

| Input role | Preparation |
| --- | --- |
| Prompt only | Write a compact factual brief directly. Research only facts the requested result needs but the prompt does not supply; the agent writes from the prompt alone, and neither browses nor cites. |
| PPT/PPTX used as references | Extract text and speaker notes; convert to PDF for native Video Agent attachment, or summarize into the prompt. Verify converted page count and representative pages. |
| PPT/PDF that must retain layout | Inspect page dimensions and `okou presentation screenshot --help`, then rasterize at a consistent size matching the source geometry. Retain every required page and order. Fit those bitmaps into the independently chosen output canvas at their own aspect ratio, letterboxing where the output ratio differs from the page. |
| DOC/DOCX/Markdown/text/HTML | Extract relevant text and images; use a concise brief in the prompt or export a PDF. These source formats are not native Video Agent document inputs, but that does not make them controlled-composition inputs. |
| Spreadsheet/CSV/data | Calculate and verify the needed facts first, then send them as charts, a short PDF, or script text. |
| Image | Convert unsupported images to PNG/JPEG and verify legibility. Send the actual pixels whenever they exist: a brand mark or interface is reproduced from the file, not from a description of it. |
| Audio/video/recording | Probe codec, duration, dimensions, and tracks. Transcribe when the content supplies facts; convert unsupported formats to MP4/WebM or MP3/WAV for native references. Retain selected frames or original audio only when the user explicitly requires them, and verify the intended track. |
| Existing HyperFrames project | If the user explicitly asks to preserve, edit, or render the project, read and validate it for controlled composition. Otherwise extract useful facts and assets for native generation; Video Agent reads the supported reference formats below, not an editable timeline. |
| Other or corrupt file | Try the available reader/converter. Name the specific unreadable input, and continue only if it is nonessential to a faithful result. |

A screen recording is an ordinary video input, with one exception: a synchronized same-stem `.clicks.json` sidecar selects the camera route in SKILL.md Step 2, and [screen recording](screen-recording.md) owns its preparation and execution. Without such a sidecar, prepare the recording under the video row above.

## Keep limits attached to their actual endpoint

| API | Constraints that affect planning |
| --- | --- |
| Video Agent `/v3/video-agents` | Nonempty prompt, at most 10,000 characters; at most 20 attachments, **32 MB each** — the managed command enforces that per-reference cap, and the larger `/v3/videos` media figures below do not apply here. Native references: PNG/JPEG, MP4/WebM, MP3/WAV, PDF. Files are references: a full-frame image is reproduced verbatim when the prompt makes it a scene background, but the agent still owns scene timing and presenter placement, so this is not a preservation contract. |
| Asset upload `/v3/assets` and URL inputs | 32 MB per file. URLs must be public HTTPS **file** URLs, without login or Okou authorization headers. Resolve or upload local/private files first. |
| Direct upload `/v3/assets/direct-uploads` | Initialize with exact bytes/MIME, obey returned `max_bytes`, PUT bytes with returned headers, then POST `/v3/assets/{asset_id}/complete`. A `pending_upload` ID is not usable. Larger upload capacity does not remove downstream generation limits. |
| Avatar `/v3/videos` | Script at most 5,000 characters or audio at most 600 seconds; provide exactly one of `script`, `audio_url`, `audio_asset_id`. Media input limits are separately documented: video 100 MB, image/audio 50 MB, image/video under 2K. For an asset/URL ingestion path also honor its smaller cap. |
| TTS `/v3/voices/speech` | Text 1–5,000 characters; Starfish voice required; speed 0.5–2.0. Optional language/locale are in the provider schema; the current managed command exposes text and voice, and relies on provider language detection; read `--help` for the flags it actually has. |
| Studio `/v3/videos` | At most 50 full-frame scenes. An image scene uses either a silent duration or one narration source, not both. Arbitrary overlapping layers need a composition or an appropriate existing template. |
| HyperFrames Cloud | Takes a packaged composition, not a creative brief. Explicit fps/format/resolution/ratio exist on this endpoint and do not transfer to Video Agent. |

For more than 20 useful attachments, curate/merge derived references without discarding required facts. Name any reference you drop and why, and keep the route decided by the user's requirements rather than by an input limit. If preparation cannot fit the required material faithfully, explain the actual limit and resolve the source scope. For an oversized prompt, summarize references while keeping every instruction and any required verbatim script whole. On the controlled route, split long speech at scene or sentence boundaries, generate each necessary segment once, and keep timings aligned.

Record extracted facts and derived artifacts in the inventory with their source and preparation parameters. Reuse cached probes, extraction, and conversions after interruption or retry, and derive artifacts only for the selected route.

For native generation, pass supported references through the managed Video Agent interface so the platform can resolve artifact URLs for HeyGen; local paths and authenticated HTML pages are not provider file inputs. For controlled composition, prepare source visuals locally and pass narration audio through the managed presenter command, which resolves supported artifact URLs. Studio, direct uploads, and HyperFrames Cloud are provider capabilities; what Okou can actually run is what the managed commands expose. A login page with status 200 is not a valid media file.
