# Data Directory

This directory is used for persistent data when running Windows-MCP in Docker.

## Purpose

- Store configuration files
- Cache data
- Logs (if configured)
- Temporary files

## Docker Volume Mapping

When running the Docker container, this directory is mapped to `/app/data` inside the container.

## Files

- `.gitkeep` - Keeps this directory in git (empty directories are ignored)

## Usage

The application will create necessary subdirectories and files as needed.
