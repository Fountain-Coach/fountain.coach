# A Sound Must Earn Its Place

*On Kino International, two unsuccessful synthesizer approaches, a second listening experiment, and the distance between visual and acoustic conviction.*

**Status:** Unpublished editorial proof for author listening. Four source-bound audio recordings and four live Csound source performances, kept separate. Historical recordings are reconstructions, not original browser-session captures.

In *Kino After Dark*, the illuminated façade of Berlin's Kino International gave us a place to begin. I wanted the residue of cinema: a room with some life left in it after the film, a little distance, a phrase that might have belonged to someone who was no longer there.

The building seemed particularly suited to that imagination. Its horizontal façade, projecting glazed foyer and illuminated lettering offered a place suspended between public spectacle and private recollection. An architectural interpretation reduced it to volumes, proportions and their relationships. The result was persuasive. The picture seemed to understand the building before the sound understood its room.

[KINO-ILLUSTRATION:architectural-plate]

Our first Kino synthesizer assembled a familiar set of electronic elements: a fixed bass pattern, percussion from filtered noise, repeated material from a sample player and effects intended to provide depth. MIDI 2.0 carried control; Ear measured the output and changed an echo. The timing was correct. The connections were real. Yet the result felt papery and toyish. The bass had little weight, the percussion sounded like a placeholder, and the effects announced themselves as effects. It demonstrated the machinery, not the aftermath of a film.

We revised the environment, moving away from an insistent beat grid toward cinematic air, slowly changing texture and a quieter, original musical memory. The *Midnight Cylinder* phrase was newly composed in Csound, not sampled from Lou Donaldson or another commercial recording. Ear could still observe the resulting signal and alter a bounded echo. This second synthesizer had a more coherent sense of what an atmosphere might require. But removal was not completion. Slower movement did not automatically confer expression, and a filtered phrase could suggest distance without acquiring the weight of a performed musical object. This approach, too, did not satisfy the artistic intention.

The two early approaches should be heard together. These short excerpts are newly assembled editorial reconstructions from their own preserved Csound-rendered stems, **not** archival recordings of the browser patches as they ran. The first uses the original fixed bass and hat sounds; the second uses the original cinema-air, film-dust and Midnight Cylinder recordings. They let us hear the source materials and their contrasting direction without falsely claiming a captured performance. They are different approaches, not identical-score A/B masters.

[KINO-HISTORICAL-COMPARISON:groove-memory]

The source instruments themselves must be heard too. The live Teatro Csound host below executes the original bass-and-hat voices and the revised cinema-air, film-dust and Midnight Cylinder voices. These are not the recordings above: they are running Csound synthesis, with an explicit Start and Stop. The historical timing and layering remain reconstructed where an original browser session was not captured.

[KINO-LIVE-SYNTHS:history]

The comparison makes clear why our technical competence was not enough. The first version makes too much of its mechanisms; the second is more restrained but remains insufficiently particular as sound. An attractive interface, a perfectly correct MIDI connection or a source-bound Csound render cannot make those shortcomings disappear. The visual interpretation is strong, while the acoustic work is not. That difference belongs in the published account rather than being edited away.

The obvious escape was to go native. An AUv3 instrument inside a professional host might improve scheduling, interoperability and the familiarity of the production controls. Those advantages are real. But an unconvincing sound does not become a convincing performance because it passes through a native plug-in. I was asking a question of sound and receiving an answer about software.

We had met a related problem in *The Door Is a Score*. A door closing is not merely an audio file assigned to a verb. Someone closes it; someone else may hear it. The distance matters, as do the hand, the surface, the force and the hesitation. A careful closing may be more disturbing than a violent one. A remembered closing belongs to another time. A door left open must not produce the mechanical event of a door being shut. Sound is an action heard from somewhere, not a list of samples.

A professional *Geräuschemacher* approaches this through performance. Synthetic sound deserves the same attention. Its source may be recorded, modeled, performed or built from oscillators. None of these methods is automatically superior. Each raises a material question: how does this sound begin, how does it move, what gives it character, and what remains in the air when it stops? A small noise may need hours of work before it has the appropriate weight. Some imperfections have to be removed; others make the event credible.

We therefore made a second, more controlled experiment. Instead of changing the entire musical idea again, we wrote two original Csound patches for the **same** short score: air, a low resonance, two metallic gestures and their disappearance. Both are sixteen seconds long, without a borrowed recording or jazz sample. This time the experiment could distinguish the consequences of synthesis and acoustic direction from changes in the underlying event sequence.

The literal patch triggers dry oscillators and broadband noise with largely uniform envelopes and little convincing room. The directed patch keeps the five timed events and the air field, but adds uneven attacks, unstable partials, changing perspective, resonances and a reverberant tail. Both were rendered from Csound at 48 kHz. Their overall RMS levels are approximately matched, but a whole-file RMS measurement is not a certification of equal perceived loudness.

The real night photograph gives our second comparison its proper context. Its illuminated lettering, the glass entrance, the dark street and the surfaces disappearing into shadow suggest an acoustic world. Perhaps there is distant traffic, an interior resonance or the fading presence of people who have already left. The photograph does not document those sounds: we imagine them. But its particularity makes that imagining credible in a way the synthesizers have not yet achieved.

[KINO-ILLUSTRATION:night-photograph]

Listen now to the same score in its two forms. The second is more developed, but it is still an audition rather than an approved musical master.

[SATZFUNK-CSOUND-COMPARISON:kino-same-score-a-b]

Below, the same two original Csound orchestras and scores are executable again as live instruments. The contrast can be heard as a fixed recording or as a new run of the source itself. The engine does not confer artistic acceptance: it exposes the difference between a technically running synthesizer and a sound that has earned its place.

[KINO-LIVE-SYNTHS:controlled]

The second render has measurable differences in attack, spectral movement, stereo presentation and decay. One can identify what changed and prove that the processing did something. But none of that determines whether the imagined room becomes credible. My judgment is that neither version yet earns the acoustic authority suggested by the images. The second synthesizer can sound more processed without sounding more substantial. Its increased complexity remains audible as technique rather than disappearing into a convincing event.

The two listening comparisons do different jobs. The first reveals the larger creative history: groove and sample machinery gave way to a quieter cinematic memory room, without resolving the problem of acoustic conviction. The second keeps a single authored score constant while changing the sound-making treatment. Both are valuable precisely because they expose an unfinished artistic decision. The later render must not erase the earlier attempt merely by arriving later.

In *The Ear That Learns*, a synthetic singing instrument produced different articulations and Ear helped measure them. A measurable change could support revision; it could not establish that a machine had learned to sing well. Likewise, a spectrum, transient plot or level measurement can identify physical differences in the Kino recordings, but cannot decide whether the result is moving, believable or right for the scene. Ear is an accountable observer, not a synthetic artistic director.

This is why our audio standard cannot end at successful rendering. **Technical acceptance** establishes that an instrument executes correctly, its sources are identifiable and its output can be reproduced. **Acoustic acceptance** examines the signal's material quality, noise, dynamics, transient behaviour and spatial perspective in the intended medium. **Artistic acceptance** happens when people listen in context and decide whether the sound belongs to the work. These judgments may disagree, and an intentionally damaged sound may be exactly right. The standard is not a demand that everything be beautiful; it is a refusal to pass an unnoticed limitation off as an artistic decision.

Csound Teatro, MIDI 2.0, Ear, Sing, Satzfunk and Reframe can help preserve the source, gesture, processing, listening conditions and distinct takes in relation. The original synthesizers and these later Csound auditions should remain independently identifiable, including their score addresses and the limits of the source evidence. A successful render receipt cannot promote a recording into an artistic master. Nor can a browser playback test certify its musical quality. That responsibility remains with the people listening and authorizing the work.

The pictures make the distance unusually clear. The architectural plate is an interpretation of a real building; the night photograph records its appearance. Each has a distinct claim and an intelligible relation to the place. A day/night architectural study might make the contrast more visible still: one building, one geometry, two conditions. It would not prove that either synthesizer had succeeded. The images should not lend borrowed credibility to the audio. Their strength makes the sound's weakness more conspicuous, which is precisely why they belong together here.

An atmosphere after a film may need very little: distant air, a low resonance, a phrase that comes once and does not return. That little is difficult to make convincing. Its silence must be listened to as carefully as its sounds. We have not yet made the acoustic equivalent of what the images already suggest. The four recordings are not four steps toward guaranteed improvement. They are evidence of work undertaken, possibilities tested and artistic expectations not yet satisfied.

The work remains unfinished. Its evidence need not be.

**A sound is not ready because the machine can make it. It is ready when the work can answer for it.**
