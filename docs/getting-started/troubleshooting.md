# Troubleshooting

This page covers common issues and solutions when working with Open AD Kit.

## Docker Issues

### Container fails to start
- Verify Docker Engine is running: `docker info`
- Check that required ports are not already in use
- Ensure the `.env` file exists and is correctly configured

### Permission denied
- Make sure your user is in the `docker` group, or use `sudo`
- Check file permissions on mounted volumes

## GPU Issues

### NVIDIA Container Toolkit not detected
- Verify installation: `nvidia-ctk --version`
- Restart Docker: `sudo systemctl restart docker`
- Check GPU availability: `nvidia-smi`

## Deployment Issues

### Visualizer shows blank screen
- Wait 10–30 seconds for containers to fully initialize
- Check container logs: `docker compose logs -f`
- Verify all required map files are present

## Getting Help

- [GitHub Issues](https://github.com/autowarefoundation/openadkit/issues)
- [Autoware Foundation Discord](https://discord.gg/Q94UsPvReQ)
