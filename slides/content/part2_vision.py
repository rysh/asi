"""Slides 18-29: what AGI is, and how scientific creativity could be built.

Sections 5-7 of the outline, plus the closing slide. As in part 1, every
bullet is the outline's own sentence, verbatim — including its arrows,
equals signs and parentheticals.
"""

from __future__ import annotations

from slides.model import (
    Bullet,
    Bullets,
    ContactBlock,
    Image,
    Slide,
)

B = Bullet


# --- 5. What Is AGI? -----------------------------------------------------

SLIDE_18 = Slide(
    number=18,
    title="General Does Not Mean Universal",
    kicker="5. What Is AGI?",
    body=Bullets(
        (
            B("General intelligence = adapting to situations the system has not "
              "encountered before"),
            B("Universal = capable of every possible task. That is not what "
              "“general” means"),
            B("Performing learned tasks without error is not AGI. That is "
              "execution, not adaptation", emphasis=True),
        )
    ),
    budget_sec=40,
)


SLIDE_19 = Slide(
    number=19,
    title="What Does General Mean?",
    body=Bullets(
        (
            B("The ability to change frames when the current frame does not work",
              emphasis=True),
            B("This is the substance of Condition 3 (Wisdom under Complexity)"),
            B("This may sound simple — but implementing it fundamentally means "
              "losing controllability", emphasis=True),
        )
    ),
    budget_sec=40,
    refs=("control_imposs",),
)


SLIDE_20 = Slide(
    number=20,
    title="The Distinction Between AGI and ASI",
    body=Bullets(
        (
            B("AGI is the adaptive application of existing knowledge (reframing)",
              emphasis=True),
            B("ASI is the generation of knowledge that does not yet exist "
              "(abduction)"),
            B("Rearranging and generating are different", emphasis=True),
            B("Details in the paper"),
        )
    ),
    budget_sec=35,
    refs=("main_paper",),
)


# --- 6. The Path to Scientific Creativity --------------------------------

SLIDE_21 = Slide(
    number=21,
    title="LLMs Cannot Judge the Truth of Their Own Discoveries",
    kicker="6. The Path to Scientific Creativity",
    body=Bullets(
        (
            B("A novel output does not exist in the training data"),
            B("LLM fact-checks it → inconsistent with existing data → judged false"),
            B("New ideas are killed by the system's own verification",
              emphasis=True),
        )
    ),
    budget_sec=40,
)


SLIDE_22 = Slide(
    number=22,
    title="The Error of “In the Beginning Was the Word”",
    body=Bullets(
        (
            B("“Truth is hidden in the world and can be discovered by the right "
              "method” = Hermeticism"),
            B("Supposedly refuted by the scientific revolution, yet it resurfaces "
              "again and again (dormant pathogen)"),
            B("Latest symptoms: “scaling will reach true intelligence”, “LLMs have "
              "a world model”"),
            B("Language is a compression of the world, not the world itself",
              emphasis=True),
            B("LLMs can only operate inside the compression"),
        )
    ),
    budget_sec=40,
    refs=("intention", "conservation"),
)


SLIDE_23 = Slide(
    number=23,
    title="What Advances Intelligence: The Generation of New Meaning",
    body=Bullets(
        (
            B("Gödel's incompleteness theorem: a system generates, through "
              "self-reference, truths it cannot prove internally"),
            B("Standard philosophical interpretation: infinite regression (the same "
              "incompleteness repeating)"),
            B("My interpretation: infinite progression (generating new meaning to "
              "resolve contradiction is not regression but progress through "
              "meaning-creation)"),
            B("Mathematics has been doing exactly this throughout its history"),
            B("Meaning has no conservation law — new dimensions of meaning can be "
              "generated without subtracting from any total. This is why infinite "
              "progression is structurally possible", emphasis=True),
        )
    ),
    budget_sec=50,
    refs=("gen_contradiction", "conservation"),
)


SLIDE_24 = Slide(
    number=24,
    title="Is Truth Found or Made?",
    body=Bullets(
        (
            B("Freud's Thanatos: theoretically dead. No neuroscientific basis. "
              "Judged “false” by every accepted method of verification",
              emphasis=True),
            B("Mishima Yukio's seppuku (1970): fused Eros and Thanatos in a single "
              "irreversible bodily act"),
            B("A theoretically dead concept changed its ontological status through "
              "action — an “undead concept”"),
            B("Is truth out there in the world, waiting for humans to discover it? "
              "Or is truth constituted through action?"),
            B("For those who believe the former, this is a deeply uncomfortable "
              "joke"),
            B("If the former is correct, scaling can reach ASI. If the latter, it "
              "is entirely impossible", emphasis=True),
        )
    ),
    budget_sec=60,
    refs=("mishima",),
)


SLIDE_25 = Slide(
    number=25,
    title="Going Outside Language",
    body=Bullets(
        (
            B("Meaning can be generated (cognitive side, no conservation law)",
              emphasis=True),
            B("But facts on the world side, governed by conservation laws, cannot "
              "be generated at will. Observation is the only access",
              emphasis=True),
            B("Meaning generation alone cannot distinguish itself from "
              "hallucination"),
            B("Verification on the physical side is required: experiment, "
              "observation, measurement"),
            B("Scientific creativity is achieved only when both the cognitive and "
              "physical layers are in place", emphasis=True),
        )
    ),
    budget_sec=50,
)


# --- 7. Synthesis --------------------------------------------------------

SLIDE_26 = Slide(
    number=26,
    title="One Possible Design",
    kicker="7. Synthesis",
    body=Image(
        key="loop6",
        lead=(
            B("Decompose the scientific process: observation → pattern recognition "
              "→ hypothesis generation (abduction) → experiment design → experiment "
              "execution → result evaluation → hypothesis revision → law "
              "formulation", emphasis=True),
        ),
        caption="Each step is individually attackable as engineering. Experiment and "
                "observation are not exclusive to humans. Humans enter at judgment "
                "and direction.",
    ),
    budget_sec=40,
)


SLIDE_27 = Slide(
    number=27,
    title="Experiment as a Service",
    body=Image(
        key="ecosystem",
        lead=(
            B("Connect laboratories, electron microscopes, and telescopes into the "
              "loop, and novel discoveries will follow", emphasis=True),
        ),
        caption="Real-world verification infrastructure: automated labs, experiment "
                "APIs, cloud-accessible robotic laboratories. Not expanding the "
                "inside of language — connecting to the outside of language.",
    ),
    budget_sec=40,
)


SLIDE_28 = Slide(
    number=28,
    title="Accelerating Novel Discovery",
    body=Image(
        key="compare",
        lead=(
            B("Humanity has always advanced science by building tools that explore "
              "beyond what is currently known", emphasis=True),
        ),
        caption="An AI that can do this is Superintelligence.",
    ),
    budget_sec=35,
)


SLIDE_29 = Slide(
    number=29,
    title="Thank You / Questions",
    body=ContactBlock(
        summary=(
            "Speed and Collective Intelligence are already achieved. Scientific "
            "Creativity and General Wisdom under Complexity are not, and they are "
            "two independent axes — each requires its own design. ASI = the ability "
            "to continuously make novel discoveries and inventions, update "
            "knowledge, and surpass humans."
        ),
        lines=(
            ("Contact", "franny.philos.sophia@elanare.jp"),
            ("ORCID", "0009-0004-7089-5265"),
            ("OpenReview", "https://openreview.net/forum?id=lLWeptkTPH"),
            ("Referenced papers", "DOIs on individual slides"),
        ),
        closing="Questions welcome — and counterexamples are especially welcome.",
    ),
    budget_sec=30,
)


PART2: tuple[Slide, ...] = (
    SLIDE_18, SLIDE_19, SLIDE_20, SLIDE_21, SLIDE_22, SLIDE_23, SLIDE_24,
    SLIDE_25, SLIDE_26, SLIDE_27, SLIDE_28, SLIDE_29,
)
