using System;

namespace KiloAI.ColonyTriage
{
    // Pure independent scoring. No Unity, network, save or RimWorld mutation.
    // These are prioritization hints, NOT medical diagnosis or treatment orders.
    public static class TriageRules
    {
        public static float Clean(float value, float minimum, float maximum)
        {
            if (float.IsNaN(value) || float.IsInfinity(value))
                return minimum;
            if (value < minimum) return minimum;
            if (value > maximum) return maximum;
            return value;
        }

        public static int PriorityScore(float healthFraction, float bleedRate, bool downed)
        {
            float hp = Clean(healthFraction, 0f, 1f);
            float bleed = Clean(bleedRate, 0f, 10f);
            int injury = (int)Math.Round((1f - hp) * 100f, MidpointRounding.AwayFromZero);
            int bleeding = (int)Math.Round(bleed * 150f, MidpointRounding.AwayFromZero);
            // Downed patients are always important, but severe bleeding and
            // low health can still place other pawns above them.
            return injury + bleeding + (downed ? 150 : 0);
        }

        public static string Priority(float healthFraction, float bleedRate, bool downed)
        {
            float hp = Clean(healthFraction, 0f, 1f);
            float bleed = Clean(bleedRate, 0f, 10f);
            if (downed || hp <= 0.30f || bleed >= 0.50f) return "CRITICAL";
            if (hp <= 0.65f || bleed >= 0.10f) return "URGENT";
            return "WATCH";
        }

        public static string HealthText(float healthFraction)
        {
            int pct = (int)Math.Round(Clean(healthFraction, 0f, 1f) * 100f,
                                      MidpointRounding.AwayFromZero);
            return pct.ToString() + "%";
        }

        public static string BleedText(float bleedRate)
        {
            return Clean(bleedRate, 0f, 10f).ToString("0.00",
                System.Globalization.CultureInfo.InvariantCulture);
        }
    }
}
