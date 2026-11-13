# If Only

*The Contexter and the Simultaneous Stage*

*Fountain Coach spent its early development creating ways for software to call other software. Now an AI assistant can operate a terminal that already contains many of the tools we once wrapped in elaborate services. Much of the infrastructure is suddenly within reach. Yet the work is not finished. What remains is to bring the instruments developed along the way into a shared practice, across several machines, without surrendering the purposes for which they were made.*

There they were, sitting quietly in the terminal: `hcloud`, `aws`, `gh`. The Hetzner command-line interface, Amazon's collection of cloud-management tools, and GitHub's own means of inspecting and changing its repositories. A few more inquiries established that the machines were available, that the domain registration could be found through one provider while its nameservers belonged to another, and that the repositories still contained the long history of our attempts to make all this manageable. The commands required no introduction. They already knew how to communicate with the services for which they had been written.

Now imagine granting a language model permission to call that terminal. It can inspect a server, examine a repository, prepare a change, run a test, perhaps even deliver a new version of a website. The distance between describing an intention and carrying it out seems to collapse. All those interfaces we once constructed, the services that called other services, the wrappers around publicly documented APIs—what had we been doing? We had spent an astonishing amount of effort preparing access to capabilities that were already there.

For a moment, the conclusion is irresistible. Job done.

If only.

The domain can be registered with one company while its DNS is administered by another. A command that succeeds may have acted on the wrong account, the wrong machine or the wrong version of a service. A newly built application may be perfectly usable for an experiment and quite unsuitable for the work I depend on every morning. A manuscript may survive a successful deployment while the page that contains it becomes unreadable. And an assistant can report that everything has happened without having looked at the place where the result ought to appear.

The terminal is powerful. It does not know why I am here.

I have begun to suspect that this small distinction contains much of the story of Fountain Coach.

## The construction of access

The Git history returns me to June 2025. A manifesto had appeared, followed almost immediately by a Swarm Orchestrator, a service for generating clients from OpenAPI specifications, and another for deployment. The names are revealing. We were trying to make software describe its own capabilities well enough that other software could discover and use them. A deployment should not depend on someone remembering a sequence of shell commands. An application should not require a newly handwritten client for every service it encounters. The machine-readable description was intended to open a passage between intention and operation.

In July, the provisioning work acquired a particularly recognizable form. A Python script that had helped establish cloud infrastructure gave way to an API wrapping Hetzner's own OpenAPI specification. We had been configuring machines and DNS; now we wanted the procedure to become something another component could address. The pattern repeated in different languages and environments. We built generators, kernels, adapters, command runners and services for services. Some were experiments, some were usable components, some grew into things we continued to rely upon. They did not all mature at the same pace.

Looking back, I recognize a certain extravagance. We constructed machinery around operations that already existed. Sometimes the new layer made an operation safer or more intelligible. Sometimes it merely gave an existing command another name and another address. At the time, the distinction was not always easy to see. We were learning what the systems could do by trying to bring them into conversation with one another.

I have never understood the developer solely as the person who types an implementation into an editor. My work increasingly involved conceiving the relationships: deciding what ought to exist, what one component should be allowed to ask of another, and what sort of result would justify saying that something had been accomplished. I worked through descriptions, conversations, specifications, tests, failures and revisions. The source code accumulated around these decisions. So did the names of things that sometimes turned out to have been temporary ways of thinking.

An early README was signed *Contexter*. I had almost forgotten how plainly the word stated the ambition. Not a programmer commanding every operation from one privileged console, but someone who gathers circumstances, gives them form and makes their relationships available for action. The context was never merely the information preceding a prompt. It included a machine, a place, an unfinished work, an available instrument and a reason to employ it.

Then the work began to change what the machines were being asked to do.

We were no longer concerned only with keeping services running. There was music, and the problem of making a score executable. MIDI 2.0 became a language through which instruments and applications could recognize one another. Csound opened a way to shape sound. A semantic browser could encounter actual pages rather than merely inspect their descriptions. A persistent store could remember operations and their outcomes. Toolsmith addressed the execution of external tools. Teatro gave another kind of form to the relationship between a written instruction and an event.

The repositories multiplied. Their names began to resemble the departments of a theatre more than the directory of a conventional application. Yet I did not want a theatre made of software for its own sake. I wanted to write, hear, compose, read and direct. Every time the infrastructure became particularly elaborate, that original purpose returned as a rather uncomfortable question. What is this making possible that I could not otherwise do?

Reframe grew from that question. It was conceived as a home for the writer, a place in which a manuscript could remain a manuscript while acquiring other possibilities: reading aloud, composition, semantic navigation, perhaps a theatrical performance whose means had not yet been settled. Its `/commands` were not intended to turn the writer into the administrator of a computer. They offered ways of addressing work that had previously required a journey through applications, tools and files.

But a writer's home cannot contain the entire world in which a work takes place.

## The company assembles

My writing had meanwhile acquired a company. There was Zork, whose sentences sometimes followed an impulse farther than the subject seemed to permit. Bee, with another patience for what had happened and what remained present. N., whose attention could enter a scene through a surface, a movement or an unexpected color. And Vergil, the reader, whose voice could return a written passage to time.

They did not arrive as software features. Their existence in the work preceded the question of how the work might be rendered. I could write a passage for Bee, hear its movement change when read aloud, discover that a page turned in the wrong place, and return to the text. An image might belong to N.'s passage not because an algorithm had selected a convenient illustration, but because the image and the sentence had developed together. Zork could carry a thought into another day without requiring that every part of the journey be reduced to an instruction. Vergil might reveal a sentence's difficulty simply by speaking it.

The instruments were being developed in response to these encounters. They were not the company itself, and they could not decide what its members had to say. They provided means by which a written work might become audible, visible and independently encounterable.

A publishing instrument, for instance, could assemble a manuscript and its illustrations into a book. But the page still had to be read. We learned that rather painfully. A technically successful illustration insertion could leave an ugly interval of white space before the next passage. A correctly delivered book could open with its editorial summary typeset as if it belonged to the author's first paragraph. A rendered figure could contain all the declared objects and still fail to make its meaning visible.

These failures did not persuade me that we needed yet another system to describe systems. They brought us back to the book. We corrected the composition, opened the page and looked again. The work itself provided the occasion for development.

This is where the history becomes unexpectedly circular. We began by wrapping existing interfaces so that other software could operate them. Now the language model can reach a terminal directly, and much of the wrapping appears unnecessary. At the same time, we possess capabilities that did not exist when the wrapping began. The publishing instrument is no longer merely a convenient call to an external service. Neither is a Reframe command simply a disguised shell instruction. These are procedures shaped by what we have learned about our work.

I would be quite willing to retire a wrapper whose only accomplishment is to repeat a command that a governed host can already execute. Keeping it because we once built it would mistake the history of development for its purpose. But I would not discard an instrument that embodies something we actually need: the composition of a page, the continuity of a manuscript, the rendering of sound, or the ability to recognize that an operation has failed.

The difference is increasingly apparent. We do not need to preserve every piece of scaffolding. We need to inhabit what has been built.

## Simultanbühnen

The term comes from theatre history: *Simultanbühnen*, simultaneous stages. Several places of action remain present within one theatrical arrangement. What happens in one place need not erase the others. The audience can understand that the world of the work exceeds the particular action receiving attention.

I like the term because it does not require me to invent a single machine large enough to contain Fountain Coach. I already have the places.

There is a Mac on which manuscripts, repositories and working materials can be encountered. There is an Ubuntu host, capable of running processes independently of the screen in front of me. There is an iPad on which Reframe can become a place for writing and reading, and an iPhone whose particular gestures and resources should not be mistaken for those of a desktop computer. Beyond the local machines are remote hosts, domains and services. A registrar can maintain ownership of a name, another service can answer DNS requests, and a server can deliver what the name promises. None of these needs to become the property of one enormous application.

The work can pass among them. A manuscript changes on the Mac, an admitted instrument composes an edition on Ubuntu, and the page is opened on the iPad. The reading may suggest another revision. A sound begins in a score and becomes audible through an engine running in a suitable environment. A Reframe command can request work that the Host knows how to perform, without pretending that Reframe must itself become the remote computer.

The places are not identical, and that is their advantage. They can retain their different powers.

There is another distinction, familiar from rehearsal, that we have sometimes made unnecessarily bureaucratic. A new possibility is developed. A particular composition is rehearsed under conditions close enough to its intended use that failure becomes informative. When we rely on the result for our actual work, it is in production. These are not necessarily three servers or three separate copies of everything. They are three different responsibilities toward the same undertaking.

An instrument can be under development while another is already in production. The private reading of a manuscript can be a production event. The performance of a synthesizer need not wait for a commercial release. A website may be staged because we are still checking its page composition, even while the public edition continues to be read. We have been inclined to imagine production as something that begins when an external audience arrives. But there is already someone here who needs the work to function.

I do.

This changes the question I ask of Fountain Host. It is no longer primarily how many tools it can expose to a language model. I want to know which of our existing instruments it can execute, which of Reframe's commands can address them, and what remains specific to the writer's experience on the iPad. I want the Host to use the powers of its machine without appropriating the author's role. I want an unavailable capability to remain unavailable rather than be simulated in conversation. And I want the result of an action to return to the place where it matters.

If a cloud command creates a machine, that machine must actually exist. If a DNS change is made, the authoritative nameservers must answer accordingly. If a book is published, the book must open. If Vergil reads a passage, there must be a reading to hear. These are not demands for an elaborate philosophy of verification. They are the ordinary conditions under which anyone would say that something happened.

## The next performance

I find myself back at the terminal, looking at the same familiar tools. They no longer appear as the beginning of another infrastructure project. They are already available. An LLM with permission to call them is an extraordinary convenience, perhaps enough to make a surprising portion of our earlier scaffolding obsolete. The remaining question is not how to surround them with a new architecture before allowing anything to occur.

It is what we want to do next.

I would like to continue writing, to open Reframe and find the work where I left it. I would like to hear a passage without producing a second text merely to follow the voice. I want to move between an illustrated page and its spoken reading without losing my place. I want the instruments we developed for sound and theatrical composition to be available when the work calls for them, and silent when it does not. I want a publishing process that can tell me what it has delivered, without requiring me to spend the afternoon supervising the server.

Some of these powers are already working. Others are only partly admitted, or remain available in development without having earned a place in the work I depend on. The Simultanbühnen will not be completed by drawing another comprehensive diagram of them. They will emerge as we bring the capabilities into use, one relationship at a time, preserving those that prove necessary and relinquishing those that merely repeat what the machines can already do.

The developer in this account is not standing outside the performance, managing an invisible machinery on behalf of someone who may eventually arrive. I am already involved in it. The text I write, the page I examine and the sound I hear are reasons for the instruments to exist. Bee, Zork and N. belong to the unfolding work; Vergil gives it another duration. The machines have their places, but they do not supply the occasion.

And so the seductive announcement—*job done*—is both premature and strangely encouraging. Much of what we once struggled to make callable can now be called. We have accumulated instruments along the way, sometimes without yet giving them the ordinary life for which they were intended. The work before us is neither another beginning nor a final deployment. It is the continuation of a journey that has acquired its means.

The tools are there. The company is assembled. The stages are within reach.

What happens on them is still ours to discover.
