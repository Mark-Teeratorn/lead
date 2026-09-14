"""Tests for the CARLA sensor rig specification."""

import pytest

from lead.common.sensors.av_sensor_setup import SensorSpec, av_sensor_setup
from lead.config import ExpertConfig, load_lead_config


@pytest.fixture
def expert_config() -> ExpertConfig:
    """Default expert config without any overrides."""
    return load_lead_config().expert


def _sensor_ids(sensor_specs: list[SensorSpec]) -> list[str]:
    return [str(sensor_spec["id"]) for sensor_spec in sensor_specs]


class TestSensorAgentRig:
    """The rig a driving agent attaches."""

    def test_camera_subset_without_radars(self, expert_config: ExpertConfig) -> None:
        sensor_ids = _sensor_ids(
            av_sensor_setup(
                config=expert_config,
                perturbation_rotation=0.0,
                perturbation_translation=0.0,
                lidar=True,
                perturbate=False,
                sensor_agent=True,
                radar=False,
                camera_indices=[1, 2, 3],
            ),
        )
        camera_ids = [
            sensor_id for sensor_id in sensor_ids if sensor_id.startswith("rgb")
        ]
        assert camera_ids == ["rgb_1", "rgb_2", "rgb_3"]
        assert not any(sensor_id.startswith("radar") for sensor_id in sensor_ids)
        assert "lidar1" in sensor_ids
        assert "lidar2" in sensor_ids

    def test_whole_rig_by_default(self, expert_config: ExpertConfig) -> None:
        sensor_ids = _sensor_ids(
            av_sensor_setup(
                config=expert_config,
                perturbation_rotation=0.0,
                perturbation_translation=0.0,
                lidar=True,
                perturbate=False,
                sensor_agent=True,
                radar=True,
            ),
        )
        camera_ids = [
            sensor_id for sensor_id in sensor_ids if sensor_id.startswith("rgb")
        ]
        radar_ids = [
            sensor_id for sensor_id in sensor_ids if sensor_id.startswith("radar")
        ]
        assert camera_ids == [
            f"rgb_{index}"
            for index in range(1, expert_config.sensor_rig.num_cameras + 1)
        ]
        assert radar_ids == [
            f"radar{index}"
            for index in range(1, expert_config.sensor_rig.num_radar_sensors + 1)
        ]
