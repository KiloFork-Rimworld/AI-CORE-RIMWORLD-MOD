# AI Core: Field Triage | first executable RimWorld mod slice

[Msg⛛{RIMWORLD-FIRST-PLAYABLE-20261121}]
Status: **XML-only RimWorld 1.6 mod candidate, offline static tests available, in-game play UNVERIFIED.**

This is a contained mechanical slice of the repository's larger, unfinished AI Enhanced Gameplay vision. It does not claim that AI colonist cognition, autonomous NPCs, health AI, or legacy C# code is functioning.

## What it changes

Two genuine RecipeDef bills using only vanilla items/workbenches, plus one ResearchProjectDef.

| Bill | Bench | Spend | Receive | Work | Skill / gate |
|---|---|---|---|---|---|
| Prepare emergency field dressings | Crafting spot or drug lab | 16 Cloth + 1 herbal medicine | 2 herbal medicine | 850 ticks | Crafting 3 |
| Prepare bulk field dressings | Drug lab | 40 Cloth + 3 herbal medicine | 6 herbal medicine | 1,850 ticks | Crafting 6; research field triage protocols |

Bulk research costs 350 and follows vanilla Microelectronics Basics. Both products use MedicineHerbal, so no unknown item type, texture, or new health condition is introduced into a player save. Every extra medicine requires real consumed materials, pawn labor, and sometimes research. Output is the vanilla herbal medicine item, not a new bandage with custom health effects.

## Install candidate on RimWorld 1.6

Do **not** install this repository root. Its old About/about.xml, Defs, and Assemblies contain invalid or placeholder content. They are not part of this isolated playable candidate.

Copy ONLY:

    Playable/AI-Core-Field-Triage/

to the game's Mods directory, yielding:

    RimWorld/Mods/AI-Core-Field-Triage/About/About.xml
    RimWorld/Mods/AI-Core-Field-Triage/Defs/RecipeDefs/FieldDressings.xml
    RimWorld/Mods/AI-Core-Field-Triage/Defs/ResearchProjectDefs/FieldTriage.xml

Enable AI Core: Field Triage in the RimWorld mod manager and restart. Use a **disposable colony/save** for verification. This PR has no installer or ModsConfig updater.

Ludeon's October 2026 announcement described 1.6 as the Steam main branch and 1.7/Waylith as unstable. Only 1.6 is advertised. 1.7, any other version, DLC and modpack compatibility are not claimed.

## Verify source with Python 3.11+

From this repository root:

    python tools/verify_first_slice.py
    python -m unittest discover -s tests -p test_first_playable_mod.py -v

These tests verify structural XML, the candidate vanilla Def references, exact cost/recipe/research gates, no symlinks or legacy fake DLLs, and an unmodified recipe economy. They do not load RimWorld or prove native Def class compatibility.

Create a deterministic installation ZIP in an explicit nonexisting output path:

    python tools/verify_first_slice.py --out /tmp/AI-Core-Field-Triage.zip

The ZIP contains precisely the standalone AI-Core-Field-Triage/About and Defs. Existing output files are refused, not overwritten, and two builds from the same source have matching SHA256.

## Required actual in-game witness

1. Start RimWorld 1.6 with Core and this mod only in a disposable profile/save. Record Version.txt and the resulting Player.log.
2. Confirm no red XML loader errors and the three KiloAI prefixed Defs appear.
3. Place a crafting spot. Give a Crafting-3 pawn 16 cloth and 1 herbal medicine. Create an emergency dressing bill; observe exact input consumption, nonzero pawn work and 2 medicine output.
4. Inspect a drug lab. Verify bulk dressings require field triage protocols after Microelectronics Basics. After research, provide a Crafting-6 pawn 40 cloth and 3 medicine. Confirm a real bill produces 6 medicine, with no free loop.
5. Save/reload and verify resource counts, existing bill and research state survive without errors.
6. Measure balance and compatibility with the colony modpack separately, then request independent review. Do not assert compatibility with unstable 1.7.

## What comes next

The original project plans adaptive colonist agency, AI dialogue, advanced care and richer colony stories. The field-dressing bills give future triage logic a real resource tradeoff to plan around but are **not themselves intelligent or model-powered**. Once native game load is proven, use the existing RimForge doctor and Def index in GSV dev, plus RimWorld reference assemblies, for a bounded C# medical-priority assistant.

The original legacy root files remain intentionally quarantined, unmodified and documented for recovery. No external model service, network requests, game save writes, installed Steam mods or auto-updater is included in this change.
