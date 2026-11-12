# {{name}}

A kit on top of `{{base}}` from Open AD Kit {{version}}.

| File | What it holds |
| --- | --- |
| `openadkit.json` | The release it extends and the extra images it pins (`externalImages`) |
| `deployment.json` | Its base deployment and, optionally, its Compose files (default `compose.yaml`), narrower `requirements` and own `verify` step |
| `settings.env` | Values that differ from the base |
| `compose.yaml` | Includes the base; add your services here |
| `config/autoware/` | Parameter overrides: `<package>/<path in its share directory>`, with only the keys you change |
| `overlay_ws/src/` | Your ROS packages |

```bash
openadkit build                  # build overlay_ws in the matching devel image
openadkit validate
openadkit run --verify           # start, wait until ready, run the base's verify step
openadkit stop
```

See the [Kit Guide](https://autowarefoundation.github.io/openadkit/kits/kit-guide/)
for every extension point and how to upgrade.
