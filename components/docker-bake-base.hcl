// Docker Bake configuration for OpenADKit base images
// These are the foundation images used by all other component Dockerfiles

group "default" {
  targets = [
    "autoware-base",
    "autoware-base-cuda"
  ]
}

// For docker/metadata-action
target "docker-metadata-action-autoware-base" {}
target "docker-metadata-action-autoware-base-cuda" {}

target "autoware-base" {
  inherits = ["docker-metadata-action-autoware-base"]
  dockerfile = "components/autoware-base/Dockerfile"
  target = "base"
}

target "autoware-base-cuda" {
  inherits = ["docker-metadata-action-autoware-base-cuda"]
  dockerfile = "components/autoware-base/Dockerfile"
  target = "base-cuda"
}
