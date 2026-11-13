# Config overrides

Every Autoware service applies the files here on top of Autoware's own on each
start. Put a file at `<package>/<path in its share directory>` with only the
keys you change, for example
`autoware_launch/config/planning/scenario_planning/common/common.param.yaml`.
