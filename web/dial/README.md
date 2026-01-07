# Rotatable Dial

A tool that displays a rotatable dial visualization at a specified angle.

## Usage

Access via URL parameter: `?angle=X` where X is between -90 and +90 degrees.

Example: `?angle=45` or `?angle=-30`

## Implementation

The main index.html acts as a router that redirects to pre-generated dial HTML files in the `dials/` subdirectory based on the angle parameter.

## Purpose

Useful for displaying dial/gauge visualizations at specific angles, potentially for dashboards, demonstrations, or embedded displays.
