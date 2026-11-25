# ccg_rail.verse
# Cabarete Curb Grind — HomelandAI (HAI)
# A grindable rail. Place one ccg_rail device per rail (every S1..S5 roadside rail and each
# signature structure: Kite Line, Wave Rail, Palm Wrap, Chevron Switchback, Power-Line Rail,
# Twin Twist).
#
# ---------------------------------------------------------------------------------------------
# WHY THIS EXISTS — UEFN HAS NO NATIVE GRIND
# Fortnite's character has no rail-grind locomotion and Verse cannot read a USplineComponent.
# Two workable approaches were considered:
#
#   (A) cinematic_sequence_device per rail, Play(Agent) on entry.
#       + smooth, authored motion, camera control
#       - one Level Sequence authored per rail (~60 rails on the route), player loses input,
#         no variable entry speed, cannot early-exit cleanly, cannot measure metres grinded.
#
#   (B) "teleport-along-spline tick": the rail is described by an ordered list of empty
#       creative_prop markers (@editable RailPoints). On entering the catch volume the device
#       takes the fort_character and TeleportTo[]s it along the piecewise-linear path every
#       frame (Sleep(0.0)), facing along the segment, at the entry speed. Jumping, a timeout,
#       or reaching the end releases the rider; ccg_game_manager.AwardGrind(metres) is called.
#       + data driven (markers = spline points), per-player, measurable, early exit, works for
#         loops/spirals/zig-zags because it is just points
#       - teleport motion is stepped (hidden at 30+ Hz), no board tilt animation, and
#         Fortnite's own movement fights the teleport (we zero the risk by teleporting every tick)
#
#   >>> CHOSEN: (B) teleport-along-spline tick.  <<<
#   Marker spacing: 50–100 uu on straights, 25 uu around the Kite Line loop / Palm Wrap spiral.
# ---------------------------------------------------------------------------------------------

using { /Fortnite.com/Devices }
using { /Fortnite.com/Characters }
using { /Fortnite.com/Game }
using { /Verse.org/Simulation }
using { /UnrealEngine.com/Temporary/Diagnostics }
using { /UnrealEngine.com/Temporary/SpatialMath }

ccg_rail<public> := class(creative_device):

    @editable Manager : ccg_game_manager = ccg_game_manager{}

    # Human-readable id, e.g. "S2_north_03" or "wave_rail". Matches ccg_data.sections[].signature.id
    @editable RailId : string = "rail"

    # Ordered path markers. Use empty/invisible creative_props (e.g. a scaled-down "Prop Marker").
    # The rail mesh itself is separate — see RailMesh.
    @editable RailPoints : []creative_prop = array{}

    # The visible rail mesh (Pipe rail gallery piece or custom). Optional; used only for debug.
    @editable RailMesh : creative_prop = creative_prop{}

    # Catch volume: a thin volume_device over the rail's start (or the whole rail for mid-entry).
    @editable CatchVolume : volume_device = volume_device{}

    # Rider sits this far above the marker path (board + trucks on a pipe rail).
    @editable RideHeightCm : float = 95.0

    # Speed limits in uu/s (1 uu = 1 cm). 600 uu/s = 6 m/s.
    @editable MinSpeed : float = 350.0
    @editable MaxSpeed : float = 1200.0

    # Grind points are paid per world metre; the world is 0.6x so 1 uu = 1/60 m of game-world.
    # Set true to pay by "design metres" instead (divide by worldScale). Default: world metres.
    @editable PayDesignMeters : logic = false
    WorldScale : float = 0.6

    # true = slide (board under the deck) pays SlidePerMeter, false = grind (trucks) pays GrindPerMeter
    @editable IsSlideRail : logic = false

    # Safety: release after this many seconds no matter what.
    @editable MaxGrindSeconds : float = 12.0

    # Metal Sparks (store row fx_sparks, earned by the first 50-point grind, off by default):
    # a vfx_spawner_device mounted along this rail (orange-white sparks, see ccg_data.effects.sparks).
    # Enabled while a rider who owns AND switched on the effect is grinding; see ccg_store.IsEffectActive.
    @editable Sparks : vfx_spawner_device = vfx_spawner_device{}
    @editable IsSteel : logic = true   # sparks only on steel rails (set false for ledges / concrete)
    # P4 Horseshoe Rail Skate Ramp: pays 80/m via Manager.AwardHorseshoe (+2,500 when the whole U is ridden), sparks x2.
    @editable IsHorseshoe : logic = false

    # Graphics director (optional): lends a pooled spark light that follows the rider along the rail while
    # Metal Sparks are firing. Leave UseGraphics false if the island has no ccg_graphics device.
    @editable UseGraphics : logic = false
    @editable Graphics : ccg_graphics = ccg_graphics{}

    var Riding<private>:[player]logic = map{}

    OnBegin<override>()<suspends>:void =
        CatchVolume.AgentEntersEvent.Subscribe(OnEnter)
        if (RailPoints.Length < 2):
            Print("ccg_rail '{RailId}': needs at least 2 RailPoints")

    OnEnter(Agent:agent):void =
        if (Player := player[Agent]):
            if (Already := Riding[Player], Already?) then return
            if (set Riding[Player] = true) {}
            spawn{ Grind(Agent, Player) }

    # Main grind coroutine (one per rider).
    Grind<private>(Agent:agent, Player:player)<suspends>:void =
        defer:
            if (set Riding[Player] = false) {}

        if (Character := Agent.GetFortCharacter[], Character.IsActive[]):
            Points := PathPoints()
            if (Points.Length < 2) then return

            # Entry speed: horizontal speed when the rider hit the catch volume.
            Vel := Character.GetVelocity()
            var Speed:float = Sqrt(Vel.X * Vel.X + Vel.Y * Vel.Y)
            if (Speed < MinSpeed) then set Speed = MinSpeed
            if (Speed > MaxSpeed) then set Speed = MaxSpeed

            # Start at the closest segment to the rider (allows mid-rail entry).
            var SegIndex:int = ClosestSegment(Points, Character.GetTransform().Translation)
            var SegT:float = 0.0
            var Elapsed:float = 0.0
            var MetersGrinded:float = 0.0
            StartZ := Character.GetTransform().Translation.Z

            SparksOn := IsSteel? and Manager.Store.IsEffectActive(Player, "fx_sparks")?
            if (SparksOn?) then Sparks.Enable()
            var SparkLight:int = -1
            if (SparksOn? and UseGraphics?):
                if (Idx := Graphics.AcquireSparkLight[Character.GetTransform().Translation]) then set SparkLight = Idx
            var LightTick:int = 0

            loop:
                if (Elapsed > MaxGrindSeconds) then break
                if (SegIndex >= Points.Length - 1) then break
                if (A := Points[SegIndex], B := Points[SegIndex + 1]):
                    SegLen := Distance(A, B)
                    if (SegLen <= 0.001):
                        set SegIndex += 1
                        set SegT = 0.0
                    else:
                        Dt := 1.0 / 30.0
                        Step := Speed * Dt
                        set SegT += Step / SegLen
                        set MetersGrinded += Step / 100.0
                        set Elapsed += Dt
                        var Pos:vector3 = Lerp(A, B, SegT)
                        if (SegT >= 1.0):
                            set Pos = B
                            set SegIndex += 1
                            set SegT = 0.0
                        Dir := B - A
                        Yaw := RadiansToDegrees(ArcTan(Dir.Y, Dir.X))
                        Rot := MakeRotationFromYawPitchRollDegrees(Yaw, 0.0, 0.0)
                        Target := vector3{X := Pos.X, Y := Pos.Y, Z := Pos.Z + RideHeightCm}
                        if (not Character.TeleportTo[Target, Rot]):
                            break
                        # the borrowed spark light trails the board (every 3rd tick = 10 Hz is plenty for a glow)
                        if (SparkLight >= 0):
                            set LightTick += 1
                            if (Mod[LightTick, 3] = 0) then Graphics.MoveSparkLight(SparkLight, Pos)
                        # Early exit: the rider jumped (Fortnite jump sets a large +Z velocity).
                        V := Character.GetVelocity()
                        if (V.Z > 250.0 and Elapsed > 0.2) then break
                        Sleep(Dt)
                else:
                    break

            if (SparksOn?) then Sparks.Disable()
            if (SparkLight >= 0) then Graphics.ReleaseSparkLight(SparkLight)

            # Pay out. Convert world metres to design metres if requested.
            var PayMeters:float = MetersGrinded
            if (PayDesignMeters?) then set PayMeters = MetersGrinded / WorldScale
            if (IsHorseshoe?):
                # Full U = the rider reached the last marker (not released by a jump or the timeout).
                FullU := SegIndex >= Points.Length - 1
                Manager.AwardHorseshoe(Agent, PayMeters, FullU)
            else if (IsSlideRail?):
                Manager.AwardGrind(Agent, PayMeters * (70.0 / 60.0))   # SlidePerMeter / GrindPerMeter
            else:
                Manager.AwardGrind(Agent, PayMeters)
            # The manager banks the combo when the rider lands cleanly (Land) — see ccg_game_manager.

    # Marker transforms -> world positions.
    PathPoints<private>():[]vector3 =
        var Out:[]vector3 = array{}
        for (P : RailPoints):
            set Out += array{P.GetTransform().Translation}
        return Out

    ClosestSegment<private>(Points:[]vector3, From:vector3):int =
        var Best:int = 0
        var BestDist:float = 1000000000000.0
        for (I := 0..Points.Length - 2):
            if (A := Points[I]):
                D := Distance(A, From)
                if (D < BestDist):
                    set BestDist = D
                    set Best = I
        return Best
