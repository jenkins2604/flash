Feature: Smoke Tests
    Run smoke tests
    
    Scenario: Check firmware version
    When comparing the firmware version and git hash id
    Then the firmware version and hash id should match
    
    Scenario: check status of test station
    Then the EVSE should switch to state B
    And error code should be NoError
    
