# EchoSQL CSS Styles & Design System

This document contains all the CSS styles, animations, and design patterns used in the EchoSQL dashboard application.

## 🎨 Color Palette

### Primary Colors
- **Primary Background**: `#000000` (Black)
- **Secondary Background**: `#0a1a1a` (Very Dark Gray)
- **Card Background**: `#0a1a1a/50` (Semi-transparent)

### Border Colors
- **Primary Border**: `#gray-800`
- **Secondary Border**: `#gray-700/50`
- **Hover Border**: `#cyan-500/30`

### Accent Colors
- **Cyan**: `#22d3ee` (`cyan-400`)
- **Green**: `#4ade80` (`green-400`)
- **Blue**: `#3b82f6` (`blue-400`)

### Text Colors
- **Primary Text**: `white`
- **Secondary Text**: `gray-300`
- **Muted Text**: `gray-400`
- **Disabled Text**: `gray-500`

## 🔤 Typography

### Font Families
```css
@import url("https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=Open+Sans:ital,wght@0,300..800;1,300..800&family=Share+Tech+Mono&display=swap");

.font-dmsans {
  font-family: "DM Sans", sans-serif;
}

.font-dmmono {
  font-family: "DM Mono", monospace;
}

.font-opensans {
  font-family: "Open Sans", sans-serif;
}

.font-sharetechmono {
  font-family: "Share Tech Mono", monospace;
}
```

### Usage
- **DM Sans**: Main UI text, headings
- **DM Mono**: Code, technical text, buttons
- **Open Sans**: Body text, descriptions
- **Share Tech Mono**: Terminal/console text

## ✨ Custom Animations

### Wave Animation
```css
@keyframes wave {
  0%, 100% {
    transform: scaleY(0.5);
  }
  50% {
    transform: scaleY(1.5);
  }
}

.animate-wave {
  animation: wave 1s infinite ease-in-out;
}

.delay-100 { animation-delay: 0.1s; }
.delay-200 { animation-delay: 0.2s; }
.delay-300 { animation-delay: 0.3s; }
.delay-400 { animation-delay: 0.4s; }

.wave-bar {
  animation: wave 1s infinite ease-in-out;
  height: 20%;
}
```

### Neon Glow Effect
```css
@keyframes neon-glow {
  0% {
    box-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff;
  }
  50% {
    box-shadow: 0 0 20px #00ffff, 0 0 30px #00ffff, 0 0 40px #00ffff;
  }
  100% {
    box-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff;
  }
}

.animate-neon-glow {
  animation: neon-glow 1.5s infinite alternate;
}
```

### Typewriter Effect
```css
@keyframes typewriter {
  0% {
    width: 0;
  }
  40%, 60% {
    width: 17ch;
  }
  100% {
    width: 0;
  }
}

@keyframes blinkCursor {
  0%, 100% {
    border-color: transparent;
  }
  50% {
    border-color: white;
  }
}

.typewriter {
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
  border-right: 2px solid white;
  width: 0;
  animation: typewriter 6s steps(17, end) infinite,
    blinkCursor 0.7s step-end infinite;
}
```

### Gradient Animation
```css
@keyframes gradient {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.animate-gradient {
  animation: gradient 2s linear infinite;
}
```

### Shimmer Effect
```css
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
    opacity: 0;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    transform: translateX(100%);
    opacity: 0;
  }
}

.animate-shimmer {
  animation: shimmer 2s linear infinite;
}
```

## 🎯 Component Styles

### Dashboard Layout

#### Main Container
```css
.h-screen.overflow-hidden.bg-gradient-to-b.from-black.to-gray-900.flex.flex-col
```

#### Header Bar
```css
.p-4.bg-[#0a1a1a].border-b.border-gray-800
```

#### Brand Title
```css
.text-2xl.font-bold.text-transparent.bg-clip-text.bg-gradient-to-r.from-green-400.to-cyan-400
```

#### Main Content Area
```css
.flex-1.overflow-y-auto
```

### Database Cards

#### Card Container
```css
.relative.group.cursor-pointer.rounded-xl.px-6.py-8.backdrop-blur-sm.border-2.flex.flex-col.items-center.text-center
```

#### Default State
```css
.border-gray-700/50.hover:border-cyan-500/30.bg-[#0a1a1a]/50
```

#### Selected State
```css
.border-cyan-400.bg-[#0a1a1a]/80
```

#### Hover Effects
```css
.transition-all.duration-300.transform.hover:scale-[1.02].hover:shadow-[0_0_15px_rgba(34,211,238,0.1)]
```

#### Database Icons
```css
.text-6xl.text-cyan-400.mb-4
```

#### Database Names
```css
.text-2xl.font-semibold.text-white.group-hover:text-cyan-400.transition-colors.mb-2
```

#### Action Buttons
```css
.w-full.cursor-pointer.bg-gradient-to-r.from-green-400.to-cyan-400.text-white.rounded-xl.p-2.mt-2.hover:opacity-90.transition-all
```

#### Create New Database Button
```css
.relative.rounded-xl.p-6.border-2.border-dashed.backdrop-blur-sm.bg-[#0a1a1a]/50.border-gray-700/50.hover:border-cyan-500/30.transition-all.duration-300.group.flex.flex-col.items-center.justify-center.min-h-[200px].hover:shadow-[0_0_15px_rgba(34,211,238,0.1)]
```

### Navigation Bar

#### Main Navigation
```css
.bg-[#000000].flex.justify-between.items-center.p-8.shadow-md.border-1.border-b-[#3A3A3A]
```

#### Navigation Buttons
```css
.text-sm.md:text-md.cursor-pointer.text-white.bg-[#282828].font-dmmono.w-[90%].md:w-36.h-12.rounded-full.flex.justify-center.items-center
```

#### Mobile Menu
```css
.flex-col.md:flex.md:flex-row.gap-4.fixed.md:static.top-0.right-0.h-screen.md:h-auto.w-2/3.md:w-auto.bg-black.md:bg-transparent.z-50.md:z-auto.p-4.md:p-0.shadow-md.md:shadow-none
```

### Chat Interface

#### Chat Container
```css
.h-screen.bg-gradient-to-b.from-black.to-gray-900.flex.flex-col
```

#### Messages Area
```css
.flex-1.overflow-y-auto.p-4.space-y-6.scrollbar-thin.scrollbar-thumb-gray-700.scrollbar-track-transparent
```

#### Message Bubbles
```css
.px-4.py-3.rounded-2xl.text-sm.leading-relaxed.text-white.bg-transparent.border.border-gray-700
```

#### Loading Indicators
```css
.w-2.h-2.bg-blue-400.rounded-full.animate-pulse
```

#### Loading Message Container
```css
.w-full.flex.justify-start.px-4.my-4
.max-w-[70%].flex.flex-col.gap-1
.flex.items-center.gap-2
.text-blue-400.w-5.h-5
```

#### Error Messages
```css
.bg-red-900/50.border.border-red-500.rounded-lg.p-4.text-red-100.flex.items-center.justify-between.shadow-lg
```

### Voice Input Bar

#### Input Container
```css
.relative.rounded-xl.p-6.border-2.border-dashed.backdrop-blur-sm.bg-[#0a1a1a]/50.border-gray-700/50.hover:border-cyan-500/30.transition-all.duration-300.group
```

#### Microphone Button States
```css
/* Default */
.bg-gray-700.hover:bg-gray-600.text-white

/* Recording */
.bg-red-500.hover:bg-red-600.text-white

/* Processing */
.bg-yellow-500.hover:bg-yellow-600.text-black
```

#### Language Selector
```css
.bg-gray-700.text-white.rounded-lg.px-3.py-2.text-sm.border.border-gray-600.focus:outline-none.focus:ring-2.focus:ring-cyan-400
```

## 📜 Custom Scrollbar

### WebKit Browsers (Chrome, Safari, Edge)
```css
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
  background-color: #0a1a1a;
}

::-webkit-scrollbar-track {
  background: #1a1a1a;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #2a2a2a;
  border-radius: 4px;
  border: 2px solid #1a1a1a;
  transition: all 0.3s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(34, 211, 238, 0.4); /* cyan-400 with opacity */
  box-shadow: inset 0 0 6px rgba(34, 211, 238, 0.2);
}

::-webkit-scrollbar-corner {
  background: #1a1a1a;
}
```

### Firefox
```css
* {
  scrollbar-width: thin;
  scrollbar-color: #2a2a2a #1a1a1a;
}
```

### Custom Scrollbar Classes
```css
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
```

## 🎭 Loading States

### Spinner
```css
.w-8.h-8.border-2.border-cyan-400.border-t-transparent.rounded-full.animate-spin.mx-auto.mb-4
```

### Gradient Loading Text
```css
.animate-gradient.bg-gradient-to-r.from-gray-500.via-white.to-gray-500.text-transparent.bg-clip-text.bg-[length:200%_100%].font-medium.tracking-wide.drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]
```

### Shimmer Overlay
```css
.absolute.top-0.left-0.right-0.h-full.pointer-events-none.bg-gradient-to-r.from-transparent.via-white/20.to-transparent.animate-shimmer.opacity-50
```

## 🔘 Buttons & Interactive Elements

### Primary Button
```css
.bg-gradient-to-r.from-green-400.to-cyan-400.text-white.rounded-xl.p-2.hover:opacity-90.transition-all
```

### Secondary Button
```css
.bg-gray-700.text-white.rounded-lg.px-4.py-2.hover:bg-gray-600.transition-colors
```

### Icon Button
```css
.text-gray-300.hover:text-cyan-400.transition-colors.duration-300.rounded-lg.cursor-pointer
```

### Form Inputs
```css
.bg-gray-800.border.border-gray-600.text-white.rounded-lg.px-3.py-2.focus:outline-none.focus:ring-2.focus:ring-cyan-400.focus:border-transparent
```

## 🏷️ Utility Classes

### Backdrop Effects
```css
.backdrop-blur-sm
.bg-[#0a1a1a]/50
.bg-[#0a1a1a]/80
```

### Gradients
```css
.bg-gradient-to-b.from-black.to-gray-900
.bg-gradient-to-r.from-green-400.to-cyan-400
.text-transparent.bg-clip-text.bg-gradient-to-r.from-green-400.to-cyan-400
```

### Shadows
```css
.shadow-[0_0_15px_rgba(34,211,238,0.1)]
.drop-shadow-[0_0_15px_rgba(255,255,255,0.3)]
```

### Transitions
```css
.transition-all.duration-300
.transition-colors.duration-300
.transition-all.duration-300.transform.hover:scale-[1.02]
```

## 📱 Responsive Design

### Breakpoint Classes
```css
.max-sm:hidden      /* Hidden on small screens */
.md:hidden          /* Hidden on medium+ screens */
.md:flex            /* Flex on medium+ screens */
.md:w-36            /* Width on medium+ screens */
.lg:grid-cols-3     /* Grid columns on large screens */
.xl:grid-cols-4     /* Grid columns on extra large screens */
```

### Grid System
```css
.grid.grid-cols-1.sm:grid-cols-2.lg:grid-cols-3.xl:grid-cols-4.gap-6
```

## 🎨 Usage Examples

### Database Card Example
```jsx
<div className="relative group cursor-pointer rounded-xl px-6 py-8 
  backdrop-blur-sm border-2 flex flex-col items-center text-center
  border-gray-700/50 hover:border-cyan-500/30 bg-[#0a1a1a]/50
  transition-all duration-300 transform hover:scale-[1.02]
  hover:shadow-[0_0_15px_rgba(34,211,238,0.1)]">
  
  <div className="text-6xl text-cyan-400 mb-4">
    <DatabaseIcon />
  </div>
  
  <h3 className="text-2xl font-semibold text-white group-hover:text-cyan-400 transition-colors mb-2">
    {database.name}
  </h3>
  
  <button className="w-full cursor-pointer bg-gradient-to-r from-green-400 to-cyan-400 
    text-white rounded-xl p-2 mt-2 hover:opacity-90 transition-all">
    Connect
  </button>
</div>
```

### Loading Animation Example
```jsx
<div className="flex items-center gap-2">
  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{animationDelay: '0.1s'}}></div>
  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
  <span className="ml-2 text-gray-400">Processing...</span>
</div>
```

---

**EchoSQL Design System** - Consistent, modern, and accessible styling for database interfaces.
