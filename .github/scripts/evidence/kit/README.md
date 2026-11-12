# Example kit fixture

What CI puts on top of `openadkit new example-kit` (validation_matrix.py
`make_example_kits`) to exercise every kit extension point against a build:
a setting in `settings.env`, a parameter override in `config/autoware/`, a C++
package and the kit's own vehicle and sensor kit packages in `overlay_ws/`, a pinned external image (`external-images.json`,
merged into the kit's `openadkit.json`), and services with a healthcheck in
`docker-compose.yaml`. The kit runs Planning Simulation's verify step, then
`checks/dev_loop.sh`: it changes the C++ package, builds it, restarts and sees
the change (evidence level L3).
