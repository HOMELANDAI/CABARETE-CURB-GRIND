# ccg_trick_input.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# Flat-trick input for Fortnite without custom Input Action assets: the stock locomotion inputs become
# the trick vocabulary while the rider is airborne.
#
#   Jump                                  -> ollie (counted when the rider lands, hops shorter than MinAirSeconds ignored)
#   Crouch tap in the air                 -> kickflip
#   Sprint tap in the air                 -> heelflip
#   Crouch then Sprint within ComboWindow -> popShoveIt
#   Sprint then Crouch within ComboWindow -> treFlip
#   Crouch held >= GrabHoldSeconds in air -> grab
#   Landing < LateInputBailSeconds after a flip input -> bail (combo lost)  — land clean or lose it
#
# One ccg_air_tracker per player subscribes to its fort_character events; it re-subscribes after an
# elimination because the respawned character is a new object. Scores go through ccg_game_manager
# (AwardTrick / Land / Bail), the same calls the debug buttons use.

using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Game }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /UnrealEngine.com/Temporary/SpatialMath }

ccg_trick_input<public> := class(creative_device):

    @editable Manager : ccg_game_manager = ccg_game_manager{}
    # Optional: shows the control legend to each rider when they join.
    @editable Hud : hud_message_device = hud_message_device{}
    @editable ShowControlsOnJoin : logic = true

    @editable ComboWindowSeconds : float = 0.35
    @editable GrabHoldSeconds : float = 0.4
    @editable LateInputBailSeconds : float = 0.12
    @editable MinAirSeconds : float = 0.25
    # Ignore jump/crouch/sprint events this long after a (re)spawn or a session refresh (teleports fire them).
    @editable SpawnGuardSeconds : float = 1.5

    MsgControls<localizes>:message = "TRICKS — Jump: ollie · Crouch in air: kickflip · Sprint in air: heelflip · Crouch→Sprint: shove-it · Sprint→Crouch: tre flip · hold Crouch: grab · land clean!"

    var Trackers<private>:[player]ccg_air_tracker = map{}

    OnBegin<override>()<suspends>:void =
        for (P : GetPlayspace().GetPlayers()) { Track(P) }
        GetPlayspace().PlayerAddedEvent().Subscribe(Track)

    Track(P:player):void =
        if (Trackers[P]) then return
        T := ccg_air_tracker{Manager := Manager, Player := P, Owner := Self}
        if (set Trackers[P] = T) {}
        T.Bind()
        if (ShowControlsOnJoin?):
            Hud.SetText(MsgControls)
            Hud.Show(P)

# Per-player air/trick state. Bound to the player's current fort_character.
ccg_air_tracker := class:
    Manager:ccg_game_manager
    Player:player
    Owner:ccg_trick_input

    var InAir:logic = false
    var AirStart:float = 0.0
    var LastTap:string = ""
    var LastTapTime:float = -10.0
    var CrouchDownTime:float = -10.0
    var CrouchDownInAir:logic = false
    var FlipsThisAir:int = 0
    var LastInputTime:float = -10.0
    var TapSeq:int = 0
    var BoundAt:float = -100.0

    Guarded()<transacts>:logic =
        if (GetSimulationElapsedTime() - BoundAt < Owner.SpawnGuardSeconds) then true else false

    Bind():void =
        if (C := Player.GetFortCharacter[]):
            set BoundAt = GetSimulationElapsedTime()
            C.JumpedEvent().Subscribe(OnJumped)
            C.CrouchedEvent().Subscribe(OnCrouched)
            C.SprintedEvent().Subscribe(OnSprinted)
            C.EliminatedEvent().Subscribe(OnEliminated)

    OnEliminated(Result:elimination_result):void =
        spawn{ Rebind() }

    # Wait for the respawned character, then subscribe again (new fort_character object).
    Rebind()<suspends>:void =
        var Tries:int = 0
        loop:
            Sleep(1.0)
            set Tries += 1
            if (C := Player.GetFortCharacter[], C.IsActive[]):
                Bind()
                break
            if (Tries > 60) then break

    OnJumped(C:fort_character):void =
        if (InAir?) then return
        if (Guarded()?) then return
        set InAir = true
        set AirStart = GetSimulationElapsedTime()
        set FlipsThisAir = 0
        set LastTap = ""
        spawn{ AirLoop(C) }

    AirLoop(C:fort_character)<suspends>:void =
        Sleep(0.1)
        loop:
            if (not C.IsActive[]) then break
            if (C.IsOnGround[]) then break
            Sleep(0.05)
        Now := GetSimulationElapsedTime()
        AirTime := Now - AirStart
        set InAir = false
        if (AirTime < Owner.MinAirSeconds) then return
        if (Guarded()?) then return
        Manager.AwardTrick(Player, "ollie")
        if (FlipsThisAir > 0 and Now - LastInputTime < Owner.LateInputBailSeconds):
            Manager.Bail(Player)
        else:
            Manager.Land(Player)

    OnCrouched(Args:tuple(fort_character, logic)):void =
        Started := Args(1)
        Now := GetSimulationElapsedTime()
        if (Started?):
            if (not InAir?) then return
            if (Guarded()?) then return
            set CrouchDownTime = Now
            set CrouchDownInAir = true
            Tap("crouch", Now)
        else:
            # Grab = crouch held in the air; the release may happen just after touchdown.
            if (CrouchDownInAir? and Now - CrouchDownTime >= Owner.GrabHoldSeconds):
                set TapSeq += 1   # cancels the pending kickflip from the press
                set LastTap = ""
                Award("grab")
                if (not InAir?) then Manager.Land(Player)
            set CrouchDownInAir = false

    OnSprinted(Args:tuple(fort_character, logic)):void =
        Started := Args(1)
        if (not Started?) then return
        if (not InAir?) then return
        if (Guarded()?) then return
        Tap("sprint", GetSimulationElapsedTime())

    Tap(Kind:string, Now:float):void =
        set LastInputTime = Now
        if (LastTap <> "" and LastTap <> Kind and Now - LastTapTime <= Owner.ComboWindowSeconds):
            Combo := if (LastTap = "crouch") then "popShoveIt" else "treFlip"
            set LastTap = ""
            set TapSeq += 1
            Award(Combo)
        else:
            set LastTap = Kind
            set LastTapTime = Now
            set TapSeq += 1
            Seq := TapSeq
            spawn{ DelayedSingle(Kind, Seq) }

    # A single tap pays out once the combo window has passed without a second tap.
    DelayedSingle(Kind:string, Seq:int)<suspends>:void =
        Sleep(Owner.ComboWindowSeconds)
        if (TapSeq = Seq):
            set LastTap = ""
            Award(if (Kind = "crouch") then "kickflip" else "heelflip")
            if (not InAir?) then Manager.Land(Player)

    Award(Name:string):void =
        Manager.AwardTrick(Player, Name)
        set FlipsThisAir += 1
