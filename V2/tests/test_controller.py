import pytest
from controller import ScaleController
from fakes import FakeButton, FakeLED, FakeHX, FakePixel

def make_ctrl(weights):
    return ScaleController(
        hx=FakeHX(weights),
        relay=FakeLED(),
        button_1=FakeButton(),
        button_2=FakeButton(),
        override_switch=FakeButton(),
        pixel_1=FakePixel(),
        pixel_2=FakePixel(),
    )

def test_override_always_turns_on_relay():
    ctrl = make_ctrl([0, 0, 0])
    ctrl.override_switch.is_pressed = True
    state = ctrl.tick()
    assert state == "override"
    assert ctrl.relay.is_lit  # relay forced on

def test_job_runs_until_target_hit():
    ctrl = make_ctrl([0]*5 + [9]*5 + [11]*5)  # passes target on 3rd tick group
    ctrl.button_2.is_pressed = True          # start job
    assert ctrl.tick() == "job_started"
    ctrl.button_2.is_pressed = False         # release button

    # still running, weight < target
    for _ in range(2):
        assert ctrl.tick() == "job_running"
        assert ctrl.relay.is_lit

    # now weight crosses target
    assert ctrl.tick() == "job_finished"
    assert not ctrl.relay.is_lit

def test_hold_button_sets_target_weight():
    ctrl = make_ctrl([5]*20)  # every reading 5 lbs
    ctrl.button_1.is_pressed = True
    # press for HOLD_DURATION ticks
    for i in range(ScaleController.HOLD_DURATION):
        state = ctrl.tick()
    assert state == "weight_set"
    assert ctrl.target_weight == 5
