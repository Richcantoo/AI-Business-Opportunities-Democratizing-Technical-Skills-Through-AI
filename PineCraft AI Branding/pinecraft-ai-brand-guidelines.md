# PineCraft AI Brand Guidelines

## Brand Identity

### Mission Statement
PineCraft AI revolutionizes Pine Script development by combining cutting-edge artificial intelligence with intuitive design, transforming syntax errors into trading success in seconds.

### Brand Personality
- **Futuristic**: Embracing the digital frontier of AI-powered trading
- **Precise**: Error-free code generation with mathematical accuracy
- **Accessible**: Making complex Pine Script development simple
- **Innovative**: Pushing the boundaries of automated trading solutions

## Visual Identity

### Logo Concept
The PineCraft AI logo combines three key elements:
1. **Geometric Pine Tree**: Representing Pine Script, rendered in a digital, circuit-board style
2. **Circuit Patterns**: Symbolizing AI and technological innovation
3. **Data Nodes**: Representing the flow of trading data and algorithms

### Color Palette

#### Primary Colors
- **Electric Blue** `#00D9FF` - Primary brand color, representing technology and trust
- **Energy Orange** `#FF9F00` - Secondary accent, representing action and alerts

#### Supporting Colors
- **Deep Space** `#0A0E1A` - Dark background for that Tron Legacy aesthetic
- **Grid Blue** `#1A4F63` - Subtle grid patterns and secondary elements
- **Electric White** `#F0F8FF` - Clean text on dark backgrounds

#### Usage Guidelines
- Use Electric Blue for primary CTAs, headers, and key UI elements
- Energy Orange for alerts, notifications, and important highlights
- Maintain high contrast ratios for accessibility (WCAG AA compliance)
- Apply glow effects sparingly for emphasis

### Typography

#### Font Families
1. **Display Font**: Orbitron (900 weight)
   - Logo and major headlines
   - All caps recommended
   
2. **Heading Font**: Exo 2 (300-600 weights)
   - Section headers and subheadings
   - Mixed case
   
3. **Body Font**: Exo 2 (300-400 weights)
   - General text and descriptions
   
4. **Code Font**: JetBrains Mono (400-600 weights)
   - Pine Script code display
   - Terminal/console output

### Logo Variations

#### Primary Logo
- Horizontal layout with icon + text
- Use on dark backgrounds preferably
- Minimum size: 200px width

#### Icon Only
- Square format for app icons
- Stylized `⟨P⟩` mark
- Minimum size: 32px

#### Monochrome Versions
- Single color versions for limited color applications
- White on dark or blue on light backgrounds only

## Digital Applications

### UI/UX Principles
1. **Dark Mode First**: Primary interface should be dark with neon accents
2. **Grid Patterns**: Subtle animated grid backgrounds
3. **Glow Effects**: Strategic use of CSS glow for interactive elements
4. **Sharp Edges**: Minimal border radius (max 10px)

### Animation Guidelines
- Subtle pulse animations for live elements
- Circuit flow patterns for loading states
- Smooth transitions (0.3s ease)
- No jarring or sudden movements

### Component Styling

#### Buttons
```css
.primary-button {
    background: transparent;
    border: 2px solid #00D9FF;
    color: #00D9FF;
    padding: 12px 24px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    transition: all 0.3s ease;
}

.primary-button:hover {
    background: #00D9FF;
    color: #0A0E1A;
    box-shadow: 0 0 20px rgba(0, 217, 255, 0.8);
}
```

#### Cards
- Dark background with subtle transparency
- Thin glowing borders
- Hover state with elevation and increased glow

## Voice and Tone

### Brand Voice Attributes
- **Technical but Accessible**: Expert knowledge delivered simply
- **Confident**: We know Pine Script inside and out
- **Helpful**: Always focused on user success
- **Forward-thinking**: Embracing the future of automated trading

### Example Messaging
- ❌ "Our AI might help fix your code"
- ✅ "Transform syntax errors into profitable strategies instantly"

- ❌ "Pine Script error checker"
- ✅ "AI-powered Pine Script v6 code generation and optimization"

## Implementation Examples

### Web Application Header
```html
<header class="app-header">
    <div class="logo-container">
        <span class="logo-mark">⟨P⟩</span>
        <span class="logo-text">PINECRAFT<span class="ai">AI</span></span>
    </div>
    <nav class="main-nav">
        <a href="#" class="nav-link">Generate</a>
        <a href="#" class="nav-link">Analyze</a>
        <a href="#" class="nav-link">Learn</a>
    </nav>
</header>
```

### Error Message Styling
```html
<div class="error-message">
    <span class="error-icon">⚠️</span>
    <h3>Syntax Error Detected</h3>
    <p>Don't worry - PineCraft AI will fix it in seconds.</p>
    <button class="fix-button">Auto-Fix with AI</button>
</div>
```

## Brand Assets

### File Formats
- **Logo**: SVG (preferred), PNG (transparent background)
- **Icons**: SVG for web, ICO for favicons
- **Colors**: CSS variables, Figma styles, Adobe ASE

### Spacing and Clear Space
- Minimum clear space around logo: 0.5x the height of the logo
- Don't place other elements within this clear space
- Maintain visual breathing room in all applications

## Usage Don'ts

1. **Don't alter the logo** proportions or colors
2. **Don't use** rainbow gradients or multiple colors in the logo
3. **Don't apply** heavy drop shadows or 3D effects
4. **Don't use** on busy backgrounds without proper contrast
5. **Don't combine** with conflicting visual styles (e.g., organic, hand-drawn)

## Social Media

### Profile Images
- Use icon-only version with dark background
- Ensure high contrast for small sizes

### Cover Images
- Incorporate grid patterns and glow effects
- Include tagline prominently
- Maintain brand color scheme

## Contact

For brand inquiries or asset requests, please refer to the digital asset library or contact the brand team. 