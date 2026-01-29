// Docker Bake configuration for OpenADKit component images
// This file defines build targets for runtime images only (no devel images)

group "default" {
  targets = [
    "rosdep-depend",
    "core-devel",
    "autoware-common-devel",
    "autoware-sensing-perception",
    "autoware-localization-mapping",
    "autoware-planning-control",
    "autoware-vehicle-system",
    "autoware-visualization",
    "autoware-api",
    "autoware-universe"
  ]
}

// Intermediate images group (build dependencies)
group "intermediate" {
  targets = [
    "rosdep-depend",
    "core-devel",
    "autoware-common-devel"
  ]
}

// Runtime images group (final products)
group "runtime" {
  targets = [
    "autoware-sensing-perception",
    "autoware-localization-mapping",
    "autoware-planning-control",
    "autoware-vehicle-system",
    "autoware-visualization",
    "autoware-api",
    "autoware-universe"
  ]
}

// For docker/metadata-action
target "docker-metadata-action-rosdep-depend" {}
target "docker-metadata-action-core-devel" {}
target "docker-metadata-action-autoware-common-devel" {}
target "docker-metadata-action-autoware-sensing-perception" {}
target "docker-metadata-action-autoware-localization-mapping" {}
target "docker-metadata-action-autoware-planning-control" {}
target "docker-metadata-action-autoware-vehicle-system" {}
target "docker-metadata-action-autoware-visualization" {}
target "docker-metadata-action-autoware-api" {}
target "docker-metadata-action-autoware-universe" {}

// =============================================================================
// Intermediate build images
// =============================================================================

target "rosdep-depend" {
  inherits = ["docker-metadata-action-rosdep-depend"]
  dockerfile = "components/autoware-base/Dockerfile"
  target = "rosdep-depend"
}

target "core-devel" {
  inherits = ["docker-metadata-action-core-devel"]
  dockerfile = "components/autoware-base/Dockerfile"
  target = "core-devel"
}

target "autoware-common-devel" {
  inherits = ["docker-metadata-action-autoware-common-devel"]
  dockerfile = "components/autoware-base/Dockerfile"
  target = "autoware-common-devel"
}

// =============================================================================
// Runtime images
// =============================================================================

target "autoware-sensing-perception" {
  inherits = ["docker-metadata-action-autoware-sensing-perception"]
  dockerfile = "components/autoware-sensing-perception/Dockerfile"
  target = "autoware-sensing-perception"
}

target "autoware-localization-mapping" {
  inherits = ["docker-metadata-action-autoware-localization-mapping"]
  dockerfile = "components/autoware-localization-mapping/Dockerfile"
  target = "autoware-localization-mapping"
}

target "autoware-planning-control" {
  inherits = ["docker-metadata-action-autoware-planning-control"]
  dockerfile = "components/autoware-planning-control/Dockerfile"
  target = "autoware-planning-control"
}

target "autoware-vehicle-system" {
  inherits = ["docker-metadata-action-autoware-vehicle-system"]
  dockerfile = "components/autoware-vehicle-system/Dockerfile"
  target = "autoware-vehicle-system"
}

target "autoware-visualization" {
  inherits = ["docker-metadata-action-autoware-visualization"]
  dockerfile = "components/autoware-base/Dockerfile"
  target = "autoware-visualization"
}

target "autoware-api" {
  inherits = ["docker-metadata-action-autoware-api"]
  dockerfile = "components/autoware-api/Dockerfile"
  target = "autoware-api"
}

target "autoware-universe" {
  inherits = ["docker-metadata-action-autoware-universe"]
  dockerfile = "components/autoware-universe/Dockerfile"
  target = "autoware-universe"
}
