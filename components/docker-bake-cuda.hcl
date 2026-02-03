// Docker Bake configuration for OpenADKit CUDA component images
// This file defines build targets for CUDA runtime images only (no devel images)

group "default" {
  targets = [
    "autoware-common-devel-cuda",
    "autoware-sensing-perception-cuda",
    "autoware-cuda"
  ]
}

// For docker/metadata-action
target "docker-metadata-action-autoware-common-devel-cuda" {}
target "docker-metadata-action-autoware-sensing-perception-cuda" {}
target "docker-metadata-action-autoware-cuda" {}

// =============================================================================
// Intermediate build images (CUDA)
// =============================================================================

target "autoware-common-devel-cuda" {
  inherits = ["docker-metadata-action-autoware-common-devel-cuda"]
  dockerfile = "components/autoware-base/Dockerfile"
  target = "autoware-common-devel-cuda"
}

// =============================================================================
// Runtime images (CUDA)
// =============================================================================

target "autoware-sensing-perception-cuda" {
  inherits = ["docker-metadata-action-autoware-sensing-perception-cuda"]
  dockerfile = "components/autoware-sensing-perception/Dockerfile"
  target = "autoware-sensing-perception-cuda"
}

target "autoware-cuda" {
  inherits = ["docker-metadata-action-autoware-cuda"]
  dockerfile = "components/autoware-universe/Dockerfile"
  target = "autoware-cuda"
}
