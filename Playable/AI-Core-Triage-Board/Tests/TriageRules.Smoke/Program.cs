using System;
using KiloAI.ColonyTriage;

static class Program
{
    static int checks = 0;
    static void Assert(bool condition, string message)
    {
        checks++;
        if (!condition) throw new Exception("TRIAGE_FAIL: " + message);
    }

    static void Main()
    {
        Assert(TriageRules.Priority(1.0f, 0f, false) == "WATCH", "healthy is watch");
        Assert(TriageRules.Priority(0.64f, 0f, false) == "URGENT", "hurt needs review");
        Assert(TriageRules.Priority(0.29f, 0f, false) == "CRITICAL", "severely hurt is critical");
        Assert(TriageRules.Priority(1.0f, 0.51f, false) == "CRITICAL", "bleeding triggers critical");
        Assert(TriageRules.Priority(1.0f, 0f, true) == "CRITICAL", "downed triggers critical");
        Assert(TriageRules.PriorityScore(1.0f, 0f, false) == 0, "healthy baseline");
        Assert(TriageRules.PriorityScore(0.5f, 0f, false) == 50, "injury scale");
        Assert(TriageRules.PriorityScore(0.5f, 0.25f, true) > 
               TriageRules.PriorityScore(0.5f, 0.25f, false), "downed boost");
        Assert(TriageRules.PriorityScore(0.1f, 5f, false) >
               TriageRules.PriorityScore(0.5f, 0.0f, true),
               "dangerous bleeding beats a merely downed target");
        Assert(TriageRules.Clean(-5, 0f, 1f) == 0, "negative clamp");
        Assert(TriageRules.Clean(5, 0f, 1f) == 1, "high clamp");
        Assert(TriageRules.Clean(float.NaN, 0f, 1f) == 0, "NaN fails safely");
        Assert(TriageRules.Clean(float.PositiveInfinity, 0f, 1f) == 0,
               "nonfinite inputs fail safely");
        Assert(TriageRules.PriorityScore(float.NaN, float.PositiveInfinity, false) == 100,
               "corrupt inputs cannot poison or overflow scoring");
        Assert(TriageRules.HealthText(0.456f) == "46%", "health percent displayed");
        Assert(TriageRules.HealthText(5f) == "100%", "health display bounded");
        Assert(TriageRules.BleedText(-1f) == "0.00", "bleed display bounded");
        Assert(TriageRules.PriorityScore(0.3f, 0.2f, false) ==
               TriageRules.PriorityScore(0.3f, 0.2f, false), "determinism");
        Console.WriteLine("RIMWORLD_TRIAGE_RULES_OK (" + checks + " assertions)");
    }
}
