using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace KiloAI.ColonyTriage
{
    /// <summary>
    /// Read-only human-facing triage board. Observes only currently spawned,
    /// living player colonists on the active map. Does not persist, patch,
    /// issue jobs, alter health, treat injuries, or contact external AI.
    /// </summary>
    public sealed class MainTabWindow_ColonyTriage : MainTabWindow
    {
        private Vector2 scrollPosition;

        public override Vector2 RequestedTabSize => new Vector2(920f, 620f);

        private sealed class PatientRow
        {
            public string Label = "";
            public string Priority = "";
            public string Health = "";
            public string Bleed = "";
            public bool Downed;
            public int Score;
        }

        private static List<PatientRow> Snapshot()
        {
            var result = new List<PatientRow>();
            Map map = Find.CurrentMap;
            if (map == null || map.mapPawns == null)
                return result;

            foreach (Pawn pawn in map.mapPawns.FreeColonistsSpawned)
            {
                if (pawn == null || pawn.Dead || pawn.health == null ||
                    pawn.health.summaryHealth == null || pawn.health.hediffSet == null)
                    continue;

                float health = pawn.health.summaryHealth.SummaryHealthPercent;
                float bleeding = pawn.health.hediffSet.BleedRateTotal;
                bool downed = pawn.Downed;
                result.Add(new PatientRow
                {
                    Label = pawn.LabelShortCap,
                    Priority = TriageRules.Priority(health, bleeding, downed),
                    Health = TriageRules.HealthText(health),
                    Bleed = TriageRules.BleedText(bleeding),
                    Downed = downed,
                    Score = TriageRules.PriorityScore(health, bleeding, downed)
                });
            }

            // Most important health concerns first, with stable label order
            // for ties. No mutation of live pawn list or of any game setting.
            result.Sort((a, b) =>
            {
                int scoreOrder = b.Score.CompareTo(a.Score);
                return scoreOrder != 0
                    ? scoreOrder
                    : string.Compare(a.Label, b.Label, StringComparison.Ordinal);
            });
            return result;
        }

        public override void DoWindowContents(Rect inRect)
        {
            Widgets.Label(new Rect(0f, 0f, inRect.width, 30f),
                "AI CORE  /  COLONY TRIAGE   •   CURRENT MAP ONLY");
            Widgets.Label(new Rect(0f, 35f, inRect.width, 54f),
                "This is a read-only priority overview, not a diagnosis or doctor assignment. " +
                "Review and issue medical orders through RimWorld's ordinary Health / Work tabs.");

            if (Find.CurrentMap == null)
            {
                Widgets.Label(new Rect(0f, 105f, inRect.width, 40f),
                    "No active colony map. Select a colony to review its colonists.");
                return;
            }

            var patients = Snapshot();
            float width = Math.Max(340f, inRect.width - 20f);
            Widgets.Label(new Rect(0f, 100f, width, 28f),
                "PAWN                     PRIORITY         HEALTH         BLEED RATE      STATE");
            if (patients.Count == 0)
            {
                Widgets.Label(new Rect(0f, 140f, width, 40f),
                    "No living spawned player colonists on this map.");
                return;
            }

            var viewport = new Rect(0f, 137f, inRect.width, Math.Max(0f, inRect.height - 178f));
            var canvas = new Rect(0f, 0f, Math.Max(320f, viewport.width - 20f),
                                  patients.Count * 32f + 10f);
            Widgets.BeginScrollView(viewport, ref scrollPosition, canvas);
            try
            {
                for (int index = 0; index < patients.Count; index++)
                {
                    var patient = patients[index];
                    float y = index * 32f;
                    Widgets.Label(new Rect(6f, y, 245f, 28f), patient.Label);
                    Widgets.Label(new Rect(252f, y, 130f, 28f), patient.Priority);
                    Widgets.Label(new Rect(395f, y, 95f, 28f), patient.Health);
                    Widgets.Label(new Rect(505f, y, 105f, 28f), patient.Bleed);
                    Widgets.Label(new Rect(625f, y, 125f, 28f),
                                  patient.Downed ? "DOWNED" : "MOBILE");
                }
            }
            finally
            {
                Widgets.EndScrollView();
            }

            Widgets.Label(new Rect(0f, inRect.height - 33f, inRect.width, 30f),
                $"Displayed {patients.Count} living colonists. Live read only; no treatment or jobs changed.");
        }
    }
}
