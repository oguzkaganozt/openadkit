// Docker Bake configuration for OpenADKit base images
// These are the foundation images used by all other component Dockerfiles

group "default" {
  targets = [
    "base",
    "base-cuda"
  ]
}

// For docker/metadata-action
target "docker-metadata-action-base" {}
target "docker-metadata-action-base-cuda" {}

target "base" {
  inherits = ["docker-metadata-action-base"]
  dockerfile = "components/devel/Dockerfile.devel"
  target = "base"
}

target "base-cuda" {
  inherits = ["docker-metadata-action-base-cuda"]
  dockerfile = "components/devel/Dockerfile.devel"
  target = "base-cuda"
}
