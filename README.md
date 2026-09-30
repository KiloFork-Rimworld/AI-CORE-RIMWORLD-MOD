# AI Enhanced Gameplay Mod for RimWorld

A work-in-progress RimWorld mod (repo description: "My First Rimworld Mod") by Kilo.Musician. The idea is to make colonists feel more alive: they would form memories, show richer emotions, hold conversations, react to smarter health handling, and talk to the player through an "AI God Core" device. It is aimed at RimWorld players and modders who like the concept or want to pick up an unfinished project. It is not playable yet.

## Status

Early prototype. Read this before expecting anything to work.

- `main` has no C# source and no compiled mod. The two files in `Assemblies/` (`AIEnhancements.dll`, `ModAssembly.dll`) are identical tiny text files (a few `using` lines and a Python import snippet), not .NET assemblies.
- An earlier state of the repo, commit `538415d` (2024-05-08), held 107 `.cs` files, mostly under `Source/AITemple/`. Commit `4fcaf70` (2026-08-16) removed them. It has not been checked whether they compile. Browse them with `git checkout 538415d`.
- `About/about.xml` is not well-formed XML: `<ModMetaData>` closes after `<author>`, leaving the link, description and version elements outside it. It also has no `packageId`.
- Several XML defs are broken or point at classes that do not exist (details below). Whether RimWorld loads any of them has not been tested.

## Supported RimWorld versions

From `About/about.xml`: `targetVersion` 1.0, `supportedVersions` 1.2 and 1.3. None of these was tested.

## Install

Not verified. The repo has no releases or tags and no install instructions. The folders (`About/`, `Defs/`, `Assemblies/`, `Languages/`) follow the usual RimWorld mod shape, so the normal route of placing a mod folder in the game's `Mods` directory should apply, but this repo has not been loaded into the game. With the status above, there is no working feature to switch on anyway.

## What it adds

Defined in XML today (in `Def/`; the same files are also copied into `Defs/ResearchProjectDefs/`):

- **AI-enhanced super computer** (`AIEnhancedSuperComputer`): an item, market value 2500, mass 10, `HighTech` trade tag. The description says it boosts research, but the def sets no such stat.
- **AI-enhanced serum** (`AIEnhancedSerum`): a drug with addictiveness 0.03. Its use effect is `CompUseEffect_ActivateAI`, a class that is not in the repo.
- **AI-boosted cognition** (`AIBoostedCognition`): a health condition (hediff) giving +0.20 Consciousness.
- **`UseAIComputer` job**: its `driverClass` is the placeholder `Path.To.Namespace.JobDriver_UseComputer`.
- **Two research projects** in `Defs/ResearchProjectDefs/NewResearch1.xml`: AI Integration Basics (cost 700, Industrial, needs `MicroelectronicsBasics`) and Advanced AI Systems (cost 1400, Spacer, needs AI Integration Basics). That file does not parse as XML (a comment sits before the XML declaration).

Planned only (described in the `About` text, no code in the repo): colonist memories and emotions, conversations between colonists, procedural events, adaptive quests, colonists building rooms in player-defined zones, the "AI God Core" device, learning NPCs, performance and debugging tools. Treat these as design intent.

`Languages/English/` files (`Keyed/AI.xml`, `Keyed/Main.xml`, `Strings/Tips.xml`) are empty.

## Build from source

`ModProject.csproj` is an SDK-style class library targeting `netstandard2.0`.

- It references `UnityEngine`, `UnityEngine.CoreModule`, `Assembly-CSharp` and `RimWorld` through hard-coded `HintPath`s into a default Windows Steam install of RimWorld (`RimWorldWin64_Data/Managed`). Adjust those paths for your machine.
- NuGet packages: HarmonyX 2.12.0, Microsoft.CSharp 4.7.0, Microsoft.ML 1.5.5, Newtonsoft.Json 13.0.1, NLog 5.3.2, Serilog 2.10.0, System.Collections.Immutable 5.0.0, System.ValueTuple 4.5.0.
- The usual command for this project type is `dotnet build ModProject.csproj`. It was not run for this README, and with no `.cs` files on `main` there is nothing meaningful to compile.
- `Visual Studio/ModProject.sln` is an empty file. The "Build Mod" task in `Configs/settings.json` points at `Source/Project.csproj`, which does not exist. There are no tests on `main`.

## Repo layout

- `About/about.xml`: mod metadata (see Status).
- `Assemblies/`: the two placeholder "DLL" text files.
- `Def/`: four defs (item, drug, hediff, job). RimWorld mods conventionally use `Defs/`, so this singular folder may not be read.
- `Defs/ResearchProjectDefs/`: copies of the `Def/` files, `NewResearch1.xml`, three empty files (`AI.xml`, `Main.xml`, `Tips.xml`), and stray copies of `about.xml`, `Config.xml` and `AICompanionCore.xml`.
- `Languages/English/`: empty translation files.
- `AICompanionCore.xml` (root): a component manifest that lists source paths such as `Source/AI/Core/AICore.cs`, which are not in the current tree. It names Harmony 2.0.4 and HugsLib 7.2.1 as dependencies.
- `Config.xml` (root): a generic placeholder application config ("Example Company", sample paths), unrelated to RimWorld.
- `Configs/`, `.vscode/`, `Scripts/`, `cspell.json`, `OldestHouse.code-workspace`: editor and NuGet configuration.
- `DevelopmentTools/`: `NLog.config`, two dependency-analysis outputs that contain only `[]`, and `output_file`, a plain file listing.
- `Logs/`: two empty log files.
- `obj/`, `Visual Studio/obj/`: committed NuGet and build intermediates.
- `vault/README.md`: notes about the GitHub organization that hosts this repo; not part of the mod.

## Credits and license

- Author, per `About/about.xml`: Kilo.Musician. The link in that file is `http://github.com/KiloMusician/AIEnhancedGameplayMod`, a different repository name from this one.
- Dependencies: `AICompanionCore.xml` lists Harmony 2.0.4 and HugsLib 7.2.1; `ModProject.csproj` references HarmonyX 2.12.0 and not HugsLib; `About/about.xml` declares none. Which is intended is not settled in the repo.
- Licensed under MIT, see `LICENSE`.
