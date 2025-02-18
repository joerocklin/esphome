import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components import climate, sensor
from esphome.const import (
    CONF_AUTO_MODE,
    CONF_AWAY_CONFIG,
    CONF_COOL_ACTION,
    CONF_COOL_DEADBAND,
    CONF_COOL_MODE,
    CONF_COOL_OVERRUN,
    CONF_DEFAULT_MODE,
    CONF_DEFAULT_TARGET_TEMPERATURE_HIGH,
    CONF_DEFAULT_TARGET_TEMPERATURE_LOW,
    CONF_DRY_ACTION,
    CONF_DRY_MODE,
    CONF_FAN_MODE_ON_ACTION,
    CONF_FAN_MODE_OFF_ACTION,
    CONF_FAN_MODE_AUTO_ACTION,
    CONF_FAN_MODE_LOW_ACTION,
    CONF_FAN_MODE_MEDIUM_ACTION,
    CONF_FAN_MODE_HIGH_ACTION,
    CONF_FAN_MODE_MIDDLE_ACTION,
    CONF_FAN_MODE_FOCUS_ACTION,
    CONF_FAN_MODE_DIFFUSE_ACTION,
    CONF_FAN_ONLY_ACTION,
    CONF_FAN_ONLY_COOLING,
    CONF_FAN_ONLY_MODE,
    CONF_HEAT_ACTION,
    CONF_HEAT_DEADBAND,
    CONF_HEAT_MODE,
    CONF_HEAT_OVERRUN,
    CONF_HYSTERESIS,
    CONF_ID,
    CONF_IDLE_ACTION,
    CONF_OFF_MODE,
    CONF_SENSOR,
    CONF_SET_POINT_MINIMUM_DIFFERENTIAL,
    CONF_SWING_BOTH_ACTION,
    CONF_SWING_HORIZONTAL_ACTION,
    CONF_SWING_OFF_ACTION,
    CONF_SWING_VERTICAL_ACTION,
    CONF_TARGET_TEMPERATURE_CHANGE_ACTION,
)

CODEOWNERS = ["@kbx81"]

climate_ns = cg.esphome_ns.namespace("climate")
thermostat_ns = cg.esphome_ns.namespace("thermostat")
ThermostatClimate = thermostat_ns.class_(
    "ThermostatClimate", climate.Climate, cg.Component
)
ThermostatClimateTargetTempConfig = thermostat_ns.struct(
    "ThermostatClimateTargetTempConfig"
)
ClimateMode = climate_ns.enum("ClimateMode")
CLIMATE_MODES = {
    "OFF": ClimateMode.CLIMATE_MODE_OFF,
    "HEAT_COOL": ClimateMode.CLIMATE_MODE_HEAT_COOL,
    "COOL": ClimateMode.CLIMATE_MODE_COOL,
    "HEAT": ClimateMode.CLIMATE_MODE_HEAT,
    "DRY": ClimateMode.CLIMATE_MODE_DRY,
    "FAN_ONLY": ClimateMode.CLIMATE_MODE_FAN_ONLY,
    "AUTO": ClimateMode.CLIMATE_MODE_AUTO,
}
validate_climate_mode = cv.enum(CLIMATE_MODES, upper=True)


def validate_thermostat(config):
    # verify corresponding climate action action exists for any defined climate mode action
    requirements = {
        CONF_AUTO_MODE: [CONF_COOL_ACTION, CONF_HEAT_ACTION],
        CONF_COOL_MODE: [CONF_COOL_ACTION],
        CONF_DRY_MODE: [CONF_DRY_ACTION],
        CONF_FAN_ONLY_MODE: [CONF_FAN_ONLY_ACTION],
        CONF_HEAT_MODE: [CONF_HEAT_ACTION],
    }
    for config_mode, req_actions in requirements.items():
        for req_action in req_actions:
            if config_mode in config and req_action not in config:
                raise cv.Invalid(f"{req_action} must be defined to use {config_mode}")

    # determine validation requirements based on fan_only_cooling setting
    if config[CONF_FAN_ONLY_COOLING] is True:
        requirements = {
            CONF_DEFAULT_TARGET_TEMPERATURE_HIGH: [
                CONF_COOL_ACTION,
                CONF_FAN_ONLY_ACTION,
            ],
            CONF_DEFAULT_TARGET_TEMPERATURE_LOW: [CONF_HEAT_ACTION],
        }
    else:
        requirements = {
            CONF_DEFAULT_TARGET_TEMPERATURE_HIGH: [CONF_COOL_ACTION],
            CONF_DEFAULT_TARGET_TEMPERATURE_LOW: [CONF_HEAT_ACTION],
        }

    for config_temp, req_actions in requirements.items():
        for req_action in req_actions:
            # verify corresponding default target temperature exists when a given climate action exists
            if config_temp not in config and req_action in config:
                raise cv.Invalid(
                    f"{config_temp} must be defined when using {req_action}"
                )
            # if a given climate action is NOT defined, it should not have a default target temperature
            if config_temp in config and req_action not in config:
                raise cv.Invalid(f"{config_temp} is defined with no {req_action}")

    if CONF_AWAY_CONFIG in config:
        away = config[CONF_AWAY_CONFIG]
        for config_temp, req_actions in requirements.items():
            for req_action in req_actions:
                # verify corresponding default target temperature exists when a given climate action exists
                if config_temp not in away and req_action in config:
                    raise cv.Invalid(
                        f"{config_temp} must be defined in away configuration when using {req_action}"
                    )
                # if a given climate action is NOT defined, it should not have a default target temperature
                if config_temp in away and req_action not in config:
                    raise cv.Invalid(
                        f"{config_temp} is defined in away configuration with no {req_action}"
                    )

    # verify default climate mode is valid given above configuration
    default_mode = config[CONF_DEFAULT_MODE]
    requirements = {
        "HEAT_COOL": [CONF_COOL_ACTION, CONF_HEAT_ACTION],
        "COOL": [CONF_COOL_ACTION],
        "HEAT": [CONF_HEAT_ACTION],
        "DRY": [CONF_DRY_ACTION],
        "FAN_ONLY": [CONF_FAN_ONLY_ACTION],
        "AUTO": [CONF_COOL_ACTION, CONF_HEAT_ACTION],
    }.get(default_mode, [])
    for req in requirements:
        if req not in config:
            raise cv.Invalid(
                f"{CONF_DEFAULT_MODE} is set to {default_mode} but {req} is not present in the configuration"
            )

    return config


CONFIG_SCHEMA = cv.All(
    climate.CLIMATE_SCHEMA.extend(
        {
            cv.GenerateID(): cv.declare_id(ThermostatClimate),
            cv.Required(CONF_SENSOR): cv.use_id(sensor.Sensor),
            cv.Required(CONF_IDLE_ACTION): automation.validate_automation(single=True),
            cv.Optional(CONF_COOL_ACTION): automation.validate_automation(single=True),
            cv.Optional(CONF_DRY_ACTION): automation.validate_automation(single=True),
            cv.Optional(CONF_FAN_ONLY_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_HEAT_ACTION): automation.validate_automation(single=True),
            cv.Optional(CONF_AUTO_MODE): automation.validate_automation(single=True),
            cv.Optional(CONF_COOL_MODE): automation.validate_automation(single=True),
            cv.Optional(CONF_DRY_MODE): automation.validate_automation(single=True),
            cv.Optional(CONF_FAN_ONLY_MODE): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_HEAT_MODE): automation.validate_automation(single=True),
            cv.Optional(CONF_OFF_MODE): automation.validate_automation(single=True),
            cv.Optional(CONF_FAN_MODE_ON_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_FAN_MODE_OFF_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_FAN_MODE_AUTO_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_FAN_MODE_LOW_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_FAN_MODE_MEDIUM_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_FAN_MODE_HIGH_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_FAN_MODE_MIDDLE_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_FAN_MODE_FOCUS_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_FAN_MODE_DIFFUSE_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_SWING_BOTH_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_SWING_HORIZONTAL_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_SWING_OFF_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_SWING_VERTICAL_ACTION): automation.validate_automation(
                single=True
            ),
            cv.Optional(
                CONF_TARGET_TEMPERATURE_CHANGE_ACTION
            ): automation.validate_automation(single=True),
            cv.Optional(CONF_DEFAULT_MODE, default="OFF"): cv.templatable(
                validate_climate_mode
            ),
            cv.Optional(CONF_DEFAULT_TARGET_TEMPERATURE_HIGH): cv.temperature,
            cv.Optional(CONF_DEFAULT_TARGET_TEMPERATURE_LOW): cv.temperature,
            cv.Optional(
                CONF_SET_POINT_MINIMUM_DIFFERENTIAL, default=0.5
            ): cv.temperature,
            cv.Optional(CONF_COOL_DEADBAND): cv.temperature,
            cv.Optional(CONF_COOL_OVERRUN): cv.temperature,
            cv.Optional(CONF_HEAT_DEADBAND): cv.temperature,
            cv.Optional(CONF_HEAT_OVERRUN): cv.temperature,
            cv.Optional(CONF_HYSTERESIS, default=0.5): cv.temperature,
            cv.Optional(CONF_FAN_ONLY_COOLING, default=False): cv.boolean,
            cv.Optional(CONF_AWAY_CONFIG): cv.Schema(
                {
                    cv.Optional(CONF_DEFAULT_TARGET_TEMPERATURE_HIGH): cv.temperature,
                    cv.Optional(CONF_DEFAULT_TARGET_TEMPERATURE_LOW): cv.temperature,
                }
            ),
        }
    ).extend(cv.COMPONENT_SCHEMA),
    cv.has_at_least_one_key(
        CONF_COOL_ACTION, CONF_DRY_ACTION, CONF_FAN_ONLY_ACTION, CONF_HEAT_ACTION
    ),
    validate_thermostat,
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await climate.register_climate(var, config)

    heat_cool_mode_available = CONF_HEAT_ACTION in config and CONF_COOL_ACTION in config
    two_points_available = CONF_HEAT_ACTION in config and (
        CONF_COOL_ACTION in config or CONF_FAN_ONLY_ACTION in config
    )

    sens = await cg.get_variable(config[CONF_SENSOR])
    cg.add(var.set_default_mode(config[CONF_DEFAULT_MODE]))
    cg.add(
        var.set_set_point_minimum_differential(
            config[CONF_SET_POINT_MINIMUM_DIFFERENTIAL]
        )
    )
    cg.add(var.set_sensor(sens))

    if CONF_COOL_DEADBAND in config:
        cg.add(var.set_cool_deadband(config[CONF_COOL_DEADBAND]))
    else:
        cg.add(var.set_cool_deadband(config[CONF_HYSTERESIS]))

    if CONF_COOL_OVERRUN in config:
        cg.add(var.set_cool_overrun(config[CONF_COOL_OVERRUN]))
    else:
        cg.add(var.set_cool_overrun(config[CONF_HYSTERESIS]))

    if CONF_HEAT_DEADBAND in config:
        cg.add(var.set_heat_deadband(config[CONF_HEAT_DEADBAND]))
    else:
        cg.add(var.set_heat_deadband(config[CONF_HYSTERESIS]))

    if CONF_HEAT_OVERRUN in config:
        cg.add(var.set_heat_overrun(config[CONF_HEAT_OVERRUN]))
    else:
        cg.add(var.set_heat_overrun(config[CONF_HYSTERESIS]))

    if two_points_available is True:
        cg.add(var.set_supports_two_points(True))
        normal_config = ThermostatClimateTargetTempConfig(
            config[CONF_DEFAULT_TARGET_TEMPERATURE_LOW],
            config[CONF_DEFAULT_TARGET_TEMPERATURE_HIGH],
        )
    elif CONF_DEFAULT_TARGET_TEMPERATURE_HIGH in config:
        cg.add(var.set_supports_two_points(False))
        normal_config = ThermostatClimateTargetTempConfig(
            config[CONF_DEFAULT_TARGET_TEMPERATURE_HIGH]
        )
    elif CONF_DEFAULT_TARGET_TEMPERATURE_LOW in config:
        cg.add(var.set_supports_two_points(False))
        normal_config = ThermostatClimateTargetTempConfig(
            config[CONF_DEFAULT_TARGET_TEMPERATURE_LOW]
        )
    cg.add(var.set_supports_fan_only_cooling(config[CONF_FAN_ONLY_COOLING]))
    cg.add(var.set_normal_config(normal_config))

    await automation.build_automation(
        var.get_idle_action_trigger(), [], config[CONF_IDLE_ACTION]
    )

    if heat_cool_mode_available is True:
        cg.add(var.set_supports_heat_cool(True))
    else:
        cg.add(var.set_supports_heat_cool(False))

    if CONF_COOL_ACTION in config:
        await automation.build_automation(
            var.get_cool_action_trigger(), [], config[CONF_COOL_ACTION]
        )
        cg.add(var.set_supports_cool(True))
    if CONF_DRY_ACTION in config:
        await automation.build_automation(
            var.get_dry_action_trigger(), [], config[CONF_DRY_ACTION]
        )
        cg.add(var.set_supports_dry(True))
    if CONF_FAN_ONLY_ACTION in config:
        await automation.build_automation(
            var.get_fan_only_action_trigger(), [], config[CONF_FAN_ONLY_ACTION]
        )
        cg.add(var.set_supports_fan_only(True))
    if CONF_HEAT_ACTION in config:
        await automation.build_automation(
            var.get_heat_action_trigger(), [], config[CONF_HEAT_ACTION]
        )
        cg.add(var.set_supports_heat(True))
    if CONF_AUTO_MODE in config:
        await automation.build_automation(
            var.get_auto_mode_trigger(), [], config[CONF_AUTO_MODE]
        )
    if CONF_COOL_MODE in config:
        await automation.build_automation(
            var.get_cool_mode_trigger(), [], config[CONF_COOL_MODE]
        )
        cg.add(var.set_supports_cool(True))
    if CONF_DRY_MODE in config:
        await automation.build_automation(
            var.get_dry_mode_trigger(), [], config[CONF_DRY_MODE]
        )
        cg.add(var.set_supports_dry(True))
    if CONF_FAN_ONLY_MODE in config:
        await automation.build_automation(
            var.get_fan_only_mode_trigger(), [], config[CONF_FAN_ONLY_MODE]
        )
        cg.add(var.set_supports_fan_only(True))
    if CONF_HEAT_MODE in config:
        await automation.build_automation(
            var.get_heat_mode_trigger(), [], config[CONF_HEAT_MODE]
        )
        cg.add(var.set_supports_heat(True))
    if CONF_OFF_MODE in config:
        await automation.build_automation(
            var.get_off_mode_trigger(), [], config[CONF_OFF_MODE]
        )
    if CONF_FAN_MODE_ON_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_on_trigger(), [], config[CONF_FAN_MODE_ON_ACTION]
        )
        cg.add(var.set_supports_fan_mode_on(True))
    if CONF_FAN_MODE_OFF_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_off_trigger(), [], config[CONF_FAN_MODE_OFF_ACTION]
        )
        cg.add(var.set_supports_fan_mode_off(True))
    if CONF_FAN_MODE_AUTO_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_auto_trigger(), [], config[CONF_FAN_MODE_AUTO_ACTION]
        )
        cg.add(var.set_supports_fan_mode_auto(True))
    if CONF_FAN_MODE_LOW_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_low_trigger(), [], config[CONF_FAN_MODE_LOW_ACTION]
        )
        cg.add(var.set_supports_fan_mode_low(True))
    if CONF_FAN_MODE_MEDIUM_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_medium_trigger(), [], config[CONF_FAN_MODE_MEDIUM_ACTION]
        )
        cg.add(var.set_supports_fan_mode_medium(True))
    if CONF_FAN_MODE_HIGH_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_high_trigger(), [], config[CONF_FAN_MODE_HIGH_ACTION]
        )
        cg.add(var.set_supports_fan_mode_high(True))
    if CONF_FAN_MODE_MIDDLE_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_middle_trigger(), [], config[CONF_FAN_MODE_MIDDLE_ACTION]
        )
        cg.add(var.set_supports_fan_mode_middle(True))
    if CONF_FAN_MODE_FOCUS_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_focus_trigger(), [], config[CONF_FAN_MODE_FOCUS_ACTION]
        )
        cg.add(var.set_supports_fan_mode_focus(True))
    if CONF_FAN_MODE_DIFFUSE_ACTION in config:
        await automation.build_automation(
            var.get_fan_mode_diffuse_trigger(), [], config[CONF_FAN_MODE_DIFFUSE_ACTION]
        )
        cg.add(var.set_supports_fan_mode_diffuse(True))
    if CONF_SWING_BOTH_ACTION in config:
        await automation.build_automation(
            var.get_swing_mode_both_trigger(), [], config[CONF_SWING_BOTH_ACTION]
        )
        cg.add(var.set_supports_swing_mode_both(True))
    if CONF_SWING_HORIZONTAL_ACTION in config:
        await automation.build_automation(
            var.get_swing_mode_horizontal_trigger(),
            [],
            config[CONF_SWING_HORIZONTAL_ACTION],
        )
        cg.add(var.set_supports_swing_mode_horizontal(True))
    if CONF_SWING_OFF_ACTION in config:
        await automation.build_automation(
            var.get_swing_mode_off_trigger(), [], config[CONF_SWING_OFF_ACTION]
        )
        cg.add(var.set_supports_swing_mode_off(True))
    if CONF_SWING_VERTICAL_ACTION in config:
        await automation.build_automation(
            var.get_swing_mode_vertical_trigger(),
            [],
            config[CONF_SWING_VERTICAL_ACTION],
        )
        cg.add(var.set_supports_swing_mode_vertical(True))
    if CONF_TARGET_TEMPERATURE_CHANGE_ACTION in config:
        await automation.build_automation(
            var.get_temperature_change_trigger(),
            [],
            config[CONF_TARGET_TEMPERATURE_CHANGE_ACTION],
        )

    if CONF_AWAY_CONFIG in config:
        away = config[CONF_AWAY_CONFIG]

        if two_points_available is True:
            away_config = ThermostatClimateTargetTempConfig(
                away[CONF_DEFAULT_TARGET_TEMPERATURE_LOW],
                away[CONF_DEFAULT_TARGET_TEMPERATURE_HIGH],
            )
        elif CONF_DEFAULT_TARGET_TEMPERATURE_HIGH in away:
            away_config = ThermostatClimateTargetTempConfig(
                away[CONF_DEFAULT_TARGET_TEMPERATURE_HIGH]
            )
        elif CONF_DEFAULT_TARGET_TEMPERATURE_LOW in away:
            away_config = ThermostatClimateTargetTempConfig(
                away[CONF_DEFAULT_TARGET_TEMPERATURE_LOW]
            )
        cg.add(var.set_away_config(away_config))
