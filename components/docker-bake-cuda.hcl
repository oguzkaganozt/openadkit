// Docker Bake configuration for OpenADKit CUDA component images
// This file defines build targets for CUDA runtime images only (no devel images)

group "default" {
  targets = [
    "universe-common-devel-cuda",
    "universe-sensing-perception-cuda",
    "universe-cuda"
  ]
}

// For docker/metadata-action
target "docker-metadata-action-universe-common-devel-cuda" {}
target "docker-metadata-action-universe-sensing-perception-cuda" {}
target "docker-metadata-action-universe-cuda" {}

// =============================================================================
// Intermediate build images (CUDA)
// =============================================================================

target "universe-common-devel-cuda" {
  inherits = ["docker-metadata-action-universe-common-devel-cuda"]
  dockerfile = "components/autoware-base/Dockerfile"
  target = "universe-common-devel-cuda"
}

// =============================================================================
// Runtime images (CUDA)
// =============================================================================

target "universe-sensing-perception-cuda" {
  inherits = ["docker-metadata-action-universe-sensing-perception-cuda"]
  dockerfile = "components/autoware-sensing-perception/Dockerfile"
  target = "universe-sensing-perception-cuda"
}

target "universe-cuda" {
  inherits = ["docker-metadata-action-universe-cuda"]
  dockerfile = "components/autoware-universe/Dockerfile"
  target = "universe-cuda"
}
