#!/usr/bin/env python
import storyboard
import timeline

print("=" * 80)
print("STORYBOARD: Crash Scenario - Immediate DENM Transmission")
print("=" * 80)


def createStories(board):
    """
    Create crash incident story.
    
    Timeline:
    ---------
    t=50.0s: First vehicle to pass triggers crash
             - StopEffect: Vehicle stops immediately
             - SignalEffect: Emits "crash_incident" to middleware
             - CrashedVehicleService triggers DENM transmission
    
    Note: Using time-based condition (first vehicle after t=50s)
          instead of specific vehicle name for better portability.
    """
    # Crash occurs at t=200 seconds
    time_condition = storyboard.TimeCondition(timeline.seconds(200.0))
    
    # Use LimitCondition to affect only 1 vehicle
    limit_condition = storyboard.LimitCondition(1)
    
    # Effect 1: Emergency stop (vehicle immobilized)
    stop_effect = storyboard.StopEffect()
    
    # Effect 2: Signal emission (triggers CrashedVehicleService)
    signal_effect = storyboard.SignalEffect("crash_incident")
    
    # Combine conditions: after t=50s, affect first vehicle only
    combined_condition = storyboard.AndCondition(time_condition, limit_condition)
    crash_story = storyboard.Story(combined_condition, [stop_effect, signal_effect])
    
    # Register story
    board.registerStory(crash_story)
    
    print(f"[STORY REGISTERED]")
    print(f"  Type: CRASHED VEHICLE")
    print(f"  Vehicle ID: accident_veh_0")
    print(f"  Trigger Time: 200.0s")
    print(f"  Signal: 'crash_incident'")
    print(f"  Effects: Emergency Stop + Signal Emission")
    print("=" * 80)


