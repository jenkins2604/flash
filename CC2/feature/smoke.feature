Feature: Smoke Tests
    Check firmware version
    Updating charging state
    Check if CC2 react correctly when faults happen

    Scenario: Check firmware version
    When comparing the firmware version and git hash id
    Then the firmware version and hash id should match

    Scenario: change state A to B
    Given reset test station 
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
    
    @wip
    Scenario: Test shorted diode
    Given reset test station
    And the current state is C
    When trigger fault shorted diode
    Then the EVSE should switch to state F
    And wait for 30
    
    Scenario: Test negative CP
    Given reset test station 
    And the current state is B
    When trigger fault negative CP
    Then the EVSE should switch to state F
    And wait for 10
    
    Scenario: Test residue current
    Given reset test station 
    And the current state is C
    When trigger fault residue current
    Then the EVSE should switch to state F
    And error code should be OcuErrorRCMDC
    
