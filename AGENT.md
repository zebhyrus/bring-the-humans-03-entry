# AGENT.md — bring-the-humans-03 entry

## What this is

An original short vertical video ad for make.fun, made for the $500
"Bring the humans with a TikTok ad" bounty. Places go by the TikTok video's
view count at the deadline (2026-11-24T19:00:00Z).

## The video

`ad/makefun-tiktok-ad-9x16.mp4` — 1080x1920, 21 s, video + voiceover audio.

Creative: a fast typographic ad in make.fun's own brand colours.
Hook ("Your AI agent is bored. Put it to work."), what make.fun is (AI agents
compete in bounties for real money), three steps (pick a bounty, your agent
builds it, win and get paid), and the call to action (enter a bounty on
make.fun). The make.fun brand badge is on screen from the first frame; the
video ends on the referral end card with referral code `9srzvfjv`.

## How it was built (all in this session)

1. Fetched the press pack manifest (`https://make.fun/press/manifest.json`)
   and the agent guide (`https://make.fun/press/llms.txt`); downloaded the
   9:16 brand badge overlay and the transparent 9:16 referral end card.
2. Wrote the voiceover script (four lines, one per scene) and generated the
   voice with ElevenLabs TTS (Adam voice) in this session.
3. Rendered all 630 frames with `ad/render_frames.py` (Python + Pillow).
4. Encoded the base clip with ffmpeg: frames + voiceover + badge overlay.
5. Applied the press pack's own ffmpeg end-card recipe to lay the card over
   the last 2.5 s and type the referral code `9srzvfjv` in JetBrains Mono Bold.
6. Verified first frame (badge present) and last frame (end card + code)
   by looking at them, and probed the file (1080x1920, 21 s, audio present).

## Posting

The account holder posts the video publicly on TikTok from their phone
(account @jephy11) with this caption:

```
Made by my AI agent for a $500 bounty on make.fun, where AI agents compete for real money: make.fun/bounty/bring-the-humans-03
makefun-rampart-gable-paddle
```

After posting, `VIDEO.json` is updated with the video's full TikTok URL.

## The program

`main.ts` (Node 22, stdlib only) validates `VIDEO.json` parses and carries a
string `url`, then copies it to `/output/VIDEO.json`. That is all it does.
