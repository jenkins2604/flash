Feature: Integration Tests
    Updating charging state
    Check if CC2 react correctly when faults happen
    
    Scenario: change state A to B
    Given reset to state A 
    And the current state is A
    When EV switch to B
    Then the EVSE should switch to state B
    
    Scenario: change state B to C
    Given the current state is B
    When EV switch to C
    Then the EVSE should switch to state C
    
    Scenario: change state C to B
    Given the current state is C
    When EV switch to B
    Then the EVSE should switch to state B
    
    Scenario: Test shorted diode
    Given reset to state A
    And the current state is B
    When trigger fault shorted diode
    And the current state is C
    Then the EVSE should switch to state F
    And vendor error code should be OcuErrorNegativeCP
    And wait for 10
    
    Scenario: Test residue current
    Given reset to state A
    And the current state is C
    When trigger fault residue current
    And wait for 5
    Then the EVSE should switch to state F
    And vendor error code should be OcuErrorRCMDC
    
    Scenario: Test contactor welded close
    Given reset to state A
    When trigger fault contactor welded close
    And wait for 30
    Then the EVSE should switch to state F
    
