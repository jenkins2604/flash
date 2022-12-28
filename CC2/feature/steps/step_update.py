from behave import when, then
from hamcrest import assert_that, equal_to
from subprocess import Popen,PIPE
from pathlib import Path


def compare(version, hash_id):
    assert version is not None
    assert hash_id is not None
    version = version.splitlines()
    hash_id = hash_id.splitlines()
    print(version)
    print(hash_id)
    if version[0] == hash_id[0]:
        return "match"
    else:
        return "not match"

@when('comparing the firmware version and git hash id')
def step_comparing_the_firmware_version_and_git_hash_id(context):
    command = ["sshpass", "-p", "root", "ssh", "root@192.168.7.2", "cat /etc/version"]
    context.version = Popen(command, stdout=PIPE, stderr=PIPE).stdout.read()
    context.version = context.version.decode().strip('\n')

    p = Path(__file__).resolve(strict=True).parents[2]
    with open(p / "version") as f:
        context.hash_id = f.read()

@then('the firmware version and hash id should {be}')
def step_the_firmware_version_and_hash_id_should(context, be):
    assert_that(compare(context.version, context.hash_id), equal_to(be))
