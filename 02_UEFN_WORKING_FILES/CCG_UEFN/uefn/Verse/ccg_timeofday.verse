# ccg_timeofday.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# Sunset mode: a day / sunset toggle (ccg_data.timeOfDay). Values from the data:
#   day     sun elevation 62°, Caribbean noon (default)
#   sunset  sun elevation 6°, azimuth west (behind the Cabarete Sign), sky top #2B1E5A -> horizon #FF8A3D,
#           sun #FFB347, fog #E89A6B, ambient 0.35; park floodlights + street lamps on, neon shop signs lit.
#
# The always-works tier: the two looks are TWO Day Sequence devices authored in the editor (ccg_graphics layers the
# cinematic Environment-Light-Rig grade on top when its sequences are wired — see UEFN_GRAPHICS.md §2)
# (one paused at noon, one paused at the sunset time with the colours above baked into its Day Sequence
# settings) and this device enables one and disables the other. Lights are customizable_light_devices
# (floodlights: #FFF2D6, 9 m masts, 4 per park; street lamps: #FFD9A0 every 40 m design = 24 m world) turned
# on only in sunset; neon signs are creative_props (lit version) shown in sunset while their unlit twins hide.
#
# Wiring (LEVEL_BUILD_GUIDE.md -> "Sunset mode"):
#   DaySequence      -> day_sequence_device, time fixed at 12:00, Enabled at start
#   SunsetSequence   -> day_sequence_device, time fixed at ~17:50, Disabled at start
#   ParkFloodlights  -> customizable_light_device x16 (4 per park), off at start
#   StreetLamps      -> customizable_light_device along both curbs, off at start
#   MuralWashLights  -> customizable_light_device x6 aimed at the murals (ccg_data.murals), off at start
#   NeonLit / NeonUnlit -> creative_prop pairs for HAI SKATE, OJO CLUB, Mojito Bar, Full Moon, Olivia's
#   ToggleButton     -> button_device at the start screen / pause kiosk ("T" on other platforms)
#   Hud              -> hud_message_device

using { /Fortnite.com/Devices }
using { /Fortnite.com/Game }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }

ccg_timeofday<public> := class(creative_device):

    @editable DaySequence : day_sequence_device = day_sequence_device{}
    @editable SunsetSequence : day_sequence_device = day_sequence_device{}
    @editable ParkFloodlights : []customizable_light_device = array{}
    @editable StreetLamps : []customizable_light_device = array{}
    # Six mural wash lights (ccg_data.murals[].lightAtSunset), warm #FFD9A0 aimed at each mural; sunset only.
    @editable MuralWashLights : []customizable_light_device = array{}
    @editable NeonLit : []creative_prop = array{}
    @editable NeonUnlit : []creative_prop = array{}
    @editable ToggleButton : button_device = button_device{}
    @editable Hud : hud_message_device = hud_message_device{}
    # ccg_data.timeOfDay.modes[].default = "day"
    @editable StartInSunset : logic = false
    # Cross-fade the two Day Sequence devices instead of a hard swap (both devices: Fade Speed ≈ 0.4, Blend Time 4 s).
    @editable UseFade : logic = true

    # Other devices (ccg_rail sparks intensity, HUD tint) can read this.
    var Sunset<public>:logic = false

    # Fired on every change (true = sunset).
    ModeChangedEvent<public>:event(logic) = event(logic){}

    MsgDay<localizes>:message = "DAY — Caribbean noon"
    MsgSunset<localizes>:message = "SUNSET — golden hour, lights on"

    OnBegin<override>()<suspends>:void =
        ToggleButton.InteractedWithEvent.Subscribe(OnToggle)
        ApplyMode(StartInSunset)

    OnToggle(Agent:agent):void =
        ApplyMode(not Sunset?)
        if (Sunset?) then ShowHud(Agent, MsgSunset) else ShowHud(Agent, MsgDay)

    SetSunset<public>(Enable:logic):void = ApplyMode(Enable)

    ApplyMode<private>(ToSunset:logic):void =
        set Sunset = ToSunset
        if (ToSunset?):
            if (UseFade?):
                SunsetSequence.Enable()
                SunsetSequence.FadeIn()
                DaySequence.FadeOut()
            else:
                DaySequence.Disable()
                SunsetSequence.Enable()
            for (L : ParkFloodlights) { L.TurnOn() }
            for (L : StreetLamps) { L.TurnOn() }
            for (L : MuralWashLights) { L.TurnOn() }
            for (P : NeonLit) { P.Show() }
            for (P : NeonUnlit) { P.Hide() }
        else:
            if (UseFade?):
                DaySequence.Enable()
                DaySequence.FadeIn()
                SunsetSequence.FadeOut()
            else:
                SunsetSequence.Disable()
                DaySequence.Enable()
            for (L : ParkFloodlights) { L.TurnOff() }
            for (L : StreetLamps) { L.TurnOff() }
            for (L : MuralWashLights) { L.TurnOff() }
            for (P : NeonLit) { P.Hide() }
            for (P : NeonUnlit) { P.Show() }
        ModeChangedEvent.Signal(ToSunset)

    ShowHud<private>(Agent:agent, Text:message):void =
        Hud.SetText(Text)
        Hud.Show(Agent)
