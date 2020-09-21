# Copyright 2020-present NAVER Corp. Under BSD 3-clause license

"""
Merge kapture objects with remapping of identifiers.
"""

from typing import List, Optional, Type, Dict

import kapture
from kapture.io.records import TransferAction, get_image_fullpath
from kapture.utils.Collections import get_new_if_not_empty

from .merge_reconstruction import merge_keypoints, merge_descriptors, merge_global_features, merge_matches
from .merge_reconstruction import merge_points3d_and_observations, merge_points3d
from .merge_records_data import merge_records_data


def get_sensors_mapping(sensors: kapture.Sensors, offset: int = 0) -> Dict[str, str]:
    """
    Creates list of sensor names,identifiers

    :param sensors: list of sensor definitions
    :param offset: optional offset for the identifier numbers
    :return: mapping of sensor names to identifiers
    """
    return {k: f'sensor{v}' for k, v in zip(sensors.keys(), range(offset, offset + len(sensors)))}


def get_rigs_mapping(rigs: kapture.Rigs, offset: int = 0) -> Dict[str, str]:
    """
    Creates list of rig names,identifiers

    :param rigs: list of rig definitions
    :param offset: optional offset for the identifier numbers
    :return: mapping of rig names to identifiers
    """
    return {k: f'rig{v}' for k, v in zip(rigs.keys(), range(offset, offset + len(rigs)))}


def merge_sensors(
        sensors_list: List[Optional[kapture.Sensors]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.Sensors:
    """
    Merge several sensors list into one list with new identifiers.

    :param sensors_list: list of sensors definitions to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged sensors definitions
    """
    assert len(sensors_list) > 0
    assert len(sensors_list) == len(sensor_mappings)

    merged_sensors = kapture.Sensors()
    for sensors, mapping in zip(sensors_list, sensor_mappings):
        if sensors is None:
            continue
        for sensor_id in sensors.keys():
            new_id = mapping[sensor_id]
            merged_sensors[new_id] = sensors[sensor_id]
    return merged_sensors


def merge_rigs(
        rigs_list: List[Optional[kapture.Rigs]],
        rig_mappings: List[Dict[str, str]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.Rigs:
    """
    Merge several rigs list into one list with new identifiers for the rigs and the sensors.

    :param rigs_list: list of rigs definitions to merge
    :param rig_mappings: mapping of the rigs identifiers to their new identifiers
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged rigs definitions
    """
    assert len(rigs_list) > 0
    assert len(rigs_list) == len(rig_mappings)
    assert len(rigs_list) == len(sensor_mappings)

    merged_rigs = kapture.Rigs()
    for rigs, rig_mapping, sensor_mapping in zip(rigs_list, rig_mappings, sensor_mappings):
        if rigs is None:
            continue
        for rig_id, sensor_id in rigs.key_pairs():
            new_rig_id = rig_mapping[rig_id]
            new_sensor_id = sensor_mapping[sensor_id]
            merged_rigs[(new_rig_id, new_sensor_id)] = rigs[(rig_id, sensor_id)]
    return merged_rigs


def merge_trajectories(
        trajectories_list: List[Optional[kapture.Trajectories]],
        rig_mappings: List[Dict[str, str]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.Trajectories:
    """
    Merge several trajectories list into one list with new identifiers for the rigs and the sensors.

    :param trajectories_list: list of trajectories to merge
    :param rig_mappings: mapping of the rigs identifiers to their new identifiers
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged trajectories
    """
    assert len(trajectories_list) > 0
    assert len(trajectories_list) == len(rig_mappings)
    assert len(trajectories_list) == len(sensor_mappings)

    merged_trajectories = kapture.Trajectories()
    for trajectories, rig_mapping, sensor_mapping in zip(trajectories_list, rig_mappings, sensor_mappings):
        if trajectories is None:
            continue
        for timestamp, sensor_id, pose in kapture.flatten(trajectories):
            if sensor_id in rig_mapping:
                new_sensor_id = rig_mapping[sensor_id]
            else:
                new_sensor_id = sensor_mapping[sensor_id]
            merged_trajectories[(timestamp, new_sensor_id)] = pose
    return merged_trajectories


def merge_records_camera(
        records_camera_list: List[Optional[kapture.RecordsCamera]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.RecordsCamera:
    """
    Merge several camera records list into one list with new identifiers for the sensors.

    :param records_camera_list: list of camera records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged camera records
    """
    assert len(records_camera_list) > 0
    assert len(records_camera_list) == len(sensor_mappings)

    merged_records_camera = kapture.RecordsCamera()
    for records_camera, sensor_mapping in zip(records_camera_list, sensor_mappings):
        if records_camera is None:
            continue
        for timestamp, sensor_id, filename in kapture.flatten(records_camera):
            new_sensor_id = sensor_mapping[sensor_id]
            merged_records_camera[(timestamp, new_sensor_id)] = filename
    return merged_records_camera


def merge_records_lidar(
        records_lidar_list: List[Optional[kapture.RecordsLidar]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.RecordsLidar:
    """
    Merge several lidar records list into one list with new identifiers for the sensors.

    :param records_lidar_list: list of lidar records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged lidar records
    """
    assert len(records_lidar_list) > 0
    assert len(records_lidar_list) == len(sensor_mappings)

    merged_records_lidar = kapture.RecordsLidar()
    for records_lidar, sensor_mapping in zip(records_lidar_list, sensor_mappings):
        if records_lidar is None:
            continue
        for timestamp, sensor_id, filename in kapture.flatten(records_lidar):
            new_sensor_id = sensor_mapping[sensor_id]
            merged_records_lidar[(timestamp, new_sensor_id)] = filename
    return merged_records_lidar


def merge_records_wifi(
        records_wifi_list: List[Optional[kapture.RecordsWifi]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.RecordsWifi:
    """
    Merge several wifi records list into one list with new identifiers for the sensors.

    :param records_wifi_list: list of wifi records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged wifi records
    """
    assert len(records_wifi_list) > 0
    assert len(records_wifi_list) == len(sensor_mappings)

    merged_wifi_records = kapture.RecordsWifi()
    for wifi_records, sensor_mapping in zip(records_wifi_list, sensor_mappings):
        if wifi_records is None:
            continue
        for timestamp, sensor_id, bssid, record_wifi_signal in kapture.flatten(wifi_records):
            new_sensor_id = sensor_mapping[sensor_id]
            if (timestamp, new_sensor_id) not in merged_wifi_records:
                merged_wifi_records[timestamp, new_sensor_id] = kapture.RecordWifi()
            # if collision, keep first one.
            merged_wifi_records[timestamp, new_sensor_id].setdefault(bssid, record_wifi_signal)
    return merged_wifi_records


def merge_records_bluetooth(
        records_bluetooth_list: List[Optional[kapture.RecordsBluetooth]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.RecordsBluetooth:
    """
    Merge several bluetooth records list into one list with new identifiers for the sensors.

    :param records_bluetooth_list: list of wifi records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged bluetooth records
    """
    assert len(records_bluetooth_list) > 0
    assert len(records_bluetooth_list) == len(sensor_mappings)

    merged_bluetooth_records = kapture.RecordsBluetooth()
    for bluetooth_records, sensor_mapping in zip(records_bluetooth_list, sensor_mappings):
        if bluetooth_records is None:
            continue
        for timestamp, sensor_id, address, record_bluetooth_signal in kapture.flatten(bluetooth_records):
            new_sensor_id = sensor_mapping[sensor_id]
            if (timestamp, new_sensor_id) not in merged_bluetooth_records:
                merged_bluetooth_records[timestamp, new_sensor_id] = kapture.RecordBluetooth()
            # if collision, keep first one.
            merged_bluetooth_records[timestamp, new_sensor_id].setdefault(address, record_bluetooth_signal)
    return merged_bluetooth_records


def merge_records_generic(
        records_type,
        records_list,
        sensor_mappings: List[Dict[str, str]]):
    """
    Merge several records list into one list with new identifiers for the sensors.

    :param records_type: kapture class corresponding to the Records.
    :param records_list: list of records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged records
    """
    assert len(records_list) > 0
    assert len(records_list) == len(sensor_mappings)

    merged_records = records_type()
    for records, sensor_mapping in zip(records_list, sensor_mappings):
        if records is None:
            continue
        for timestamp, sensor_id, record in kapture.flatten(records):
            new_sensor_id = sensor_mapping[sensor_id]
            merged_records[timestamp, new_sensor_id] = record
    return merged_records


def merge_records_gnss(
        records_gnss_list: List[Optional[kapture.RecordsGnss]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.RecordsGnss:
    """
    Merge several gnss records list into one list with new identifiers for the sensors.

    :param records_gnss_list: list of gnss records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged gnss records
    """
    return merge_records_generic(
        kapture.RecordsGnss,
        records_gnss_list,
        sensor_mappings)


def merge_records_accelerometer(
        records_accelerometer_list: List[Optional[kapture.RecordsAccelerometer]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.RecordsAccelerometer:
    """
    Merge several accelerometer records list into one list with new identifiers for the sensors.

    :param records_accelerometer_list: list of accelerometer records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged accelerometer records
    """
    return merge_records_generic(
        kapture.RecordsAccelerometer,
        records_accelerometer_list,
        sensor_mappings)


def merge_records_gyroscope(
        records_gyroscope_list: List[Optional[kapture.RecordsGyroscope]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.RecordsGyroscope:
    """
    Merge several gyroscope records list into one list with new identifiers for the sensors.

    :param records_gyroscope_list: list of gyroscope records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged gyroscope records
    """
    return merge_records_generic(
        kapture.RecordsGyroscope,
        records_gyroscope_list,
        sensor_mappings)


def merge_records_magnetic(
        records_magnetic_list: List[Optional[kapture.RecordsMagnetic]],
        sensor_mappings: List[Dict[str, str]]) -> kapture.RecordsMagnetic:
    """
    Merge several magnetic records list into one list with new identifiers for the sensors.

    :param records_magnetic_list: list of magnetic records to merge
    :param sensor_mappings: mapping of the sensor identifiers to their new identifiers
    :return: merged magnetic records
    """
    return merge_records_generic(
        kapture.RecordsMagnetic,
        records_magnetic_list,
        sensor_mappings)


def merge_remap(kapture_list: List[kapture.Kapture],  # noqa: C901: function a bit long but not too complex
                skip_list: List[Type],
                data_paths: List[str],
                kapture_path: str,
                images_import_method: TransferAction) -> kapture.Kapture:
    """
    Merge multiple kapture while keeping ids (sensor_id) identical in merged and inputs.

    :param kapture_list: list of kapture to merge.
    :param skip_list: input optional types to not merge. sensors and rigs are unskippable
    :param data_paths: list of path to root path directory in same order as mentioned in kapture_list.
    :param kapture_path: directory root path to the merged kapture.
    :param images_import_method: method to transfer image files
    :return: merged kapture object
    """
    merged_kapture = kapture.Kapture()

    # find new sensor ids / rig ids
    sensors_mapping = []
    rigs_mapping = []
    _compute_new_ids(kapture_list, rigs_mapping, sensors_mapping)

    # concatenate all sensors with the remapped ids
    new_sensors = merge_sensors([a_kapture.sensors for a_kapture in kapture_list], sensors_mapping)
    # if merge_sensors returned an empty object, keep merged_kapture.sensors to None
    merged_kapture.sensors = get_new_if_not_empty(new_sensors, merged_kapture.sensors)

    # concatenate all rigs with the remapped ids
    new_rigs = merge_rigs([a_kapture.rigs for a_kapture in kapture_list], rigs_mapping, sensors_mapping)
    # if merge_rigs returned an empty object, keep merged_kapture.rigs to None
    merged_kapture.rigs = get_new_if_not_empty(new_rigs, merged_kapture.rigs)

    # all fields below can be skipped with skip_list
    # we do not assign the properties when the merge evaluate to false, we keep it as None
    if kapture.Trajectories not in skip_list:
        new_trajectories = merge_trajectories([a_kapture.trajectories for a_kapture in kapture_list],
                                              rigs_mapping,
                                              sensors_mapping)
        merged_kapture.trajectories = get_new_if_not_empty(new_trajectories, merged_kapture.trajectories)

    if kapture.RecordsCamera not in skip_list:
        new_records_camera = merge_records_camera([a_kapture.records_camera for a_kapture in kapture_list],
                                                  sensors_mapping)
        merged_kapture.records_camera = get_new_if_not_empty(new_records_camera, merged_kapture.records_camera)

        merge_records_data([[image_name
                             for _, _, image_name in kapture.flatten(every_kapture.records_camera)]
                            if every_kapture.records_camera is not None else []
                            for every_kapture in kapture_list],
                           [get_image_fullpath(data_path, image_filename=None) for data_path in data_paths],
                           kapture_path,
                           images_import_method)
    if kapture.RecordsLidar not in skip_list:
        new_records_lidar = merge_records_lidar([a_kapture.records_lidar for a_kapture in kapture_list],
                                                sensors_mapping)
        merged_kapture.records_lidar = get_new_if_not_empty(new_records_lidar, merged_kapture.records_lidar)
    if kapture.RecordsWifi not in skip_list:
        new_records_wifi = merge_records_wifi([a_kapture.records_wifi for a_kapture in kapture_list],
                                              sensors_mapping)
        merged_kapture.records_wifi = get_new_if_not_empty(new_records_wifi, merged_kapture.records_wifi)
    if kapture.RecordsBluetooth not in skip_list:
        new_records_bluetooth = merge_records_bluetooth([a_kapture.records_bluetooth for a_kapture in kapture_list],
                                                        sensors_mapping)
        merged_kapture.records_bluetooth = get_new_if_not_empty(new_records_bluetooth, merged_kapture.records_bluetooth)
    if kapture.RecordsGnss not in skip_list:
        new_records_gnss = merge_records_gnss([a_kapture.records_gnss for a_kapture in kapture_list],
                                              sensors_mapping)
        merged_kapture.records_gnss = get_new_if_not_empty(new_records_gnss,
                                                           merged_kapture.records_gnss)
    if kapture.RecordsAccelerometer not in skip_list:
        new_records_accelerometer = merge_records_accelerometer(
            [a_kapture.records_accelerometer for a_kapture in kapture_list],
            sensors_mapping)
        merged_kapture.records_accelerometer = get_new_if_not_empty(new_records_accelerometer,
                                                                    merged_kapture.records_accelerometer)
    if kapture.RecordsGyroscope not in skip_list:
        new_records_gyroscope = merge_records_gyroscope(
            [a_kapture.records_gyroscope for a_kapture in kapture_list],
            sensors_mapping)
        merged_kapture.records_gyroscope = get_new_if_not_empty(new_records_gyroscope,
                                                                merged_kapture.records_gyroscope)
    if kapture.RecordsMagnetic not in skip_list:
        new_records_magnetic = merge_records_magnetic(
            [a_kapture.records_magnetic for a_kapture in kapture_list],
            sensors_mapping)
        merged_kapture.records_magnetic = get_new_if_not_empty(new_records_magnetic,
                                                               merged_kapture.records_magnetic)

    # for the reconstruction, except points and observations, the files are copied with shutil.copy
    # if kapture_path evaluates to False, all copies will be skipped (but classes will be filled normally)
    if kapture.Keypoints not in skip_list:
        keypoints = [a_kapture.keypoints for a_kapture in kapture_list]
        keypoints_not_none = [k for k in keypoints if k is not None]
        if len(keypoints_not_none) > 0:
            new_keypoints = merge_keypoints(keypoints, data_paths, kapture_path)
            merged_kapture.keypoints = get_new_if_not_empty(new_keypoints, merged_kapture.keypoints)
    if kapture.Descriptors not in skip_list:
        descriptors = [a_kapture.descriptors for a_kapture in kapture_list]
        descriptors_not_none = [k for k in descriptors if k is not None]
        if len(descriptors_not_none) > 0:
            new_descriptors = merge_descriptors(descriptors, data_paths, kapture_path)
            merged_kapture.descriptors = get_new_if_not_empty(new_descriptors, merged_kapture.descriptors)
    if kapture.GlobalFeatures not in skip_list:
        global_features = [a_kapture.global_features for a_kapture in kapture_list]
        global_features_not_none = [k for k in global_features if k is not None]
        if len(global_features_not_none) > 0:
            new_global_features = merge_global_features(global_features, data_paths, kapture_path)
            merged_kapture.global_features = get_new_if_not_empty(new_global_features, merged_kapture.global_features)
    if kapture.Matches not in skip_list:
        matches = [a_kapture.matches for a_kapture in kapture_list]
        new_matches = merge_matches(matches, data_paths, kapture_path)
        merged_kapture.matches = get_new_if_not_empty(new_matches, merged_kapture.matches)

    if kapture.Points3d not in skip_list and kapture.Observations not in skip_list:
        points_and_obs = [(a_kapture.points3d, a_kapture.observations) for a_kapture in kapture_list]
        new_points, new_observations = merge_points3d_and_observations(points_and_obs)
        merged_kapture.points3d = get_new_if_not_empty(new_points, merged_kapture.points3d)
        merged_kapture.observations = get_new_if_not_empty(new_observations, merged_kapture.observations)
    elif kapture.Points3d not in skip_list:
        points = [a_kapture.points3d for a_kapture in kapture_list]
        new_points = merge_points3d(points)
        merged_kapture.points3d = get_new_if_not_empty(new_points, merged_kapture.points3d)
    return merged_kapture


def _compute_new_ids(kapture_list, rigs_mapping, sensors_mapping):
    sensor_offset = 0
    rigs_offset = 0
    for every_kapture in kapture_list:
        if every_kapture.sensors is not None:
            sensors_mapping.append(get_sensors_mapping(every_kapture.sensors, sensor_offset))
            sensor_offset += len(every_kapture.sensors)
        else:
            sensors_mapping.append({})

        if every_kapture.rigs is not None:
            rigs_mapping.append(get_rigs_mapping(every_kapture.rigs, rigs_offset))
            rigs_offset += len(every_kapture.rigs)
        else:
            rigs_mapping.append({})
