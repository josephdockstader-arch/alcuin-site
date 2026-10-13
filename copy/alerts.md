# Developments board -- the "What has changed recently" strip on the
# guides page. Reverse chronological, newest first, capped at 8 on the
# page (load_alerts caps at 14); older items stay here as the running record.
#
# TWO RULES THE BUILDER ENFORCES, so neither depends on anyone
# remembering them:
#   1. A `url` is preferred but NOT required (Joseph, 2026-09-18): a
#      figure we can attribute in words does not need a hyperlink. But
#      `source` is not optional -- an unattributed number has no
#      business on the page.
#   2. `draft: yes` never renders. Park an item here the moment you
#      hear about it; it reaches the site only when the link has been
#      opened and the facts checked.
#
# Fields:
#   date      ISO date the thing happened. Sorts the board.
#   display   how the date should read.
#   where     who did it -- jurisdiction or body. Shown as the tag.
#   headline  what happened, under about twelve words, no hype.
#   detail    one sentence of what it actually does.
#   source    who to credit in the link text: "Read it at <source>".
#   url       the outbound link. Issuing body first, then reporting.
#   guide     optional slug of one of our guides.
#   guide-label  link text for that guide.
#   stat      optional. A figure rendered large above the headline,
#             for rows that report where things stand rather than
#             something that happened.
#   draft     yes = held back.
#
# Every live URL below was opened and checked on the date noted in its
# block. Re-check before any major site update; outbound links rot.
# 2026-09-29 sweep: all 13 live URLs re-opened (openai.com returns 403
# to curl but loads in a browser). Four rows added, three parked as
# drafts, Oklahoma row enriched. See the per-row comments.

stat: 9 of 35
date: 2026-09-18
display: September 2026
where: Nationally
headline: Nine of those states actually require a district to act
detail: The rest publish advice. Counting only binding duties on districts to adopt a policy, the nine are Ohio, Tennessee, Maryland, Idaho, Oklahoma, Utah, North Carolina, Virginia, and Arkansas. Florida's rule was approved in September and is not yet filed. Louisiana and Nevada bind schools in other ways without requiring a policy, and Texas and Colorado may reach districts through general public-sector AI law. Arizona requires nothing.
source: our own review of each state's statute or rule, September 2026
url:
guide: do-schools-need-an-ai-policy
guide-label: do schools need a policy
# Counted from primary sources, not trackers. THE CRITERION IS
# "BINDING POLICY DUTY ON DISTRICTS" and it is applied consistently --
# an earlier version mixed a date requirement in and then broke it,
# which is what made the list arbitrary. Under this rule:
#   IN: a statute or adopted rule requiring districts to ADOPT A
#       POLICY. Dated or not -- Virginia's has no deadline and still
#       counts, which is why Arkansas (also undated) can count too.
#   OUT: Louisiana -- Act 782 makes principals DISTRIBUTE information
#       about AI-image crimes. Real, binding, not a policy duty.
#   OUT: Nevada -- AB 406 BARS a use (AI performing the mental-health
#       functions of a counselor, psychologist or social worker under
#       NRS 391.293/294/296). A prohibition, not a policy duty.
#   OUT: Texas -- SB 1964 binds "local governments" and the word
#       "school" appears NOWHERE in the bill analysis. Arkansas is in
#       because Act 848's entity list explicitly names "a public
#       school district" and "an open-enrollment public charter
#       school." Naming beats inferring; that is the whole line.
#   OUT: Colorado -- same inference problem. SB 26-189 binds
#       "deployers" and never says a district is one.
#   PENDING: Florida -- approved 2026-09-16, notice of change
#       2026-09-18, not filed. It is named in the detail, not counted.
# RECHECKED 2026-09-29: unchanged. Florida still not filed (flrules
# shows Change 9/18, no Final). Utah's proposed R277-334 (below) does
# not move the count; Utah is already in via HB 273.
# Recheck Florida early Nov. Maryland's clock runs 120 days from a
# release the state never dated and may already have run.
# STILL OPEN: Minnesota is not a proven negative (two 2026 session-law
# chapters containing "artificial intelligence" went unread), and New
# Mexico required schools to ADMINISTER an AI reading assessment from
# 2025-26, which would qualify if it sits in an adopted rule.

---

date: 2026-09-16
display: September 16, 2026
where: Florida
headline: Florida's State Board approves binding AI rules for schools
detail: Districts and charters would have to amend their internet safety policies by July 1, 2027. Parents must opt a child in before an AI instructional tool is used, and a comparable non-AI alternative is the default for anyone who does not. Tools for Voluntary Prekindergarten through grade 5 face added review, and AI built to meet a student's social or emotional needs is barred. The rule was approved with changes and has not yet been filed as final.
source: the Florida Administrative Register
url: https://www.flrules.org/gateway/ruleNo.asp?id=6A-1.0957
guide: what-an-ai-policy-should-include
guide-label: what a policy should include
# CORRECTED 2026-09-18. The first version said "notify parents and
# offer a non-AI alternative on request," which INVERTED the consent
# default. Rule 6A-1.0957(3)(e)1.e requires parents to "opt their
# child INTO using the tool" and makes the comparable non-AI tool the
# path "IF THEY DO NOT OPT THEM IN." A district reading the old
# wording would have defaulted students into AI and waited for
# objections -- out of compliance on the most-watched provision in
# the rule. This was the single worst error on the board.
# Also fixed: "July 2027" -> July 1, 2027. Grade band named as VPK
# through 5, since VPK is a distinct Florida program. The companion
# bar covers AI meeting social or emotional needs "including Social
# Emotional Learning," which is broader than "companion AI."
# NOT YET REFLECTED: the 2026-09-18 notice of change broadened the
# definition to agentic AI, added supervision, activity logs and a
# vendor-independent kill switch, barred AI as decision maker without
# human review, and added incident disclosure. Add when it is filed.
# RECHECKED 2026-09-29: still not filed. flrules history shows Change
# 31384852 (9/18/2026) and no Final row after the 2023 original; FAC
# still says effective 8/22/2023. Notice of Change text is in FAR Vol.
# 52 No. 182 pp. 4056-57 (flrules.org/faw/fawdocuments/
# fawvolumefolders2026/52182/52182doc.pdf). Verbatim from it: districts
# and charters "must, by July 1, 2027, adopt and implement an
# amendment to their internet safety policy."
# DO NOT call this law.

---

date: 2026-09-02
display: September 2, 2026
where: New York City
headline: New York City bars student generative AI through grade 8
detail: A one-year moratorium covers roughly 600,000 students from 2-K through grade 8, with carve-outs for assistive technology, multilingual learners and career programs. High school access is five supervised pilots reaching about five percent of high schoolers, not general availability. Companion chatbots are barred in every grade. Staff may use AI for planning and administration, but not for grading, behavior monitoring, or placement, promotion and graduation decisions.
source: NYC Public Schools
url: https://www.schools.nyc.gov/about-us/policies/guidance-on-artificial-intelligence
guide: do-schools-need-an-ai-policy
guide-label: do schools need a policy
# ATTRIBUTION: NYC PUBLIC SCHOOLS' policy, signed by Chancellor Kamar
# H. Samuels, announced jointly with Mayor Mamdani. Not "the mayor's
# ban."
# CORRECTED 2026-09-18: the first version read as though every high
# school had five tools available. They are PILOTS -- five classes per
# school at most, about 50,000 students, roughly 5% of the district.
# Carve-outs added: "bars" alone was too absolute.
# The ~600,000 is the City's own figure. Do not pair it with the
# ~799,000 total register. "2-K" is correct and is not a typo for 3-K.
# "Companion chatbots" is verbatim from the release and is NOWHERE
# defined. Do not supply a definition.

---

date: 2026-09-02
display: September 2, 2026
where: Los Angeles
headline: Los Angeles blocks generative AI on district student devices
detail: The second-largest district in the country blocked generative AI on district-issued Chromebooks and tablets in every grade for 2026-27, affecting about 378,000 students in district-operated schools. Earlier policy had allowed supervised access from age thirteen. The change was made administratively rather than by board vote, and an ad hoc committee reports recommendations at the end of the school year.
source: LAist
url: https://laist.com/news/education/lausd-students-barred-artificial-intelligence-tools
guide: ai-and-thinking
guide-label: AI and thinking
# CORRECTED 2026-09-18, three errors:
#   1. "all student devices" -> district-issued only. The block runs
#      through Lightspeed filtering; nothing covers personal devices.
#   2. "reversing a policy" implied a board decision. There wasn't
#      one. Board members learned of it at the ad hoc committee's
#      first meeting; Nick Melvoin said it "didn't really come from
#      the board." Now "administratively rather than by board vote."
#   3. "before the year ends" read as December 2026. The committee
#      reports at the END OF THE 2026-27 SCHOOL YEAR, about June 2027.
# 378,000 is district-operated schools only; LAUSD including
# independent charters is about 500,000. Non-generative AI (adaptive
# learning, captioning, translation) stays on.
# There is no primary document -- no board resolution, no press
# release. That absence is itself the finding.

---

date: 2026-09-10
display: September 10, 2026
where: California
headline: California bars school software from training AI on student data
detail: AB 1159, signed September 10, amends the state's K-12 and early-learning student privacy acts so that an operator may not use covered information, including persistent unique identifiers, to train a generative AI system or develop an AI system. It also extends coverage to services designed or marketed for school purposes and to companies working on an operator's behalf, and it lets a pupil harmed by a violation sue. A companion act for higher education takes effect July 1, 2027.
source: the California Legislature
url: https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202520260AB1159
guide: ai-and-ferpa
guide-label: AI and FERPA
# ADDED 2026-09-29. Chapter 182, approved and filed 2026-09-10. Opened
# the chaptered text on leginfo. Digest verbatim: "prohibit an operator
# from using covered information, as defined, including persistent
# unique identifiers, created or gathered by the operator's site,
# service, or application to train a generative artificial
# intelligence system or service or develop an artificial intelligence
# system." Coverage change verbatim: "designed OR marketed" (was "and").
# The statute says "actually harmed"; the row drops "actually" (house
# blacklist) without changing the meaning.
# This is a STATUTE, unlike the Florida and Utah rules on this board.
# Signed the same day: SB 1119 (companion chatbots, mostly operative
# July 1, 2027), SB 1128 (kindergarten take-home devices, CDE model
# device policy), AB 2071 (digital wellness instruction). Not rowed;
# AB 1159 is the one that binds ed-tech vendors directly.
# TRAP: AB 1064 was vetoed in October 2025. Search results conflate it
# with this package. Nothing K-12/AI was signed or vetoed 9/15-9/30.

---

date: 2026-09-09
display: September 9, 2026
where: Vendors
headline: Microsoft and the AFT announce an enforceable AI privacy standard for schools
detail: The National AI Safety and Privacy Standard, negotiated with the American Federation of Teachers and its New York City affiliate, says student and educator data will not be used to train AI models, sold or repurposed, that AI will not make decisions without human oversight, and that companies must give families plain-language information about how their tools work. A district can write the protections into its Microsoft customer agreement, which is what makes them enforceable. Microsoft says it will extend the agreement to every district in the country.
source: Microsoft
url: https://news.microsoft.com/source/2026/09/09/aft-uft-and-microsoft-announce-national-ai-safety-privacy-standard-for-schools-to-protect-students-families-and-educators/
guide: questions-to-ask-an-ai-vendor
guide-label: questions to ask a vendor
# ADDED 2026-09-29. Opened the Microsoft Source release. Verbatim:
# "U.S. school districts can incorporate these protections directly
# into their Microsoft customer agreements, making them contractually
# enforceable." Smith: "we'll extend this agreement to every school
# district across the country." Data verbatim: "will not be used to
# train AI models, sold or repurposed."
# TRAP: Forbes (9/9) reports a November 1, 2026 effective date for
# districts with existing agreements. THAT DATE IS NOT IN THE PRIMARY
# RELEASE. Do not add it until Microsoft's own fact sheet says so.
# Also unresolved in the primary text: whether protections apply
# automatically or only when a district opts them into its contract.
# The row says "can write," which is what Microsoft wrote.
# A 9/16 Microsoft blog restated the standard and said Copilot Chat is
# default-off for K-12 students. Not rowed separately.

---

date: 2026-09-01
display: September 1, 2026
where: Utah
headline: Utah's proposed AI governance rule is open for comment until October 1
detail: Rule R277-334 would require every district and charter to adopt a classroom technology and AI policy before July 1, 2027, with the state board's model policy applying by default to any that does not. Students could not use generative AI for academic work unless an educator authorizes it for a specific instructional purpose, educators could not use it to grade work on its own, and what the rule calls high-risk AI interaction could not be used with students. The earliest the rule can take effect is October 8, 2026, and a first draft of the model policy is already posted.
source: the Utah State Board of Education
url: https://schools.utah.gov/adminrules/administrativerules/rulesinprocess
guide: what-an-ai-policy-should-include
guide-label: what a policy should include
# ADDED 2026-09-29. Opened USBE's Rules in Process page (Proposed
# Rules tab): "September 1, 2026 - Number 2026-17 / Approved by the
# Board: August 6, 2026 / Public Comments accepted until: October 1,
# 2026 / First Possible Effective Date: October 8, 2026," and the list
# includes "R277-334. Classroom Technology and Artificial Intelligence
# Governance (New)." Rule text verified in the Utah State Bulletin
# 9/1/2026 PDF (rules.utah.gov/wp-content/uploads/b20260901.pdf):
#   R277-334-4(1): "Before July 1, 2027, an LEA shall adopt: (a) the
#     Board's model policy ... or (b) a locally adopted policy"
#   R277-334-4: "the Board's model policy shall serve as the default
#     policy for the LEA"
#   R277-334-6(5): "An LEA shall prohibit student use of generative
#     artificial intelligence for academic work unless authorized by an
#     educator for a specific instructional purpose."
#   R277-334-6(4)(e): "refrain from using generative artificial
#     intelligence to independently grade student work."
#   R277-334-6(8): "High-risk artificial intelligence interaction may
#     not be used with students."
# Draft model policy: "Draft.V1 Utah Instructional Technology and
# Artificial Intelligence Model Policy and Implementation Resource,"
# utah.gov/pmn/files/1482215.pdf, opened. Verbatim: "If an LEA fails to
# adopt or create Instructional Technology and AI policies ... the
# Model Policy will become their default policy."
# NOT VERIFIED BY US, from the research pass only: the USBE Standards
# and Assessment Committee gave the draft preliminary approval 9/4;
# full board hears it in October; statutory deadline to publish is
# Dec 1, 2026. Kept out of the row.
# This is a PROPOSED RULE, not law. HB 273 is the law (see the March
# 18 row). Recheck after Oct 8 for the effective date, and after the
# October board meeting for the model policy.

---

date: 2026-09-01
display: September 1, 2026
where: Washington, D.C.
headline: The District of Columbia issues a model AI policy for school staff
detail: The Office of the State Superintendent of Education released its first model policy on staff use of AI, offered as guidance that each local education agency may adapt or set aside. It sorts uses into three tiers. Surveillance of students and staff, discipline decisions, teacher evaluations, and eligibility for IEPs or Section 504 plans are off limits. Drafting IEP language and grading student work are allowed with safeguards, and lesson planning and school communications are allowed with a person reviewing. A February survey found 45 percent of the city's local education agencies had a staff AI policy.
source: the Office of the State Superintendent of Education
url: https://osse.dc.gov/release/osse-releases-ai-model-policy-guide-responsible-staff-use-schools
guide: ai-policies-vs-guidelines
guide-label: policies versus guidelines
# ADDED 2026-09-29. Opened the OSSE release. Verbatim: "offered as
# guidance only -- not legal advice"; "just 45% of LEAs had established
# a staff AI policy"; red tier lists "physical surveillance of students
# and staff, student discipline decisions, evaluations of teacher
# performance, and determining eligibility for individualized
# education programs (IEPs) or Section 504 accommodations"; yellow
# includes "drafting IEP language, reviewing and grading student work."
# TRAP: some coverage says grading and IEP drafting are BANNED. They
# are yellow (allowed with safeguards). Staff use only; no student
# provisions; no deadline.

---

date: 2026-08-28
display: August 28, 2026
where: Vendors
headline: Anthropic opens free Claude for Teachers to US districts
detail: US schools and districts can put staff into one centrally managed organization under a single set of K-12 terms, with single sign-on, role-based access and domain claiming. Qualifying organizations that sign up by June 30, 2027 get a full year of free access.
source: Anthropic
url: https://claude.com/blog/claude-for-teachers-now-available-for-schools-and-districts
guide: questions-to-ask-an-ai-vendor
guide-label: questions to ask a vendor
# CORRECTED 2026-09-18: "U.S." was missing -- the offering is US-only.
# And the free-period sentence now uses ANTHROPIC'S OWN construction,
# "sign up by June 30, 2027 get a full year of free access," instead
# of our paraphrase "a full year free from the date they enroll."
# The paraphrase was probably right but no Anthropic source says the
# year starts at enrollment. On a page advising districts about a
# deadline, use their words.
# Domain claiming added -- the most useful feature for a district
# whose teachers already signed up individually.
# Free is not unlimited: usage limits match individual accounts and
# overage billing is off unless an admin opts in.

---

date: 2026-08-26
display: August 26, 2026
where: Vendors
headline: OpenAI expands free ChatGPT for Teachers to more districts
detail: Fifty-five more school systems across twenty states add over 100,000 educators and staff, bringing OpenAI to more than 100 K-12 organizations in thirty states covering over 300,000 educators and staff. The company also announced a sixteen-state data privacy agreement through the Student Data Privacy Consortium. Accounts are for educators and staff, not students, and OpenAI says the tool stays free for verified US K-12 educators through June 2028.
source: OpenAI
url: https://openai.com/index/bringing-chatgpt-for-teachers-to-more-us-school-districts/
guide: questions-to-ask-an-ai-vendor
guide-label: questions to ask a vendor
# CORRECTED 2026-09-18: the 300,000 was attached to the 55 systems in
# 20 states. It belongs to the cumulative base -- 100+ organizations
# across 30 states. Two different numbers in the same announcement.
# Added the National Data Privacy Agreement, which for a procurement
# audience beats the headcount.
# JUNE 2028 IS CORRECT AND IS A TRAP: the November 2025 launch said
# June 2027 and a lot of still-indexed coverage repeats it. Anyone
# "correcting" this from a quick search introduces the error.

---

stat: 35 + PR
date: 2026-08-21
display: August 2026
where: Nationally
headline: Thirty-five states and Puerto Rico publish AI guidance
detail: The count covers guidance published for schools statewide, from a short advisory to a full framework, and it is contested: other trackers say thirty-two or thirty-seven depending on whether they count documents issued by someone other than the state education agency. Arizona and Utah are both on this one.
source: AI for Education state guidance tracker
url: https://www.aiforeducation.io/ai-resources/state-ai-guidance
guide: ai-guidance-arizona-utah
guide-label: what Arizona and Utah have published
# CORRECTED 2026-09-18: was "official state guidance," which
# contradicted our own Arizona row -- Arizona's document is published
# by a university, and Ballotpedia's tracker omits Arizona for exactly
# that reason. Now "published for schools statewide," and the contest
# between trackers is stated rather than hidden.
# Verified by opening the tracker: "35 states (and Puerto Rico) now
# have official guidance or policy on the use of AI in K12 schools.
# (Updated 8/21/2026)." Not updated since.
# COUNTING TRAP: the page shows 38 state headings; three (NJ, NY, TN)
# are asterisked as NOT having state guidance. 38 - 3 = 35.
# The tracker's Arizona summary still describes v25's structure and
# has not ingested the June 2026 rewrite.
# RECHECKED 2026-09-29: page unchanged, still "Updated 8/21/2026."

---

date: 2026-07-07
display: July 7, 2026
where: North Carolina
headline: North Carolina requires an AI policy from every school unit
detail: The state budget act requires the governing body of every public school unit to adopt an AI policy by June 30, 2027, after the education department develops a model by December 31, 2026 and makes it available by January 15, 2027. Teachers in districts, charters and lab schools must finish ten hours of state AI training by June 30, 2028.
source: the North Carolina General Assembly
url: https://www.ncleg.gov/Sessions/2025/Bills/Senate/PDF/S257v8.pdf
guide: what-an-ai-policy-should-include
guide-label: what a policy should include
# S.L. 2026-41 (SB 257, budget act) section 7.39. Approved 7 Jul 2026.
# CORRECTED 2026-09-18, wrong in BOTH directions in one sentence:
#   - The POLICY duty was stated too narrow. Section 7.39 creates it in
#     five places: local boards, charter schools, regional school
#     boards, lab school chancellors, AND the boards of trustees of the
#     schools for the deaf and blind. The statute says it collectively:
#     "Governing bodies of public school units shall adopt." Now uses
#     that phrase.
#   - The TRAINING duty was stated too broad. 7.39(p) names only
#     "local school administrative units, charter schools, or
#     laboratory schools." Teachers at regional schools and the
#     schools for the deaf and blind must have a policy but are not
#     covered by the training mandate. Now names the three.
# Also: two department dates, not one -- DEVELOP by Dec 31, ensure
# ACCESS by Jan 15. Modules are from the Friday Institute at NC State,
# minimum 10 hours, self-paced.
# Verified directly against the enrolled act.

---

date: 2026-06-19
display: June 19, 2026
where: Arizona
headline: Arizona's governor vetoes a school AI instruction bill
detail: HB 4005 would have required instruction on the ethical and educational uses of AI in grades 3, 6, 8, 10 and 12 from 2027-28, binding districts while leaving charter schools out. The veto letter objected to setting different requirements for charters and districts, and said academic content should be left to experts rather than politicians. A second bill on student AI use policies did not pass.
source: the Office of the Arizona Governor
url: https://azgovernor.gov/office-arizona-governor/news/2026/06/governor-katie-hobbs-legislative-action-update-0
guide: ai-guidance-arizona-utah
guide-label: what Arizona and Utah have published
# One of two items the adversarial check passed clean. Veto letter
# verbatim: "I do not support establishing different instructional
# content requirements between charter schools and school districts.
# Furthermore the development of academic content and requirements
# should be left to experts, not politicians forcing mandates on
# teachers."
# REFINED 2026-09-18: added "while leaving charter schools out," since
# a reader could otherwise infer charters faced a STRICTER rule. The
# bill bound "each school district" only.
# HB 4040 is described narrowly -- its actual subject is
# academic-integrity policy to detect unauthorized student AI use, and
# it covered universities too. It died in House Rules at sine die.

---

date: 2026-06-02
display: June 2, 2026
where: Utah
headline: Utah makes Gemini for Education available statewide
detail: The state board says the tool reaches Utah's more than 650,000 students and, by its count, 28,000 educators from 2026-27, with each district deciding for itself whether to adopt it. Utah is requiring restrictive classroom technology policy and offering a statewide AI assistant at the same time.
source: the Utah State Board of Education
url: https://www.schools.utah.gov/publicrelations/_publicrelations_/_2026/USBEAdoptsGeminiEducationPressRelease.pdf
guide: questions-to-ask-an-ai-vendor
guide-label: questions to ask a vendor
# CORRECTED 2026-09-18. USBE's release says 680,000 students, and
# USBE'S OWN FALL 2025-26 COUNT IS 656,311 -- down 11,478, the third
# consecutive annual decline. 680,000 described Utah around 2022.
# Repeating a source's stale number is still publishing a wrong
# number, so this says "more than 650,000."
# The 28,000 educator figure could not be verified against any current
# official total (NCES shows 31,164 FTE for 2022), so it is attributed
# to USBE rather than asserted.
# "adopts statewide" -> "makes available statewide": USBE's own
# headline says "Adopts" but its body quotes Superintendent Hart
# saying "Local education agencies maintain full local control over
# whether to adopt these tools." We should not repeat a contradiction.

---

date: 2026-06-08
display: June 2026
where: Arizona
headline: Arizona's schools guidance is rewritten around AI literacy
detail: Version 26.01 is a full rewrite subtitled "A Call for AI Literacy," promoting literacy from one section to the organizing frame. It is published by the Arizona Institute for Education and the Economy at Northern Arizona University, with Department of Education staff among its authors. The Department's own AI page does not link it.
source: Arizona K12 AI Guidance
url: https://www.azk12.ai
guide: ai-guidance-arizona-utah
guide-label: what Arizona and Utah have published
# CORRECTED 2026-09-18: was "the state's guidance," which is the
# claim our own 35-state row had to be softened to match. Verified by
# opening azed.gov's AI page in a browser (it blocks every automated
# fetcher): it links the U.S. Department of Education's 2023 report
# and says NOTHING about the NAU document. So ADE neither publishes
# nor points to it, while two ADE staff are core authors. The row now
# says exactly that, which is more interesting than either simple
# version.
# "from governing tools to" was dropped: v25.01's changelog already
# mentions AI literacy. 26.01 promotes it to the frame -- its version
# history entry reads simply "Rewrite," where every prior entry is an
# incremental tweak.
# Publisher is the Institute, at azk12.AI. Not the Arizona K12 Center,
# which is azk12.ORG and a different organization.

---

date: 2026-04-13
display: April 13, 2026
where: Federal
headline: Education Department adds an AI priority for grant competitions
detail: A supplemental priority published in April and effective May 13, 2026 lists professional development for educators on AI among the things a project may do. The Department may use it in any discretionary competition, or use only some of its parts, so it shapes which applications score well in the competitions that adopt it. It is not itself a source of money.
source: the Federal Register
url: https://www.govinfo.gov/content/pkg/FR-2026-04-13/pdf/2026-07087.pdf
guide: paying-for-ai-with-federal-funds
guide-label: paying for AI work with federal funds
# CORRECTED 2026-09-18: the row was dated May 13, which is the
# EFFECTIVE date. Published April 13, 2026 (91 FR 18774). The row now
# sorts by publication and names both.
# Also softened: the notice says the priority "may be used" across
# discretionary programs and that the Secretary may use "one or more
# of the priority's component parts." The AI-PD subpart is not
# guaranteed to appear in any given competition, so "shapes which
# applications score well" now carries "in the competitions that
# adopt it."
# Educator PD appears three times: (a)(v), (a)(vi), (a)(xi).
# Docket ED-2025-OS-0118.

---

date: 2026-05-12
display: May 12, 2026
where: Oklahoma
headline: Oklahoma requires district AI policies before the 2027-28 year
detail: Every district board must adopt a policy covering six things: responsible staff, permitted and prohibited instructional uses, data protection and minimization, transparency to students and families, a review cycle, and compliance with the state's guardrails, which bar AI as the primary basis for grading, discipline, placement or promotion. Separately and already in force, districts must disclose every AI tool to parents each year and honor an opt-out with no academic penalty. The state education department's July 2026 guidance for schools, version 3.0, folds the act in and includes a district policy and compliance checklist.
source: the Oklahoma Legislature
url: https://www.oklegislature.gov/cf_pdf/2025-26%20ENR/SB/SB1734%20ENR.PDF
guide: what-an-ai-policy-should-include
guide-label: what a policy should include
# CORRECTED 2026-09-18. The first version listed FOUR of the six
# required elements, dropping (4) transparency to students and
# families and (6) compliance with subsection E and state guidance --
# the catch-all that pulls in the whole guardrail regime. A district
# building a policy from that list would have been non-compliant.
# Element 3 is "data protection AND DATA MINIMIZATION"; minimization
# is a distinct duty.
# Added subsections F and G, which are in force NOW and are the part
# a parent will call about: annual written disclosure naming every AI
# tool, its vendor, data collected and purpose, plus an at-any-time
# written opt-out with no academic penalty.
# REMOVED the charter sentence. "Does not mention charter schools
# either way" was literally true -- zero occurrences of "charter" --
# but misleading: 70 O.S. 3-136(A)(1) exempts charters from statutes
# outside the Charter Schools Act by default, and SB 1734 sits at
# 11-120, outside it. The default resolves toward EXEMPTION, not
# silence. Too long for the row; it is in the working file.
# Deadline verified: "Prior to the beginning of the 2027-2028 school
# year." The act is otherwise effective 1 Jul 2026 with an emergency
# clause.
# ADDED 2026-09-29: OSDE "Guidance and Considerations for Using
# Artificial Intelligence in Oklahoma K-12 Schools, Version 3.0, July
# 2026, Incorporating Oklahoma 70 O.S. 11-120." PDF opened and text
# extracted; Part I section 2 is "District Policy & Compliance
# Checklist." URL: oklahoma.gov/content/dam/ok/en/osde/
# ai-and-digital-learning/Guidance%20for%20Using%20AI%20in%20Oklahoma
# %20Schools%20v.3.pdf. Not linked from the row; one link per row.

---

date: 2026-03-18
display: March 18, 2026
where: Utah
headline: Utah requires a classroom technology policy with an AI component
detail: HB 273 gives the state board until December 1, 2026 to post a model policy and every district and charter until July 1, 2027 to adopt it or a conforming version. The bill is mostly about screen time and devices, and the policy districts adopt must contain an AI use component rather than being an AI policy as such.
source: the Utah Legislature
url: https://le.utah.gov/~2026/bills/static/HB0273.html
guide: what-an-ai-policy-should-include
guide-label: what a policy should include
# CORRECTED 2026-09-18. The headline said "requires every district and
# charter to adopt an AI policy." Not false, but not what the bill is:
# HB 273 is titled "Classroom Technology Amendments," and most of the
# model policy is grade-band screen-time rules (K-3 gets no take-home
# devices, no 1:1, no homework requiring internet).
# THE DATES ATTACH TO THE RIGHT DUTY: July 1, 2027 is from
# 53G-7-228(3)(e), the balanced-technology-use policy that must
# CONTAIN an AI component. The bill's separate standalone AI provision,
# 53G-7-1402(3)(a), carries NO statutory deadline -- timelines are
# delegated to board rulemaking. Citing the wrong section would attach
# a real date to a duty that has none.
# Charters included: "public school" covers districts, charters and
# the Utah Schools for the Deaf and the Blind.
# Worth knowing: the board may declare the model policy the DEFAULT
# for any LEA that fails to adopt, and digital-literacy and ed-tech
# state funds are tied to certifying adoption.

---

# HELD. Three named districts is not a trend with a denominator.
# NYC, LAUSD and Katy ISD (Texas, 2026-07-20, K-6 barred, grade 7 by
# teacher direction, 8-12 approved tools with permission) are the
# confirmed ones. Name them or find a real count.
stat: TBD
date: 2026-09-02
display: September 2026
where: Districts
headline: Large districts are restricting student AI use
detail: Placeholder.
source: TBD
url:
draft: yes

---

# LIVE 2026-09-29 at Joseph's call (was held as a draft the same
# morning). A motion, not an order. Nothing has been granted and no
# hearing date is in the filing. The PDF was downloaded and read:
# Filing # 257955836, e-filed 09/28/2026, 49 pages with exhibits.
# Hosted by a TV station because myfloridalegal.com blocks automated
# fetches; open the AG release in a browser before swapping the link.
# Update the row when the court rules.
date: 2026-09-28
display: September 28, 2026
where: Florida
headline: Florida's attorney general asks a court to bar ChatGPT for minors
detail: In its June lawsuit against OpenAI, the state moved for a temporary injunction that would, pending trial, stop the company from offering ChatGPT to minors in Florida and from collecting data from children under 13 without notice and verifiable parental consent, among other relief. The motion targets the consumer product, not school-licensed tools, and the court has not ruled.
source: the Florida Attorney General
url: https://cbs12.com/resources/pdf/188afcfe-9850-412c-b100-16574c3ca84b-plaintiffs_motion_for_temporary_injunction.pdf
guide: do-schools-need-an-ai-policy
guide-label: do schools need a policy
# Motion verbatim (Conclusion): "B. Offering ChatGPT to minors in
# Florida; C. Collecting and processing data from minors under the age
# of 13 in Florida ... without first (1) providing written notice ...
# (2) obtaining verifiable parental consent." Reuters 9/28:
# reuters.com/world/florida-asks-court-bar-openai-developing-new-models-
# part-child-harm-lawsuit-2026-09-28/. Suit filed June 1, 2026,
# Highlands County, Case No. 26000295GCAXMX.

---

# ADDED 2026-09-29 (second sweep). Both Google posts opened and quoted.
# Sept 17 post (workspaceupdates.googleblog.com/2026/09/notebooks-in-
# gemini-...): "students of all ages, educators, and professionals can
# access notebooks"; "Admins: Access to Notebooks in Gemini is on by
# default"; "Gradual rollout (up to 15 days for feature visibility)
# started on September 14, 2026."
# Aug 4 post (workspaceupdates.googleblog.com/2026/08/gemini-in-google-
# classroom-is-expanding-to-users-of-all-ages-...): "Starting August 10,
# 2026, Gemini in Classroom will also be made available to K-12 and
# higher education students of all ages"; "Access to the Gemini tab in
# Classroom is On by default for teachers and students of all ages";
# "If Gemini in Classroom is currently turned off for students, access
# will remain off for all students, including students younger than
# 18." Editions: "Education: Fundamentals, Standard, and Plus."
# TRAP: "on by default" only reaches students whose admin already has
# Gemini turned on. A district that turned Gemini off is untouched.
# The row says so. EdWeek (9/1) quotes Common Sense's Robbie Torney
# calling it a rollout that "defaults to adoption rather than
# permission." Not used; the row states the mechanism instead.
date: 2026-09-17
display: September 17, 2026
where: Vendors
headline: Google turns on Gemini notebooks for students of all ages
detail: Notebooks in the Gemini app, which hold up to ten sources and the conversations about them, began reaching students of all ages on September 14, on by default wherever an administrator already has Gemini turned on. It follows the August 10 change that opened the Gemini tab in Google Classroom to students of every age on the same terms. A district that has Gemini switched off for students is unaffected either way, and one that has it on now has both.
source: Google
url: https://workspaceupdates.googleblog.com/2026/09/notebooks-in-gemini-dedicated-workspace-for-focused-organized-work-now-for-schools-and-organizations.html
guide: scaffolding-ai-use-k12
guide-label: scaffolding AI use by grade

---

# HELD 2026-09-29 for Joseph's call. A governor's framework, not a rule
# or a statute. Release opened (governor.maryland.gov, 2026-09-22):
# "Governor Moore today announced a new AI framework outlining his
# administration's core principles." Verbatim school items: "working
# with the Maryland State Department of Education and the legislature
# to require schools to implement protocol for any AI tool a student
# interacts with at school"; "Implement a 'do no harm' policy for AI
# use in schools ... to ensure that any AI tools in classrooms have
# demonstrated outcomes for student learning, are supplementing
# educator instruction, and that families are informed before use";
# MSDE "to issue model K-12 lesson plans."
# SEPARATE, still unresolved: the AI Ready Schools Act (SB 720,
# effective June 1, 2026) gives local boards 120 days from MSDE's
# guidance. MSDE's page shows no publication date; MACo (9/10) says
# "sometime this month"; one county report says Oct 22. No primary
# source for a date. Do not print one.
date: 2026-09-22
display: September 22, 2026
where: Maryland
headline: Maryland's governor proposes a "do no harm" rule for classroom AI
detail: A framework from the governor's office says the administration will work with the state education department and the legislature to require a protocol for any AI tool a student uses at school, to allow classroom AI tools only where they have demonstrated outcomes for learning and families are told before use, and to issue model K-12 lesson plans on AI. It is a statement of intent. Nothing in it binds a district yet, and the state's separate deadline for local AI policies under this year's AI Ready Schools Act is running now.
source: the Office of the Governor of Maryland
url: https://governor.maryland.gov/news/press-releases/governor-moore-outlines-ai-framework-protect-marylanders
guide: ai-policies-vs-guidelines
guide-label: policies versus guidelines
draft: yes

# SEEN 2026-09-29 (second sweep), NOT ROWED:
#   Pennsylvania HB 2788, introduced 9/24: permissive staff AI training,
#     unfunded unless appropriated. A bill introduction.
#   Quaker Valley SD (PA) adopted a generative-AI policy 9/22, 8-0.
#     ~1,900 students. Local.
#   Atlanta Public Schools reviewed a draft student AI policy 9/16;
#     decision expected in November. Recheck then.
#   Learning Commons (CZI-backed) open AI-in-education platform, 9/22.
#     Vendor infrastructure.
#   Microsoft 9/16 blog restating the 9/9 standard; Copilot Chat
#     default-off for K-12 students.
#   Springfield, MA (Kiley Prep) Alpha-School-model pilot: start
#     reported for late September, no confirmation it began.
