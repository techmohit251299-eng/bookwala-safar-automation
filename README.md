# Book Summary Video Automation — Step 1

**What's built so far:**
- `.github/workflows/generate-video.yml` — GitHub Actions workflow. Runs daily at 9 AM UTC (edit the cron line to change timing), also runnable manually from the Actions tab.
- `scripts/select_book.py` — auto-picks the next book from `data/books.json`, marks it used, writes `data/selected_book.json`. Cycles back to the start once every book has been used.
- `data/books.json` — your book list. Add more books here anytime.

**To use this:**
1. Push this folder to a GitHub repo.
2. Add repo secrets (Settings → Secrets and variables → Actions) — you'll need `ANTHROPIC_API_KEY` and `ELEVENLABS_API_KEY` once step 2 and 3 are added.
3. The workflow will run on schedule, or trigger it manually to test.

**Next steps (not built yet, commented out in the workflow):**
1. Script generation — motivational, focus-themed script with emotion tags for ElevenLabs
2. Voiceover generation via ElevenLabs
3. AI visual generation per script scene
4. Video assembly
5. Thumbnail generation
6. Publish to YouTube
