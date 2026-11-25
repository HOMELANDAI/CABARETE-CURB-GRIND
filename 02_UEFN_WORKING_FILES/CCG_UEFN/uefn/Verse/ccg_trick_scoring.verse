# ccg_trick_scoring.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# Scoring module. Point values mirror ccg_data.json -> "scoring". Keep them in sync by hand
# (UEFN Verse cannot read JSON at runtime). Source of truth: platforms/shared/ccg_data.json.

using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

# ---------------------------------------------------------------------------
# Point constants (ccg_data.scoring)
# ---------------------------------------------------------------------------
ccg_scoring<public> := module:
    Ollie<public>:int = 100
    Kickflip<public>:int = 400
    Heelflip<public>:int = 400
    PopShoveIt<public>:int = 300
    TreFlip<public>:int = 900
    GrindPerMeter<public>:int = 60
    SlidePerMeter<public>:int = 70
    ManualPerMeter<public>:int = 40
    Spin180<public>:int = 200
    Spin360<public>:int = 600
    Grab<public>:int = 250
    SignGap<public>:int = 1500
    # P4 bonus feature — Horseshoe Rail Skate Ramp (parks[P4].bonusFeature.scoring)
    HorseshoePerMeter<public>:int = 80
    HorseshoeTunnel<public>:int = 200
    HorseshoeFullU<public>:int = 2500
    HorseshoeSparksBoost<public>:float = 2.0
    # Each extra trick in a combo adds this to the multiplier (1.0, 1.5, 2.0, ...)
    ComboMultiplierStep<public>:float = 0.5
    # "bailPenalty": "lose current combo" — implemented in combo_tracker.Bail()
    MaxComboMultiplier<public>:float = 8.0

    # Park mastery thresholds (ccg_data.parks[].masterScore)
    MasterScoreP2Multiplex<public>:int = 25000
    MasterScoreP3Mojito<public>:int = 20000
    MasterScoreP4Courtyard<public>:int = 20000

    # Look up a flat trick by its data key. Returns 0 for unknown names.
    TrickPoints<public>(Name:string):int =
        if (Name = "ollie") then return Ollie
        if (Name = "kickflip") then return Kickflip
        if (Name = "heelflip") then return Heelflip
        if (Name = "popShoveIt" or Name = "shoveit" or Name = "pop_shove_it") then return PopShoveIt
        if (Name = "treFlip" or Name = "treflip" or Name = "360flip") then return TreFlip
        if (Name = "spin180") then return Spin180
        if (Name = "spin360") then return Spin360
        if (Name = "grab") then return Grab
        if (Name = "signGap" or Name = "sign_gap") then return SignGap
        return 0

# ---------------------------------------------------------------------------
# combo_tracker — one per player. Accumulates banked points for the current line.
# Call Land() when the rider rolls away clean, Bail() when they fall.
# ---------------------------------------------------------------------------
combo_tracker<public> := class:
    var TrickCount<private>:int = 0
    var BasePoints<private>:int = 0
    var LastTrick<private>:string = ""

    GetTrickCount<public>():int = TrickCount
    GetBasePoints<public>():int = BasePoints
    GetLastTrick<public>():string = LastTrick

    # Multiplier = 1 + step * (tricks - 1), clamped.
    GetMultiplier<public>():float =
        if (TrickCount <= 1) then return 1.0
        Raw := 1.0 + ccg_scoring.ComboMultiplierStep * (1.0 * (TrickCount - 1))
        if (Raw > ccg_scoring.MaxComboMultiplier) then return ccg_scoring.MaxComboMultiplier
        return Raw

    # Points the combo is worth right now if landed.
    GetPendingPoints<public>():int =
        Scaled := GetMultiplier() * (1.0 * BasePoints)
        if (Rounded := Round[Scaled]) then return Rounded
        return BasePoints

    # Add a trick's base points to the open combo.
    Add<public>(Name:string, Points:int)<transacts>:void =
        if (Points <= 0) then return
        set TrickCount += 1
        set BasePoints += Points
        set LastTrick = Name

    # Rider landed clean: bank and reset. Returns the banked total.
    Land<public>()<transacts>:int =
        Banked := GetPendingPoints()
        Reset()
        return Banked

    # Rider bailed: "lose current combo". Returns 0.
    Bail<public>()<transacts>:int =
        Reset()
        return 0

    Reset<public>()<transacts>:void =
        set TrickCount = 0
        set BasePoints = 0
        set LastTrick = ""

# ---------------------------------------------------------------------------
# Free functions
# ---------------------------------------------------------------------------

# Base points for a named flat trick (before the combo multiplier).
ScoreTrick<public>(Name:string):int =
    Points := ccg_scoring.TrickPoints(Name)
    if (Points = 0):
        Print("ccg_trick_scoring: unknown trick '{Name}'")
    return Points

# Base points for a grind of the given length in metres (world metres, i.e. after worldScale).
ScoreGrind<public>(Meters:float):int =
    if (Meters <= 0.0) then return 0
    Raw := (1.0 * ccg_scoring.GrindPerMeter) * Meters
    if (Rounded := Round[Raw]) then return Rounded
    return 0

# Board slides (rail under the deck, not the trucks) pay slightly more per metre.
ScoreSlide<public>(Meters:float):int =
    if (Meters <= 0.0) then return 0
    Raw := (1.0 * ccg_scoring.SlidePerMeter) * Meters
    if (Rounded := Round[Raw]) then return Rounded
    return 0

ScoreManual<public>(Meters:float):int =
    if (Meters <= 0.0) then return 0
    Raw := (1.0 * ccg_scoring.ManualPerMeter) * Meters
    if (Rounded := Round[Raw]) then return Rounded
    return 0
