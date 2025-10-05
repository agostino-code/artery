#!/usr/bin/env python
import os
import storyboard
import timeline

print("=" * 80)
print("STORYBOARD: Witness Scenario - Delayed DENM Transmission")
print("=" * 80)

# Default witness reaction delay (seconds)
DEFAULT_WITNESS_DELAY = 3.0


def _resolve_witness_delay() -> float:
    """
    Resolve witness delay from environment variable or use default.
    
    Returns:
        float: Witness delay in seconds (>= 0)
    """
    env_value = os.environ.get("STELVIO_WITNESS_DELAY")
    
    if not env_value:
        print(f"[CONFIG] STELVIO_WITNESS_DELAY not set, using default: {DEFAULT_WITNESS_DELAY}s")
        return DEFAULT_WITNESS_DELAY
    
    try:
        delay = float(env_value)
        if delay < 0:
            raise ValueError("Delay must be non-negative")
        print(f"[CONFIG] STELVIO_WITNESS_DELAY = {delay}s")
        return delay
    except ValueError as e:
        print(f"[ERROR] Invalid STELVIO_WITNESS_DELAY: '{env_value}' ({e})")
        print(f"[CONFIG] Using default: {DEFAULT_WITNESS_DELAY}s")
        return DEFAULT_WITNESS_DELAY


def createStories(board):
    """
    Create witness scenario stories.
    
    Timeline:
    ---------
    t=200.0s: accident_veh_0 crashes silently
              - StopEffect: Vehicle stops (no signal)
              
    t=200.0+DELAY: witness_veh_0 reports accident
              - SignalEffect: Emits "witness_report" to middleware
              - WitnessVehicleService triggers DENM transmission
    """
    witness_delay = _resolve_witness_delay()
    
    # -------------------------------------------------------------------------
    # STORY 1: Accident Vehicle (Silent Crash - No DENM)
    # -------------------------------------------------------------------------
    accident_time = storyboard.TimeCondition(timeline.seconds(200.0))
    accident_limit = storyboard.LimitCondition(1)  # Affect only 1 vehicle
    stop_effect = storyboard.StopEffect()
    
    accident_condition = storyboard.AndCondition(accident_time, accident_limit)
    accident_story = storyboard.Story(accident_condition, [stop_effect])
    board.registerStory(accident_story)
    
    print(f"[STORY 1 REGISTERED] ACCIDENT (Silent)")
    print(f"  Trigger Time: 50.0s (first vehicle)")
    print(f"  Effect: Emergency Stop Only (NO DENM)")
    
    # -------------------------------------------------------------------------
    # STORY 2: Witness Vehicle (Delayed DENM Reporting)
    # -------------------------------------------------------------------------
    witness_trigger_time = 200.0 + witness_delay
    witness_time = storyboard.TimeCondition(timeline.seconds(witness_trigger_time))
    witness_limit = storyboard.LimitCondition(1)  # Affect only 1 vehicle (the witness)
    signal_effect = storyboard.SignalEffect("witness_report")
    
    witness_condition = storyboard.AndCondition(witness_time, witness_limit)
    witness_story = storyboard.Story(witness_condition, [signal_effect])
    board.registerStory(witness_story)
    
    print(f"\n[STORY 2 REGISTERED] WITNESS (Delayed Report)")
    print(f"  Trigger Time: {witness_trigger_time:.1f}s (second vehicle)")
    print(f"  Witness Delay: {witness_delay:.1f}s")
    print(f"  Signal: 'witness_report'")
    print(f"  Effect: DENM Transmission")
    print("=" * 80)


