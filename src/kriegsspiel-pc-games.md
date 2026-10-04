title: The Prussian Kriegsspiel never ported cleanly — which PC games come closest
date: 2026-10-04
tldr: The 1824 Kriegsspiel rests on five pillars: a human umpire, orders that take time, double-blind fog of war, simultaneous movement, and a training purpose with no win condition. PC wargames each cover one or two; none covers all. Command Ops 2, Combat Mission's WeGo and the radio games come closest.

## The yardstick the 1824 apparatus sets

"The player must be given no greater certainty than that which exists in reality."

The claim that PC games never captured the Prussian Kriegsspiel is nearly right, in a specific way: no single one has. To judge the field fairly, use the yardstick of the apparatus itself. In 1824 Georg Heinrich Rudolf Johann von Reisswitz published in Berlin the *Anleitung zur Darstellung militairischer Manöver mit dem Apparat des Kriegs-Spieles* — instructions for representing military manoeuvres with the Kriegsspiel apparatus — and as the English précis puts it, "winning and losing in the sense of a game is not the object". The design has five distinct pillars (Wargame Library, "Kriegsspiel"; the 1824 original on archive.org):

1. **An umpire.** One person alone sees the whole board, adjudicates movement and combat, and delivers what each side may know. "All orders, reports, and communications pass through the umpire, who must determine the time required for their delivery." The game is for instruction, not for a win.
2. **Orders, not manipulation.** Players write orders; couriers carry them; delivery consumes real time and can fail. Nobody picks up a piece.
3. **Double-blind fog of war.** "Each party is informed only of that which it could know under the assumed conditions", and "those movements which are not visible remain concealed". The original is played on three identical maps, one per side plus the umpire's.
4. **Simultaneous movement.** Both sides move together in fixed, real-time increments — two minutes in the original — before combat is resolved.
5. **Friction as curriculum.** Reports arrive late and wrong; orders are misread; that is the point. The International Kriegsspiel Society (IKS) states the pedagogical core as "command and control in combat situations, the friction of orders, command confusion and delays, and the assessment of tactical situations based on incomplete data" (IKS FAQ). 

Everything below is judged against those five pillars. The good news for an enthusiast: the five divide almost perfectly into the families of "command" PC games, and the games below each implement one or two of them well. The bad news: nothing implements more than three, and the missing pillar — a human umpire — is the one that makes a Kriegsspiel a Kriegsspiel.

## Pillar two, implemented: orders that take time

**Command Ops 2** (Panther Games; on Steam since March 2015) is the cleanest version of the command pillar at operational scale. Its own feature list leads with "orders delay", "macro management" and "no hexes, no turns, no micromanagement, no click fests". You plan at corps, division or brigade level, hand the plan down the chain, and subordinate commanders and the enemy AI execute; you never drag a battalion through a hex. The flaw for a Kriegsspiel player is map honesty: inside your own lines you see your order of battle on the one shared board, which is more and cleaner information than any 1824 staff would have had. It is the strongest "write the orders, then wait" title on the list, but it is not double-blind.

**General Staff: Black Powder** (Riverview; still listed as "coming soon" on Steam in October 2026) is the most literal homage in the field. The store text is explicit: "orders are given by courier"; the fog of war is selectable as total, partial or none and is computed from 3D line of sight and visibility conditions; the game ships with four black-powder battles (Antietam, Quatre Bras, Ligny, Manassas) and supports PBEM and local multiplayer. Its artificial intelligence, MATE, began as a DARPA research programme (grant W911NF-11-200024) that demonstrated the software analysing a real tactical situation and proposing an envelopment course of action within seconds. The courier pillar and the fog pillar are genuine; the simultaneity pillar is not — PBEM is one-sided sequential, so both sides cannot move at once, and there is no umpire's third map.

**King's Orders** (AFTERLIFE / Games Operators, 2024) is the odd one on the list, and in its favour. It is a medieval kingdom sim played by correspondence: "send orders by letters to your generals", and "it takes time for your runner to deliver the message and the route is full of dangers"; deliberately there is no battle preview — "your understanding of events is solely derived from received reports". That is precisely the command-and-report loop of pillars two and three, bought at the cost of pillar four: battles are settled off-screen and the map is barely tactical. For the enthusiast who values the *structure* of the Kriegsspiel over its era, it is more faithful than most Napoleonic titles.

**HistWar: Napoleon and HistWar: Les Grognards** (the French studio whose Grognards line descends from the 2001 Matrix-published LGAA) are sold as "tactical wargame[s] designed to provide the most accurate simulation of battles from the Napoleonic era", played "as Commander-in-Chief", drawing "inspiration from Jomini and Clausewitz". You command through a staff map while subordinates execute; the IKS-aligned community keeps a dedicated HistWar section beside its Scourge of War one. In practice you can reach down and micromanage past the command model, which the original apparatus would punish; treat it as a richer, more forgiving cousin.

**Decisive Campaigns: Barbarossa** (VR Designs, 2015) is the operational extreme: "within a command hierarchy" you task theatre commanders and armies, who "may refuse". That is honest command-by-delegation, but at 30 km hexes and four-day turns the two-minute rhythm of the umpire's tick has gone. It belongs in the command family, no further.

## Pillars four and three: the umpire's tick, then fog as the interface

The original apparatus resolves both sides simultaneously in short, true time. The natural computer form of that is "WeGo": write all orders blind, both sides move together, then receive the report. The natural computer form of pillar three is worse than that — the enemy should only ever exist as someone's testimony.

**Combat Mission** (Battlefront, now sold under Matrix; *Red Thunder* and the other titles on Steam) advertises a "[u]nique hybrid system for RealTime and WeGo (turn based) play" at "battalion and below scale". WeGo is the closest thing to the umpire's tick in any commercial game: you issue every order before resolution, both sides move at once, and the replay plays the role of the umpire's report. PBEM (and PBEM+) carries the correspondence workflow into email. The gaps are the familiar ones: the map is shared, and at battalion-and-below you order squads and single tanks, where order delay is a cosmetic option rather than a throttle.

**Graviteam Tactics** (*Operation Star*, 2012, and successors) is the Eastern-Front counterpart, platoon to battalion, whose selling point is that "every soldier has several basic parameters, such as experience level, fatigue, and morale, which affect their behaviour and effectiveness", while scenario AI "chooses the best strategy based on behaviour rather than a script". You give plans; the men decide; the shared-board caveat applies as elsewhere.

**Flashpoint Campaigns: Red Storm** (On Target Simulations / Matrix, 2013) is the one game that models the *time-and-information* pillar directly. Its mechanics: an "asynchronous turn structure that models the OODA loop"; "variable length turns based on current Command, Control and Communication state (C3)" — lose your C3 and your own orders take longer and arrive later; and an active fog of war in which units can "report back incorrect or incomplete intel". That is pillar five — delayed, degraded, unreliable reports — as a mechanic rather than a garnish. The same caveat applies: one shared board, and you hand-order every battalion.

**Radio Commander** (Critical Forge / Klabater, 2019; the GOG "Complete Edition") compresses pillar three into the interface itself: "situation reports are received exclusively through dramatic radio transmissions", the "only operational interface is a strategic map" on which you keep tokens and notes, and you decide on testimony alone. There is no battlefield to watch, which is precisely the point.

**Radio General** (Foolish Mortals Games / Michael Long, 2020) does the same at the microphone: "a real-time strategy game where you can't see your units" and the reports you receive are "incomplete (and often confused)", taken from a command tent. The fog here is structural, not decorative. Both radio games buy pillar three by spending the tactical depth a real map game would use; they are two versions of the same coin.

## The black-powder game the community actually adopted

**Scourge of War** (Norb Software; the Remastered edition on Steam since September 2024) is real-time and turn-free — "a type of wargame that we call real time command simulation". In multiplayer, messages ride couriers that "can be delayed, killed or captured". This is the same vocabulary as Reisswitz's umpire; the Kriegsspiel community's own 2011 review of the original was headed "Finally a kriegsspiel on the PC?" and praised exactly this: "the game handles all the umpiring requirements for a typical von Reisswitz kriegsspiel: unpredictable scenario, movement, contact reports, combat, message transmission". The IKS-linked forum still maintains a dedicated Scourge of War section, and its Store page quotes that review. It presents the fog as lived experience — a saddle camera, sound of distant cannon — rather than as an umpire's map. Its cost: pillar four is gone (real time, no simultaneous tick) and pillar one was never there (no human umpire).

## What a PC game still cannot give you

Steel the premise, and it mostly survives. None of these is a Kriegsspiel, and the reasons are structural, not implementation flaws:

- **No human umpire.** A computer can adjudicate, but it cannot judge or run the debrief, and its situational evaluation is an algorithm, not a skill.
- **No third map.** Every title above is played from one shared board. Double-blind is approximated — by spotting and "when last seen" reporting in Flashpoint, by prose in the radio games, by nothing in others — but WeGo replays and PBEM exchanges reveal, in the end, everything a side could not have known.
- **No "not a game" ethos.** They are balanced, winnable, save-scummable products. The 1824 apparatus was deliberately unfair, asymmetrical and educational.
- **Direct control leaks back.** In every title here except King's Orders you can reach down and drag units; friction is a setting, not a requirement.

For completeness, what is not even close: Total War, Ultimate General, Close Combat and Steel Division command on the spot, and the classic hex-grimoire titles — The Operational Art of War IV and the Panzer Campaigns family — push shadowless counters around a shared board with no interposed command layer at all. They inherit the map, not the mechanism. **Grand Tactician: The Civil War** sits between: a grand campaign with historical command structures and orders of battle that drops into direct control when armies meet.

## The real thing is also on PC — it just is not a product

The most useful answer for an enthusiast is to stop approximating. The International Kriegsspiel Society "play[s] digitally via the internet": a human umpire, double-blind maps, simultaneous movement, message delay, and a post-game critique, run over Discord with Tabletop Simulator (optional) for the pieces; message-by-post games stretch one turn over days. It is free, open to novices, keeps the rules away from players "so the game cannot be gamed", and its Saturday games run "about four hours, sometimes up to 6 hours" including the debriefing. The 1824 original is freely digitised and the English translation circulates. For a Kriegsspiel enthusiast this satisfies all five pillars at once; nothing on a game store does.

## What to buy, if approximations are what you want

- Orders pillar alone: **Command Ops 2** for a map, **King's Orders** for correspondence.
- Simultaneity pillar alone: a **Combat Mission** title in WeGo.
- Fog-as-testimony pillar alone: **Radio General** or **Radio Commander**.
- Black-powder, multiplayer, community-endorsed: **Scourge of War – Remastered**, plus joining the real thing at the IKS.

On honesty of ranking: I would put the claim that Command Ops 2 together with a Combat Mission WeGo title covers four of the five pillars better than any single title at about eight in ten, and the claim that no commercial title covers more than three of the five at nine in ten. Within the black-powder group the margin between Scourge of War and General Staff: Black Powder is small by design; the former is the better simulator of command, the latter the more literal architect of fog and couriers.

## Sources

**The apparatus (primary and definition)**

- Georg Heinrich Rudolf Johann von Reisswitz, *Anleitung zur Darstellung militairischer Manöver mit dem Apparat des Kriegs-Spieles*, Berlin: G. Reimer, 1824 (German original). [Original](https://archive.org/details/reisswitz-1824)
- The Wargame Library, "Kriegsspiel" (librarian's summary; English quotations from the 1824 manual, including "The player must be given no greater certainty…", "Winning and losing in the sense of a game is not the object", and the two-minute/three-map exposition). [Original](https://www.wargamelibrary.com/kriegsspiel)
- International Kriegsspiel Society, "What is Kriegsspiel?". [Original](https://kriegsspiel.org/what-is-kriegsspiel/) · [Archived](https://web.archive.org/web/20261004032514/https://kriegsspiel.org/what-is-kriegsspiel/)
- International Kriegsspiel Society, FAQ ("What is Kriegsspiel?", "Is it just another tactical game?", "What do I need to play?" — double-blind, message and order delay, Discord/Tabletop Simulator, session lengths). [Original](https://kriegsspiel.org/faq/) · [Archived](https://web.archive.org/web/20260711205627/https://kriegsspiel.org/faq/)
- International Kriegsspiel Society, Resources (online play; Tabletop Simulator modules). [Original](https://kriegsspiel.org/resources/) · [Archived](https://web.archive.org/web/20260826040724/https://kriegsspiel.org/resources/)

**Community review**

- "Finally a kriegsspiel on the PC? Gettysburg: Scourge of War review", Kriegsspiel News Forum, 6 September 2011 (couriers that can be delayed/killed/captured; "handles all the umpiring requirements for a typical von Reisswitz kriegsspiel"). [Original](https://kriegsspiel.forumotion.net/t197-finally-a-kriegsspiel-on-the-pc-gettysburg-scourge-of-war-review) · [Archived](https://web.archive.org/web/20260730224645/https://kriegsspiel.forumotion.net/t197-finally-a-kriegsspiel-on-the-pc-gettysburg-scourge-of-war-review)

**Games (all descriptions quoted from the linked store or developer pages)**

- Scourge of War – Remastered, Norb Software (Steam page; quotes the 2011 forum review). [Original](https://store.steampowered.com/app/2205330/Scourge_Of_War__Remastered/) · [Archived](https://web.archive.org/web/20260730224632/https://store.steampowered.com/app/2205330/Scourge_Of_War__Remastered/)
- King's Orders, AFTERLIFE / Games Operators (Steam page; "lack of battle preview", "runner… the route is full of dangers", reports only). [Original](https://store.steampowered.com/app/1369690/Kings_Orders/) · [Archived](https://web.archive.org/web/20260929002724/https://store.steampowered.com/app/1369690/Kings_Orders/)
- General Staff: Black Powder, Riverview (Steam page; courier orders, total/partial/no fog of war via 3D line of sight, MATE AI, PBEM; still "coming soon" as of October 2026). [Original](https://store.steampowered.com/app/1128490/General_Staff_Black_Powder/) · [Archived](https://web.archive.org/web/20260905043933/https://store.steampowered.com/app/1128490/General_Staff_Black_Powder/)
- Riverview Artificial Intelligence, research page on MATE (DARPA grant W911NF-11-200024; COA in under ten seconds). [Original](https://www.riverviewai.com/) · [Archived](https://web.archive.org/web/20260626022139/https://www.riverviewai.com/)
- Command Ops 2 Core Game, Panther Games (Steam page; "orders delay", "macro management", "no hexes, no turns, no micromanagement"). [Original](https://store.steampowered.com/app/521800/Command_Ops_2_Core_Game/) · [Archived](https://web.archive.org/web/20260416023649/https://store.steampowered.com/app/521800/Command_Ops_2_Core_Game/)
- Flashpoint Campaigns: Red Storm Player's Edition, On Target Simulations / Matrix Games (Steam page; OODA asynchronous turns, C3-dependent turn length, active FOW with incorrect/incomplete intel). [Original](https://store.steampowered.com/app/330720/Flashpoint_Campaigns_Red_Storm_Players_Edition/) · [Archived](https://web.archive.org/web/20260625102358/https://store.steampowered.com/app/330720/Flashpoint_Campaigns_Red_Storm_Players_Edition/)
- Combat Mission Red Thunder, Battlefront / Slitherine-Matrix (Steam page; RealTime and WeGo, battalion-and-below, PBEM). [Original](https://store.steampowered.com/app/2418000/Combat_Mission_Red_Thunder/) · [Archived](https://web.archive.org/web/20260819064505/https://store.steampowered.com/app/2418000/Combat_Mission_Red_Thunder/)
- Graviteam Tactics: Operation Star, Graviteam (Steam page; soldier experience/fatigue/morale, behavioural AI). [Original](https://store.steampowered.com/app/275290/Graviteam_Tactics_Operation_Star/) · [Archived](https://web.archive.org/web/20260329211005/https://store.steampowered.com/app/275290/Graviteam_Tactics_Operation_Star/)
- Radio General, Foolish Mortals Games / Michael Long (Steam page; "you can't see your units", confused reports). [Original](https://store.steampowered.com/app/1011610/Radio_General/) · [Archived](https://web.archive.org/web/20261002054913/https://store.steampowered.com/app/1011610/Radio_General/)
- Radio Commander: Vietnam '64, Critical Forge / Klabater (Steam page; situation reports only via radio, strategic-map interface). [Original](https://store.steampowered.com/app/871530/Radio_Commander_Vietnam_64/) · [Archived](https://web.archive.org/web/20260916175332/https://store.steampowered.com/app/871530/Radio_Commander_Vietnam_64/)
- Radio Commander: Complete Edition, GOG. [Original](https://www.gog.com/en/game/radio_commander_complete_edition) · [Archived](https://web.archive.org/web/20260906081711/https://www.gog.com/en/game/radio_commander_complete_edition)
- HistWar: Napoleon, HistWar (histwar.com; "as Commander-in-Chief", "inspiration from Jomini and Clausewitz"). [Original](https://www.histwar.com/en/collections/histwar-napoleon) · [Archived](https://web.archive.org/web/20251006064033/https://www.histwar.com/en/collections/histwar-napoleon)
- HistWar: Les Grognards, HistWar (histwar.com; lineage from LGAA, 2001; the IKS forum's dedicated section). [Original](https://www.histwar.com/en/collections/histwar-les-grognards) · [Archived](https://web.archive.org/web/20250908001529/https://www.histwar.com/en/collections/histwar-les-grognards)
- Decisive Campaigns: Barbarossa, VR Designs / Wastelands Interactive (Steam page; command hierarchy, theatre commanders who "may refuse", 30 km hexes, four-day turns). [Original](https://store.steampowered.com/app/454530/Decisive_Campaigns_Barbarossa/) · [Archived](https://web.archive.org/web/20260827072207/https://store.steampowered.com/app/454530/Decisive_Campaigns_Barbarossa/)
- The Operational Art of War IV, Matrix Games (Steam page; the hex-counter tradition, direct control). [Original](https://store.steampowered.com/app/792660/The_Operational_Art_of_War_IV/) · [Archived](https://web.archive.org/web/20260913081437/https://store.steampowered.com/app/792660/The_Operational_Art_of_War_IV/)
- Grand Tactician: The Civil War, Grand Tactician Entertainment (Steam page; grand campaign with historical command structures and OOBs, tactical battles). [Original](https://store.steampowered.com/app/654890/Grand_Tactician_The_Civil_War_1861_1865/) · [Archived](https://web.archive.org/web/20261004151907/https://store.steampowered.com/app/654890/Grand_Tactician_The_Civil_War_1861_1865/)
