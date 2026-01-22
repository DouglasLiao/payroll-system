# Design System High-Level Diagram

This diagram represents the high-level architecture of the Design System integrated into the Payroll System. It details the relationship between the core token foundations, component overrides, and the theming engine that supports light and dark modes.

```mermaid
classDiagram
    %% Core Theme Engine
    class ThemeEngine {
        +getTheme(mode: PaletteMode) Theme
        +createTheme(options)
    }

    %% Token Foundations
    class Foundations {
        +Palette
        +Typography
        +Shape
    }

    class Palette {
        +Primary: Indigo (#4F46E5 / #6366F1)
        +Secondary: Slate (#1E293B / #F8FAFC)
        +Background: Slate 50 / Slate 950
        +Text: Slate 900 / Slate 50
        +Divider: Slate 200 / Slate 800
    }

    class Typography {
        +FontFamily: "Inter", system-ui
        +Scale: H1 (2.5rem) ... Subtitle2 (0.75rem)
        +Weights: 400, 500, 600, 700
    }

    class Shape {
        +BorderRadius: 8px (Default)
    }

    %% Component Customizations
    class Components {
        <<Overrides>>
        +MuiButton
        +MuiCard
        +MuiListItemButton
        +MuiTableCell
    }

    %% Component Details
    class MuiButton {
        +TextTransform: none
        +BorderRadius: 8px
        +FontWeight: 600
        +BoxShadow: none (contained)
    }

    class MuiCard {
        +BorderRadius: 12px
        +BoxShadow: Custom Slate Shadows
        +Border: 1px solid Slate
    }

    class MuiListItemButton {
        +BorderRadius: 8px
        +SelectedState: Indigo Tint
    }

    class MuiTableCell {
        +BorderBottom: Colored by Mode
    }

    %% Relationships
    ThemeEngine --> Foundations : configures
    Foundations *-- Palette
    Foundations *-- Typography
    Foundations *-- Shape
    ThemeEngine --> Components : injects styles

    Components *-- MuiButton
    Components *-- MuiCard
    Components *-- MuiListItemButton
    Components *-- MuiTableCell

    %% Modes
    class Modes {
        <<Enumeration>>
        Light
        Dark
    }

    Palette ..> Modes : adapts to
```

## Key Design Principles

1.  **Premium Aesthetics**: Usage of Inter font, custom shadows, and refined Indigo/Slate palette.
2.  **Glassmorphism**: Applied in key areas (e.g., Login Card) using backdrop-filter and translucency.
3.  **Consistency**: Global overrides ensure all MUI components align with the design system tokens.
4.  **Dark Mode Support**: First-class support with semantic color mapping for backgrounds and text.
