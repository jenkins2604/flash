Feature: Smoke Test
	Check firmware version
    Updating charging state B to C and vice versa

    Scenario: change state B to C
		Given the current state is B
        When EV switch to C
        Then the EVSE should switch to state C

	Scenario: Check firmware version
        When comparing the firmware version and git shash id
        Then the firmware version and shash id should match
