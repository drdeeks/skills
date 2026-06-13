# MiniKit to Farcaster Conversion Guide

## Overview

This guide helps migrate MiniKit-based applications to the Farcaster protocol.

## Key Differences

| Feature | MiniKit | Farcaster |
|---------|---------|-----------|
| Auth | MiniKit Auth | Farcaster Auth |
| Frames | MiniKit Frames | Farcaster Frames |
| State | Local state | Hub-based state |
| Events | MiniKit events | Farcaster events |

## Migration Steps

1. Replace MiniKit dependencies with Farcaster packages
2. Update authentication flow
3. Migrate frame handlers
4. Update state management
5. Test all functionality
6. Deploy and verify

## Common Issues

- Authentication tokens may need regeneration
- Frame URLs must be updated
- State schema may differ
- Event formats changed
