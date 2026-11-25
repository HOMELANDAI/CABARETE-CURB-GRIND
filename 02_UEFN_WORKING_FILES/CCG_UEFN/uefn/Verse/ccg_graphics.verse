# ccg_graphics.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# Graphics director for the island: the "max" visual tier on top of ccg_timeofday.
#
#   • Cinematic grade swap   — one Level Sequence (LS_CCG_Sunset, 6 s) animates the Environment Light Rig
#                              (DirectionalLight, SkyAtmosphere, SkyLight, ExponentialHeightFog, the ColorGradient /
#                              post-process volume) from the Caribbean-noon grade to the golden-hour grade.
#                              Sunset = Play(), day = PlayReverse(): no second rig, no pop.
#   • Wet road               — LS_CCG_WetRoad animates the Wetness scalar on the road / park material instances
#                              (0 → 0.35) so Lumen picks up the floodlights + neon in the asphalt.
#   • Heat haze              — vfx_spawner_devices (Heat Distortion preset) at the Horseshoe tunnel exits and above the
#                              floodlight heads; sunset only.
#   • Spark lights           — a small pool of customizable_light_devices (warm orange, Cast Shadows OFF) that
#                              ccg_rail borrows while a rider grinds with Metal Sparks on: the light teleports to the
#                              rail, turns on, and is handed back when the grind ends. Fortnite caps dynamic lights,
#                              so the pool (default 2) is the budget, not the rail count.
#   • Mural wash flicker     — optional slow sodium-lamp flicker on the six mural washes (DimLight / UndimLight).
#   • Quality tiers          — Low-end skips the haze and the spark lights (mobile / Switch); High keeps everything.
#
# Everything is optional: leave a slot empty and that feature is skipped. ccg_timeofday still runs the Day Sequence
# device swap (the always-works tier); this device layers the cinematic tier on top when the sequences exist.
#
# Wiring (UEFN_GRAPHICS.md §2–§6):
#   TimeOfDay          -> the island's ccg_timeofday device
#   SunsetSequence     -> cinematic_sequence_device playing LS_CCG_Sunset   (Everyone, not looping)
#   WetRoadSequence    -> cinematic_sequence_device playing LS_CCG_WetRoad  (Everyone, not looping)
#   HeatHaze           -> vfx_spawner_device x N (Heat Distortion), disabled at start
#   SparkLights        -> customizable_light_device x2..3, off at start, radius 350, #FF9A3C, shadows off
#   MuralWashLights    -> same six lights ccg_timeofday owns (for the flicker)

using { /Fortnite.com/Devices }
using { /Fortnite.com/Game }
using { /Verse.org/Simulation }
using { /Verse.org/Random }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /UnrealEngine.com/Temporary/SpatialMath }

ccg_quality_tier<public> := enum:
    LowEnd      # mobile / Switch: no haze, no spark lights, no flicker
    HighEnd     # PC / current consoles: everything

ccg_graphics<public> := class(creative_device):

    @editable TimeOfDay : ccg_timeofday = ccg_timeofday{}
    @editable Quality : ccg_quality_tier = ccg_quality_tier.HighEnd

    # Cinematic tier (optional)
    @editable UseCinematicGrade : logic = true
    @editable SunsetSequence : cinematic_sequence_device = cinematic_sequence_device{}
    @editable WetRoadSequence : cinematic_sequence_device = cinematic_sequence_device{}

    # Sunset-only atmosphere
    @editable HeatHaze : []vfx_spawner_device = array{}

    # Spark light pool (ccg_rail borrows these)
    @editable SparkLights : []customizable_light_device = array{}
    # How far above the rail path the spark light sits (cm).
    @editable SparkLightHeightCm : float = 60.0

    # Mural washes (same devices as ccg_timeofday.MuralWashLights) + a slow flicker
    @editable MuralWashLights : []customizable_light_device = array{}
    @editable MuralWashFlicker : logic = true
    @editable FlickerMinSeconds : float = 4.0
    @editable FlickerMaxSeconds : float = 11.0

    var SparkBusy<private>:[int]logic = map{}
    var Sunset<private>:logic = false

    OnBegin<override>()<suspends>:void =
        TimeOfDay.ModeChangedEvent.Subscribe(OnMode)
        for (L : SparkLights) { L.TurnOff() }
        for (H : HeatHaze) { H.Disable() }
        # match whatever ccg_timeofday started in
        OnMode(TimeOfDay.Sunset)
        if (MuralWashFlicker? and Quality = ccg_quality_tier.HighEnd):
            spawn{ FlickerLoop() }

    OnMode(ToSunset:logic):void =
        set Sunset = ToSunset
        if (UseCinematicGrade?):
            if (ToSunset?):
                SunsetSequence.Play()
                WetRoadSequence.Play()
            else:
                SunsetSequence.PlayReverse()
                WetRoadSequence.PlayReverse()
        if (Quality = ccg_quality_tier.HighEnd):
            for (H : HeatHaze):
                if (ToSunset?) then H.Enable() else H.Disable()

    # --- spark light pool -------------------------------------------------------------------------------------
    # Returns the pool index of a light now parked at Position and turned on, or false when none is free / low tier.
    AcquireSparkLight<public>(Position:vector3)<decides><transacts>:int =
        Quality = ccg_quality_tier.HighEnd
        var Found:int = -1
        for (I := 0..SparkLights.Length - 1, Found < 0):
            if (B := SparkBusy[I], B?) {} else { set Found = I }
        Found >= 0
        L := SparkLights[Found]
        if (set SparkBusy[Found] = true) {}
        Target := vector3{X := Position.X, Y := Position.Y, Z := Position.Z + SparkLightHeightCm}
        if (L.TeleportTo[Target, IdentityRotation()]) {}
        L.TurnOn()
        Found

    MoveSparkLight<public>(Index:int, Position:vector3):void =
        if (L := SparkLights[Index]):
            Target := vector3{X := Position.X, Y := Position.Y, Z := Position.Z + SparkLightHeightCm}
            if (L.TeleportTo[Target, IdentityRotation()]) {}

    ReleaseSparkLight<public>(Index:int):void =
        if (L := SparkLights[Index]):
            L.TurnOff()
            if (set SparkBusy[Index] = false) {}

    # --- mural wash flicker -------------------------------------------------------------------------------------
    FlickerLoop<private>()<suspends>:void =
        loop:
            Sleep(GetRandomFloat(FlickerMinSeconds, FlickerMaxSeconds))
            if (Sunset? and MuralWashLights.Length > 0):
                Pick := GetRandomInt(0, MuralWashLights.Length - 1)
                if (L := MuralWashLights[Pick]):
                    # two quick dips: sodium lamp warming
                    L.DimLight()
                    Sleep(0.08)
                    L.UndimLight()
                    Sleep(0.12)
                    L.DimLight()
                    Sleep(0.06)
                    L.UndimLight()
