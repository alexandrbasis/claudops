# Rule Sections

This file defines the section metadata for React Native + Expo best practices.

## Section Structure

Each section has:
- **name**: Section identifier (used as filename prefix)
- **title**: Human-readable section name
- **impact**: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
- **description**: What this section covers

## Sections

### rendering (Core Rendering)
**Impact**: CRITICAL
Fundamental React Native rendering rules. Violations cause runtime crashes or broken UI.

### list-performance (List Performance)
**Impact**: HIGH
Optimizing virtualized lists (FlatList, LegendList, FlashList) for smooth scrolling and fast updates.

### animation (Animation)
**Impact**: HIGH
GPU-accelerated animations, Reanimated patterns, and avoiding render thrashing during gestures.

### scroll-performance (Scroll Performance)
**Impact**: HIGH
Tracking scroll position without causing render thrashing.

### navigation (Navigation)
**Impact**: HIGH
Using native navigators for stack and tab navigation instead of JS-based alternatives.

### react-state (React State)
**Impact**: MEDIUM
Patterns for managing React state to avoid stale closures and unnecessary re-renders.

### state-architecture (State Architecture)
**Impact**: MEDIUM
Ground truth principles for state variables and derived values.

### react-compiler (React Compiler)
**Impact**: MEDIUM
Compatibility patterns for React Compiler with React Native and Reanimated.

### user-interface (User Interface)
**Impact**: MEDIUM
Native UI patterns for images, menus, modals, styling, and platform-consistent interfaces.

### design-system (Design System)
**Impact**: MEDIUM
Architecture patterns for building maintainable component libraries.

### monorepo (Monorepo)
**Impact**: LOW
Dependency management and native module configuration in monorepos.

### third-party-dependencies (Third-Party Dependencies)
**Impact**: LOW
Wrapping and re-exporting third-party dependencies for maintainability.

### javascript (JavaScript)
**Impact**: LOW
Micro-optimizations like hoisting expensive object creation.

### fonts (Fonts)
**Impact**: LOW
Native font loading for improved performance.
