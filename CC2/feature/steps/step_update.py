from behave   import given, when, then
from hamcrest import assert_that, equal_to, is_not
from subprocess import Popen,PIPE
from pathlib import Path

def compare(version, hash_id):
    """
    Business logic how a Ninja should react to increase his survival rate.
    """
    assert version is not None
    assert hash_id is not None
    if version == hash_id:
        return "match"
    else:
        return "not match"


@when('comparing the firmware version and git shash id')
def step_comparing_the_firmware_version_and_git_shash_id(context):
    command = ["sshpass", "-p", "root", "ssh", "root@192.168.7.2", "cat /etc/version"]
    context.version = Popen(command, stdout=PIPE, stderr=PIPE).stdout.read()
    context.version = context.version.decode().strip('\n')
    
    p = Path(__file__).resolve(strict=True).parents[2]
    with open(p / "version") as f:
        context.hash_id = f.readline().strip('\n')

@then('the firmware version and shash id should {be}')
def step_the_firmware_version_and_shash_id_should(context, be):
    assert_that(compare(context.version, context.hash_id), equal_to(be))