# Retired schema aliases

S6 found byte-identical JSON Schema and Protobuf copies outside the versioned
source tree, plus generated Python wrappers under authored schema directories.
They are preserved here only for migration review.

Canonical authored contracts live in `schemas/v1/`; generated bindings live in
`shared/generated/`. Nothing in this directory is a supported import or build
input.
