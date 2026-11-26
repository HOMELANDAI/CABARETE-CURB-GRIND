# ccg_game_manager.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# Central run manager: per-player score / combo / parks mastered, park-zone volumes,
# store volume, Sign Gap volume, P1 Vagamundo mastery gate, HUD, and the courtyard finish.
#
# Wire-up (see LEVEL_BUILD_GUIDE.md, "Device wiring table"):
#   ParkZoneP1..P4   -> volume_device around each park footprint
#   StoreVolume      -> volume_device over the HAI Skate Store (Ocean Dream Plaza, ~470 m)
#   SignGapVolume    -> volume_device spanning the gap between the Sign Twins at the start
#   FinishTrigger    -> trigger_device at the Courtyard Cabarete entrance (~1608 m)
#   VagamundoBarrier -> barrier_device across the Vagamundo roll-ins (P1 is locked until P2+P3+P4 mastered)
#   Hud              -> hud_message_device
#   EndGame          -> end_game_device (ends the run after the results message)
#   Store            -> the ccg_store device (earned-tier grants: GrantEarned / GrantLifetimeTier)
#   TrickButtons     -> optional button_devices for debugging tricks without animations
#
# Store tier events fired from here (see ccg_store.verse header for the key table):
#   park mastered (P2/P3/P4)      -> Store.GrantEarned(Agent, "park:<Id>")   Desert Dusk kaftan + deck
#   Vagamundo (P1) mastered       -> Store.GrantEarned(Agent, "park:P1")
#   Sign Gap cleared              -> Store.GrantEarned(Agent, "signgap")
#   every 25,000 lifetime points  -> Store.GrantLifetimeTier(Agent, N)       Original kaftan N + deck
#   trick milestones              -> "grinds:10|25|50", "trick:treFlip", "combo:5000|10000", "grindmeters:100" (knits)
#   first grind worth >= 50 pts   -> "grind:50" (fx_sparks — Metal Sparks; player toggles it with ccg_store.ToggleEffect)

using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Game }
using { /Fortnite.com/Playspaces }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /UnrealEngine.com/Temporary/SpatialMath }

# Per-player run state.
ccg_player_state<public> := class:
    var Score<public>:int = 0
    var Combo<public>:combo_tracker = combo_tracker{}
    var BestLine<public>:int = 0
    var GrindMeters<public>:float = 0.0
    # Park ids that reached masterScore in this run ("P2", "P3", "P4", and "P1" once unlocked+skated)
    var Mastered<public>:[]string = array{}
    # Points earned inside each park during this run, keyed by park id
    var ParkPoints<public>:[string]int = map{}
    var CurrentPark<public>:string = ""
    var Finished<public>:logic = false
    # Points banked across every run this session; each 25,000 grants the next Original kaftan.
    var LifetimePoints<public>:int = 0
    var LifetimeTiers<public>:int = 0
    # Trick-milestone counter for the earned knits.
    var CleanGrinds<public>:int = 0
    # Murals seen this run (ids from ccg_data.murals).
    var MuralsSeen<public>:[]string = array{}
    # Sign Gap guard (26 Nov): last award time, so one pass pays once.
    var LastSignGapAt<public>:float = -100.0

    HasSeenMural<public>(Id:string)<transacts>:logic =
        for (M : MuralsSeen, M = Id) { return true }
        return false

    HasMastered<public>(ParkId:string)<transacts>:logic =
        for (Id : Mastered, Id = ParkId) { return true }
        return false

ccg_game_manager<public> := class(creative_device):

    # ----- Park zones (volumes placed over each park footprint) -----
    @editable ParkZoneP1 : volume_device = volume_device{}   # Vagamundo Hybrid Park (bonus, locked)
    @editable ParkZoneP2 : volume_device = volume_device{}   # Carve Cabarete Multiplex (masterScore 25000)
    @editable ParkZoneP3 : volume_device = volume_device{}   # Mojito Skate Park (masterScore 20000)
    @editable ParkZoneP4 : volume_device = volume_device{}   # Courtyard Cabarete Skatepark (masterScore 20000)

    # ----- Other volumes / triggers -----
    @editable StoreVolume : volume_device = volume_device{}
    @editable SignGapVolume : volume_device = volume_device{}
    @editable SignGapGraceSeconds : float = 5.0
    @editable SignGapCooldownSeconds : float = 3.0
    # Six mural volumes (ccg_data.murals, in data order: vicewave, clisante_rush, over_everything,
    # schnauzer_detectives, ppa_microdrama, paw_power_arena) hugging each wallride wall; counted in the results.
    @editable MuralVolumes : []volume_device = array{}
    # Two volume_devices inside the Horseshoe Rail Skate Ramp tunnels (P4 bonus): +200 per pass-through.
    @editable TunnelVolumes : []volume_device = array{}
    MuralIds : []string = array{"mural_vicewave", "mural_clisante_rush", "mural_over_everything", "mural_schnauzer_detectives", "mural_ppa_microdrama", "mural_paw_power_arena"}
    @editable FinishTrigger : trigger_device = trigger_device{}

    # ----- Gating -----
    @editable VagamundoBarrier : barrier_device = barrier_device{}

    # ----- Presentation -----
    @editable Hud : hud_message_device = hud_message_device{}
    @editable EndGame : end_game_device = end_game_device{}
    @editable HudSeconds : float = 2.5

    # ----- Store (earned-tier grants) -----
    @editable Store : ccg_store = ccg_store{}
    LifetimeThreshold<public>:int = 25000
    MaxLifetimeTiers<public>:int = 10

    # ----- Optional debug trick buttons (index order: ollie, kickflip, heelflip, popShoveIt, treFlip, grab) -----
    @editable DebugTrickButtons : []button_device = array{}
    DebugTrickNames : []string = array{"ollie", "kickflip", "heelflip", "popShoveIt", "treFlip", "grab"}

    var States<private>:[player]ccg_player_state = map{}

    # ----- Localised HUD messages -----
    MsgScore<localizes>(Score:int, Combo:int):message = "Score {Score}   Combo x{Combo}"
    MsgTrick<localizes>(Trick:string, Points:int):message = "{Trick}  +{Points}"
    MsgGrind<localizes>(Meters:int, Points:int):message = "Grind {Meters} m  +{Points}"
    MsgLanded<localizes>(Points:int):message = "LANDED  +{Points}"
    MsgBail<localizes>:message = "BAIL — combo lost"
    MsgSignGap<localizes>(Points:int):message = "SIGN GAP!  +{Points}"
    MsgEnterPark<localizes>(Park:string):message = "{Park}"
    MsgMastered<localizes>(Park:string):message = "{Park} MASTERED"
    MsgVagamundoOpen<localizes>:message = "Vagamundo roof deck unlocked"
    MsgVagamundoLocked<localizes>:message = "Vagamundo is locked — master the Multiplex, Mojito and the Courtyard first"
    MsgStore<localizes>(Score:int):message = "HAI Skate Store — {Score} points to spend"
    MsgResults<localizes>(Score:int, Best:int, Parks:int, MuralCount:int, Lifetime:int, Tier:int):message = "COURTYARD REACHED\nScore {Score}\nBest line {Best}\nParks mastered {Parks}/4\nMurals seen {MuralCount}/6\nLifetime {Lifetime} (kaftan tier {Tier}/10)"
    MsgMural<localizes>(Seen:int):message = "MURAL {Seen}/6"
    MsgHorseshoe<localizes>(Meters:int, Points:int):message = "Horseshoe {Meters} m  +{Points}"
    MsgHorseshoeFull<localizes>(Points:int):message = "HORSESHOE BONUS — full U!  +{Points}"
    MsgTunnel<localizes>(Points:int):message = "TUNNEL  +{Points}"
    MsgLifetime<localizes>(Tier:int, Points:int):message = "LIFETIME {Points} — Original kaftan tier {Tier}/10"

    OnBegin<override>()<suspends>:void =
        # P1 starts locked.
        VagamundoBarrier.Enable()

        ParkZoneP1.AgentEntersEvent.Subscribe(OnEnterP1)
        ParkZoneP2.AgentEntersEvent.Subscribe(OnEnterP2)
        ParkZoneP3.AgentEntersEvent.Subscribe(OnEnterP3)
        ParkZoneP4.AgentEntersEvent.Subscribe(OnEnterP4)
        ParkZoneP1.AgentExitsEvent.Subscribe(OnExitPark)
        ParkZoneP2.AgentExitsEvent.Subscribe(OnExitPark)
        ParkZoneP3.AgentExitsEvent.Subscribe(OnExitPark)
        ParkZoneP4.AgentExitsEvent.Subscribe(OnExitPark)

        Store.SetManager(Self)
        StoreVolume.AgentEntersEvent.Subscribe(OnEnterStore)
        SignGapVolume.AgentEntersEvent.Subscribe(OnEnterSignGap)
        for (Vol : TunnelVolumes) { Vol.AgentEntersEvent.Subscribe(OnTunnel) }
        for (I := 0..MuralVolumes.Length - 1):
            if (Vol := MuralVolumes[I], Id := MuralIds[I]):
                Binding := ccg_mural_binding{Manager := Self, MuralId := Id}
                Vol.AgentEntersEvent.Subscribe(Binding.OnEnter)
        FinishTrigger.TriggeredEvent.Subscribe(OnFinish)

        for (I := 0..DebugTrickButtons.Length - 1):
            if (Button := DebugTrickButtons[I], Name := DebugTrickNames[I]):
                Binding := ccg_trick_button_binding{Manager := Self, TrickName := Name}
                Button.InteractedWithEvent.Subscribe(Binding.OnPressed)

        # Players who join late still get a state record.
        for (P : GetPlayspace().GetPlayers()) { GetState(P) }

    # ------------------------------------------------------------------
    # State access
    # ------------------------------------------------------------------
    GetState<public>(Player:player)<transacts>:ccg_player_state =
        if (S := States[Player]) then return S
        NewState := ccg_player_state{}
        if (set States[Player] = NewState) {}
        return NewState

    GetScore<public>(Player:player):int = GetState(Player).Score

    # Spend points (used by ccg_store). Fails if the player cannot afford it.
    TrySpend<public>(Player:player, Cost:int)<transacts><decides>:void =
        S := GetState(Player)
        S.Score >= Cost
        set S.Score -= Cost

    # ------------------------------------------------------------------
    # Scoring entry points (called by ccg_rail, animation hooks, debug buttons)
    # ------------------------------------------------------------------
    AwardTrick<public>(Agent:agent, TrickName:string):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            Points := ScoreTrick(TrickName)
            if (Points > 0):
                S.Combo.Add(TrickName, Points)
                ShowHud(Agent, MsgTrick(TrickName, Points))
                if (TrickName = "treFlip") then Store.GrantEarned(Agent, "trick:treFlip")

    AwardGrind<public>(Agent:agent, Meters:float):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            Points := ScoreGrind(Meters)
            set S.GrindMeters += Meters
            if (Points > 0):
                S.Combo.Add("grind", Points)
                set S.CleanGrinds += 1
                if (M := Round[Meters]):
                    ShowHud(Agent, MsgGrind(M, Points))
                if (Points >= 50) then Store.GrantEarned(Agent, "grind:50")   # Metal Sparks effect
                if (S.CleanGrinds = 10) then Store.GrantEarned(Agent, "grinds:10")
                if (S.CleanGrinds = 25) then Store.GrantEarned(Agent, "grinds:25")
                if (S.CleanGrinds = 50) then Store.GrantEarned(Agent, "grinds:50")
                if (S.GrindMeters >= 100.0) then Store.GrantEarned(Agent, "grindmeters:100")

    # P4 Horseshoe Rail Skate Ramp (ccg_rail.IsHorseshoe): 80/m, +2,500 Horseshoe Bonus for the full U.
    AwardHorseshoe<public>(Agent:agent, Meters:float, FullU:logic):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            var Points:int = 0
            if (M := Round[Meters * (ccg_scoring.HorseshoePerMeter * 1.0)]) then set Points = M
            if (FullU?) then set Points += ccg_scoring.HorseshoeFullU
            if (Points <= 0) then return
            S.Combo.Add("horseshoe", Points)
            set S.GrindMeters += Meters
            set S.CleanGrinds += 1
            if (FullU?):
                ShowHud(Agent, MsgHorseshoeFull(Points))
            else if (M := Round[Meters]):
                ShowHud(Agent, MsgHorseshoe(M, Points))
            if (Points >= 50) then Store.GrantEarned(Agent, "grind:50")

    OnTunnel(Agent:agent):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            S.Combo.Add("tunnel", ccg_scoring.HorseshoeTunnel)
            ShowHud(Agent, MsgTunnel(ccg_scoring.HorseshoeTunnel))

    # Clean landing: bank the combo into the score (and into the current park if inside one).
    Land<public>(Agent:agent):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            Banked := S.Combo.Land()
            if (Banked > 0):
                set S.Score += Banked
                if (Banked > S.BestLine) then set S.BestLine = Banked
                CreditPark(Agent, S, Banked)
                ShowHud(Agent, MsgLanded(Banked))
                ShowHud(Agent, MsgScore(S.Score, 1))
                if (Banked >= 5000) then Store.GrantEarned(Agent, "combo:5000")
                if (Banked >= 10000) then Store.GrantEarned(Agent, "combo:10000")
                AddLifetime(Agent, S, Banked)

    Bail<public>(Agent:agent):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            S.Combo.Bail()
            ShowHud(Agent, MsgBail)

    # Lifetime-points threshold loop: every 25,000 banked grants the next Original kaftan (+ its deck).
    # Lifetime points survive ResetRun but not the session (persist with a weak_map(player) if needed).
    AddLifetime<private>(Agent:agent, S:ccg_player_state, Points:int):void =
        set S.LifetimePoints += Points
        loop:
            if (S.LifetimeTiers >= MaxLifetimeTiers) then break
            Next := (S.LifetimeTiers + 1) * LifetimeThreshold
            if (S.LifetimePoints < Next) then break
            set S.LifetimeTiers += 1
            ShowHud(Agent, MsgLifetime(S.LifetimeTiers, S.LifetimePoints))
            Store.GrantLifetimeTier(Agent, S.LifetimeTiers)

    # ------------------------------------------------------------------
    # Parks & mastery
    # ------------------------------------------------------------------
    CreditPark<private>(Agent:agent, S:ccg_player_state, Points:int):void =
        if (S.CurrentPark = "") then return
        ParkId := S.CurrentPark
        var Total:int = Points
        if (Existing := S.ParkPoints[ParkId]) then set Total += Existing
        if (set S.ParkPoints[ParkId] = Total) {}
        Threshold := MasterScoreFor(ParkId)
        if (Threshold > 0, Total >= Threshold, not S.HasMastered(ParkId)?):
            set S.Mastered += array{ParkId}
            ShowHud(Agent, MsgMastered(ParkName(ParkId)))
            # Desert Dusk kaftan: one per park mastered (P2/P3/P4) and one for Vagamundo (P1).
            Store.GrantEarned(Agent, "park:{ParkId}")
            CheckVagamundoGate(Agent, S)

    MasterScoreFor(ParkId:string):int =
        if (ParkId = "P2") then return ccg_scoring.MasterScoreP2Multiplex
        if (ParkId = "P3") then return ccg_scoring.MasterScoreP3Mojito
        if (ParkId = "P4") then return ccg_scoring.MasterScoreP4Courtyard
        # P1 has masterScore 0 in the data: any landed line counts once it is unlocked.
        if (ParkId = "P1") then return 1
        return 0

    ParkName(ParkId:string):string =
        if (ParkId = "P1") then return "Vagamundo Hybrid Park"
        if (ParkId = "P2") then return "Carve Cabarete Multiplex"
        if (ParkId = "P3") then return "Mojito Skate Park"
        if (ParkId = "P4") then return "Courtyard Cabarete Skatepark"
        return ParkId

    # P1 unlocks when P2, P3 and P4 are all mastered. The barrier is a single world object,
    # so it opens for everyone once ANY player earns it (document this in multiplayer notes).
    CheckVagamundoGate<private>(Agent:agent, S:ccg_player_state):void =
        if (S.HasMastered("P2")?, S.HasMastered("P3")?, S.HasMastered("P4")?):
            VagamundoBarrier.Disable()
            ShowHud(Agent, MsgVagamundoOpen)

    OnEnterP1(Agent:agent):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            if (S.HasMastered("P2")?, S.HasMastered("P3")?, S.HasMastered("P4")?):
                EnterPark(Agent, S, "P1")
            else:
                ShowHud(Agent, MsgVagamundoLocked)
    OnEnterP2(Agent:agent):void = if (P := player[Agent]) { EnterPark(Agent, GetState(P), "P2") }
    OnEnterP3(Agent:agent):void = if (P := player[Agent]) { EnterPark(Agent, GetState(P), "P3") }
    OnEnterP4(Agent:agent):void = if (P := player[Agent]) { EnterPark(Agent, GetState(P), "P4") }

    EnterPark<private>(Agent:agent, S:ccg_player_state, ParkId:string):void =
        set S.CurrentPark = ParkId
        ShowHud(Agent, MsgEnterPark(ParkName(ParkId)))

    OnExitPark(Agent:agent):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            set S.CurrentPark = ""

    # ------------------------------------------------------------------
    # Store, Sign Gap, finish
    # ------------------------------------------------------------------
    # Murals (wallride walls): first pass per run counts toward the results.
    OnMural<public>(Agent:agent, MuralId:string):void =
        if (Player := player[Agent]):
            S := GetState(Player)
            if (not S.HasSeenMural(MuralId)?):
                set S.MuralsSeen += array{MuralId}
                ShowHud(Agent, MsgMural(S.MuralsSeen.Length))

    OnEnterStore(Agent:agent):void =
        if (Player := player[Agent]):
            ShowHud(Agent, MsgStore(GetState(Player).Score))

    # The Sign Gap volume sits between the two Cabarete Sign letter stacks ("Sign Twins"),
    # raised so only an airborne rider can clip it. Entering it = the gap was cleared.
    # Fix 26 Nov: the phantom "COMBO x1 +1,500" on spawn was this award (SignGap = 1,500), not the trick
    # input. The volume reached the spawn/ground, so walking in or spawning inside paid the gap. Now it only
    # pays an airborne rider, never in the first SignGapGraceSeconds of the session, and once per pass.
    OnEnterSignGap(Agent:agent):void =
        if (Player := player[Agent]):
            Now := GetSimulationElapsedTime()
            if (Now < SignGapGraceSeconds) then return
            if (C := Agent.GetFortCharacter[], C.IsOnGround[]) then return
            S := GetState(Player)
            if (Now - S.LastSignGapAt < SignGapCooldownSeconds) then return
            set S.LastSignGapAt = Now
            S.Combo.Add("signGap", ccg_scoring.SignGap)
            ShowHud(Agent, MsgSignGap(ccg_scoring.SignGap))
            Store.GrantEarned(Agent, "signgap")

    OnFinish(MaybeAgent:?agent):void =
        if (Agent := MaybeAgent?, Player := player[Agent]):
            S := GetState(Player)
            if (S.Finished?) then return
            set S.Finished = true
            # Bank whatever is still open.
            Land(Agent)
            spawn{ FinishSequence(Agent, S) }

    FinishSequence<private>(Agent:agent, S:ccg_player_state)<suspends>:void =
        Hud.SetText(MsgResults(S.Score, S.BestLine, S.Mastered.Length, S.MuralsSeen.Length, S.LifetimePoints, S.LifetimeTiers))
        Hud.Show(Agent)
        Sleep(6.0)
        EndGame.Activate(Agent)

    # ------------------------------------------------------------------
    # HUD helper
    # ------------------------------------------------------------------
    ShowHud<private>(Agent:agent, Text:message):void =
        Hud.SetText(Text)
        Hud.Show(Agent)

# Binds a debug button to a trick name without closures over loop variables.
ccg_trick_button_binding := class:
    Manager:ccg_game_manager
    TrickName:string
    OnPressed(Agent:agent):void =
        Manager.AwardTrick(Agent, TrickName)
        # Debug buttons auto-land so the score is visible immediately.
        Manager.Land(Agent)

# Binds a mural volume to its id without closures over loop variables.
ccg_mural_binding := class:
    Manager:ccg_game_manager
    MuralId:string
    OnEnter(Agent:agent):void = Manager.OnMural(Agent, MuralId)
