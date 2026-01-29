// Docker Bake configuration for OpenADKit component images
// This file defines build targets for runtime images only (no devel images)

group "default" {
  targets = [
    "rosdep-depend",
    "core-devel",
    "universe-common-devel",
    "universe-sensing-perception",
    "universe-localization-mapping",
    "universe-planning-control",
    "universe-vehicle-system",
    "universe-visualization",
    "universe-api",
    "universe"
  ]
}

// Intermediate images group (build dependencies)
group "intermediate" {
  targets = [
    "rosdep-depend",
    "core-devel",
    "universe-common-devel"
  ]
}

// Runtime images group (final products)
group "runtime" {
  targets = [
    "universe-sensing-perception",
    "universe-localization-mapping",
    "universe-planning-control",
    "universe-vehicle-system",
    "universe-visualization",
    "universe-api",
    "universe"
  ]
}

// For docker/metadata-action
target "docker-metadata-action-rosdep-depend" {}
target "docker-metadata-action-core-devel" {}
target "docker-metadata-action-universe-common-devel" {}
target "docker-metadata-action-universe-sensing-perception" {}
target "docker-metadata-action-universe-localization-mapping" {}
target "docker-metadata-action-universe-planning-control" {}
target "docker-metadata-action-universe-vehicle-system" {}
target "docker-metadata-action-universe-visualization" {}
target "docker-metadata-action-universe-api" {}
target "docker-metadata-action-universe" {}

// =============================================================================
// Intermediate build images
// =============================================================================

target "rosdep-depend" {
  inherits = ["docker-metadata-action-rosdep-depend"]
  dockerfile = "components/devel/Dockerfile.devel"
  target = "rosdep-depend"
}

target "core-devel" {
  inherits = ["docker-metadata-action-core-devel"]
  dockerfile = "components/devel/Dockerfile.devel"
  target = "core-devel"
}

target "universe-common-devel" {
  inherits = ["docker-metadata-action-universe-common-devel"]
  dockerfile = "components/devel/Dockerfile.devel"
  target = "universe-common-devel"
}

// =============================================================================
// Runtime images
// =============================================================================

target "universe-sensing-perception" {
  inherits = ["docker-metadata-action-universe-sensing-perception"]
  dockerfile = "components/sensing-perception/Dockerfile.sensing-perception"
  target = "universe-sensing-perception"
}

target "universe-localization-mapping" {
  inherits = ["docker-metadata-action-universe-localization-mapping"]
  dockerfile = "components/localization-mapping/Dockerfile.localization-mapping"
  target = "universe-localization-mapping"
}

target "universe-planning-control" {
  inherits = ["docker-metadata-action-universe-planning-control"]
  dockerfile = "components/planning-control/Dockerfile.planning-control"
  target = "universe-planning-control"
}

target "universe-vehicle-system" {
  inherits = ["docker-metadata-action-universe-vehicle-system"]
  dockerfile = "components/vehicle-system/Dockerfile.vehicle-system"
  target = "universe-vehicle-system"
}

target "universe-visualization" {
  inherits = ["docker-metadata-action-universe-visualization"]
  dockerfile = "components/devel/Dockerfile.devel"
  target = "universe-visualization"
}

target "universe-api" {
  inherits = ["docker-metadata-action-universe-api"]
  dockerfile = "components/api/Dockerfile.api"
  target = "universe-api"
}

target "universe" {
  inherits = ["docker-metadata-action-universe"]
  dockerfile = "components/universe/Dockerfile.universe"
  target = "universe"
}
