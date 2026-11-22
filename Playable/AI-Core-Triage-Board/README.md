# AI Core: Colony Triage Board

[Msg⛛{RIMWORLD-CARE-OBSERVER-CSHARP-20261121}]

This is a **separately installable** RimWorld 1.6 mod candidate from the old AI Enhanced Gameplay initiative. The main legacy repository root has broken Def XML and fake DLLs. Never point RimWorld's mod manager at the repository root.

The new C# code is actual game-facing implementation, not a design-only declaration. The board opens through a bottom main-button tab, reads the actual live current-map player colonists and shows their health, bleed rate and downed state ordered by a deterministic urgency score. Unlike the unfinished historical AI God Core plan, this does not pretend to control AI models or autonomously treat colonists.

## Install after exact-version compile

The mod folder is Playable/AI-Core-Triage-Board. The native DLL is **NOT** in Git. Build it using the provided project and .NET SDK:

    dotnet build Playable/AI-Core-Triage-Board/Source/TriageBoard/TriageBoard.csproj -c Release

The compiled assembly is written to Playable/AI-Core-Triage-Board/1.6/Assemblies/KiloAI.ColonyTriage.dll. It uses the existing colony standard: Krafs.Rimworld.Ref 1.6.4633 plus net472 reference assemblies. No RimWorld copyrighted game DLLs are checked in or needed during the hosted source build.

Place only the resulting Playable/AI-Core-Triage-Board folder inside the game's Mods directory; keep the Source and Tests directories outside the installed game if packaging manually. In RimWorld **1.6**, enable AI Core: Colony Triage Board in a disposable mod profile and restart. Select a map, then open the "colony triage" bottom main button. You should see a read-only ranking of your living spawned colonists.

There is no Harmony patch, load-order override, automatic medical decision, job allocation, map edit, provider integration, save schema, data collection, or model API call. Changing actual treatment remains a deliberate vanilla RimWorld action.

## Verify actual code, not just XML

From the repository root, without the game installed:

    dotnet run -c Release --project Playable/AI-Core-Triage-Board/Tests/TriageRules.Smoke/TriageRules.Smoke.csproj
    dotnet build -c Release Playable/AI-Core-Triage-Board/Source/TriageBoard/TriageBoard.csproj

The first is a pure C# source-executed regression with 18 assertions: actual urgency, very low HP, critical bleeding, downed pawns, corrupt/nonfinite float input, deterministic scoring and displayed percent/bleed. The second must compile the **actual MainTabWindow implementation against RimWorld reference assemblies**, not a mocked game API. The GitHub Actions workflow also packages the built real DLL alongside About/Defs, and verifies its real PE header.

A green build proves type/API compatibility with the **Krafs 1.6.4633 reference snapshot** only, not installed game branch, loader/class registration, UI behavior or save stability. The player's RimWorld version 1.6 may have later updates; execute a disposable in-game witness before accepting the mod.

### Actual game acceptance gates

1. RimWorld 1.6 Core + this mod only on a throwaway profile. Preserve Version.txt, Player.log and a source-stamped test log. Do not touch the user's only existing save.
2. Prove package ID and tab window class register with no red XML/assembly errors.
3. Start a three-pawn colony, wound one, make one downed or bleeding, and show priority reordering in the live window.
4. Verify the board doesn't create a job, change doctors, modify medical care defaults, change a hediff, or alter time progression.
5. Switch maps and reload the test save. Make sure the tab shows the correct map and never preserves another map's patient list.
6. Test with the existing Field Triage recipe mod enabled, then typical RimWorld 1.6 colony mod stack. Only after these: independent review and possible main integration.

The previous separate XML-only field-triage mod in PR #5 is optional, and this board can be compiled/tested without that PR. This new tab is a small real engineering step toward useful colonist care, not general artificial intelligence.
