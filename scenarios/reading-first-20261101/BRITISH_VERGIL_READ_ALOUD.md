# British Vergil: On Continuity, source-bound hearing candidate

This is an implementation candidate for the existing v109 paginated Linotype reader. The literary narrator identity is Vergil, the voice of Illustrating Inferno; an existing British-English synthetic OpenAI voice (Cedar as a candidate) is its replaceable embodiment.

**Source proof:** Private WLAN v109 HTML snapshot SHA-256 `e48eb4a93cc862bb3c600f1f676e7281439293c12106d818cf0eda62c0f5779d`. Ten source blocks (title plus all nine prose paragraphs), 2,637 characters, exact speech-input SHA-256 `fb57e1726c816497beed41a12504a276a7eeed8b9e1359e35ed07426c56f4b4c`. Publisher/source citation furniture is not narrative prose. `check_vergil_source.py` refuses any changed source.

**Reader seam:** `british-vergil-hearing.mjs` uses SatzfunkPlayer only. No new audio engine, transcript or Continuous mode. It creates no button without an authorized private recording manifest, a matching source digest and reachable same-origin WAV. Playback and seeking remain outside the repaginating leaf. The visible control discloses AI-generated voice.

**Not established:** A Cedar WAV, accent or artistic approval, source-to-audio word fidelity, WAV manifest, new active WLAN release, native iPad Safari/VoiceOver, or public production. The older v109 remains the immutable staging baseline. Do not stage a dummy file or assert Read Aloud exists before actual synthesis and acceptance.
