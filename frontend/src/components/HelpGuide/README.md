# UniPass Help Guide System

## Overview

The UniPass Help Guide System is a production-ready, reusable component system that provides contextual help and onboarding for all Cortex AI modules. It features dynamic content loading, toast notifications, and smooth animations.

## Features

### ✨ Key Capabilities
- **Dynamic Content**: Automatically loads help content based on module ID
- **Toast Notifications**: Shows a subtle notification when users land on a module page
- **Smooth Animations**: Production-quality cubic-bezier animations for all interactions
- **Responsive Design**: Fully responsive with mobile-optimized layouts
- **Modular Architecture**: Easy to extend for new modules
- **Emoji-Free Content**: Professional, clean text without emoji clutter
- **Accessible**: ARIA labels and keyboard navigation support

### 🎨 Components

#### 1. HelpGuide Component
Main component that renders the floating help button and help window.

**Location**: `/frontend/src/components/HelpGuide/HelpGuide.tsx`

**Props**:
```typescript
interface HelpGuideProps {
  content: HelpGuideContent;
  showToastOnMount?: boolean; // Default: true
}
```

#### 2. Toast Notification
Displays a brief message to inform users about available help.

**Location**: `/frontend/src/components/Toast/Toast.tsx`

**Props**:
```typescript
interface ToastProps {
  message: string;
  duration?: number; // Default: 4000ms
  onClose?: () => void;
}
```

#### 3. Help Guide Configuration
Centralized configuration for all module help content.

**Location**: `/frontend/src/components/HelpGuide/helpGuideConfig.ts`

## Usage

### Adding Help to an Existing Page

```typescript
import HelpGuide, { getHelpContent } from "@/components/HelpGuide";

export default function YourPage() {
  const helpContent = getHelpContent('your-module-id');
  
  return (
    <div>
      {/* Your page content */}
      
      {/* Add Help Guide at the end */}
      {helpContent && <HelpGuide content={helpContent} />}
    </div>
  );
}
```

### Adding a New Module's Help Content

1. Open `/frontend/src/components/HelpGuide/helpGuideConfig.ts`

2. Add a new entry to the `helpGuideConfig` object:

```typescript
export const helpGuideConfig: Record<string, HelpGuideContent> = {
  // ... existing modules
  
  'your-module-id': {
    moduleId: 'your-module-id',
    moduleName: 'Your Module Name',
    displayName: 'Cortex Your Module Dashboard',
    sections: [
      {
        title: 'What is This?',
        content: 'Brief description of what the module does.',
        type: 'paragraph'
      },
      {
        title: 'How It Works',
        content: [
          'First key point about how it works',
          'Second key point',
          'Third key point'
        ],
        type: 'list'  // or 'ordered-list'
      },
      {
        title: 'Getting Started',
        content: [
          'First step to get started',
          'Second step',
          'Third step'
        ],
        type: 'ordered-list'
      },
      // Add more sections as needed
    ]
  }
};
```

### Section Types

**Paragraph**: Single paragraph of text
```typescript
{
  title: 'Section Title',
  content: 'Your text here',
  type: 'paragraph'
}
```

**Unordered List**: Bullet points
```typescript
{
  title: 'Section Title',
  content: [
    'First item',
    'Second item',
    'Third item'
  ],
  type: 'list'
}
```

**Ordered List**: Numbered steps
```typescript
{
  title: 'Section Title',
  content: [
    'First step',
    'Second step',
    'Third step'
  ],
  type: 'ordered-list'
}
```

## Current Modules

### 1. Descriptive Analytics (`descriptive-analytics`)
- Analytics overview and insights
- Department participation metrics
- Time pattern analysis
- Engagement tracking

### 2. Anomaly Detection (`anomaly-detection`)
- AI-powered anomaly detection
- Isolation Forest algorithm
- Suspicious pattern identification
- Model training and retraining

### 3. Prediction Model (`prediction-model`)
- Attendance forecasting (coming soon)
- Engagement predictions
- Risk assessment
- Capacity planning

## Styling

### Toast Notifications
- **Position**: Fixed top-right (5.5rem from top, 2rem from right)
- **Animation**: Slide in from right with fade
- **Duration**: 5 seconds (configurable)
- **Colors**: Yellow/amber gradient (#fbbf24 to #f59e0b)

### Help Float Button
- **Position**: Fixed bottom-right (2rem from bottom, 2rem from right)
- **Size**: 56px × 56px circular button
- **Colors**: Yellow/amber gradient with glow effect
- **Hover**: Scales to 1.1× with icon rotation

### Help Window
- **Position**: Fixed bottom-right, above the float button
- **Size**: 440px width, max 640px height
- **Animation**: Slides up from bottom-right with scale effect
- **Header**: Purple gradient (#667eea to #764ba2)
- **Content**: White background with custom scrollbar

## Customization

### Changing Toast Duration
```typescript
<HelpGuide 
  content={helpContent} 
  showToastOnMount={true}  // Shows toast
/>
```

To disable toast:
```typescript
<HelpGuide 
  content={helpContent} 
  showToastOnMount={false}  // No toast
/>
```

### Custom Styling
Override styles in your module's SCSS file:

```scss
.help-float-button {
  // Your custom styles
  bottom: 3rem; // Example: different position
}
```

## Best Practices

1. **Content Guidelines**:
   - Keep sections concise (3-5 items per list)
   - Use clear, action-oriented language
   - Avoid jargon and technical terms when possible
   - No emojis in content for professional appearance

2. **Section Organization**:
   - Start with "What is This?" for context
   - Follow with "How It Works" for mechanism
   - Include "Getting Started" for onboarding
   - Add practical examples in "Key Features"
   - End with maintenance tips if applicable

3. **Accessibility**:
   - All buttons have aria-label attributes
   - Keyboard navigation supported
   - Clear focus states on interactive elements

4. **Performance**:
   - Help content is loaded only when component mounts
   - Toast auto-dismisses to prevent clutter
   - Smooth animations use hardware acceleration

## File Structure

```
frontend/src/
├── components/
│   ├── HelpGuide/
│   │   ├── HelpGuide.tsx          # Main component
│   │   ├── HelpGuide.scss         # Styles
│   │   ├── helpGuideConfig.ts     # Content configuration
│   │   └── index.ts               # Exports
│   └── Toast/
│       ├── Toast.tsx              # Toast component
│       ├── Toast.scss             # Toast styles
│       └── index.ts               # Exports
└── app/(app)/
    └── analytics/
        ├── page.tsx               # Descriptive Analytics (uses HelpGuide)
        └── anomaly/
            └── page.tsx           # Anomaly Detection (uses HelpGuide)
```

## Troubleshooting

### Help button not appearing
- Ensure `helpContent` is not null
- Check that module ID exists in `helpGuideConfig`
- Verify component is rendered at the end of your page

### Toast not showing
- Check `showToastOnMount` prop is not set to `false`
- Verify Toast component is imported correctly
- Check z-index conflicts with other fixed elements

### Styling issues
- Import HelpGuide.scss is automatic via component
- Check for CSS conflicts with parent containers
- Verify responsive breakpoints match your design

## Future Enhancements

- [ ] Keyboard shortcuts to open help (e.g., `?`)
- [ ] Search functionality within help content
- [ ] Video tutorial integration
- [ ] Interactive walkthroughs
- [ ] User feedback collection
- [ ] Analytics tracking for help usage

## Support

For issues or feature requests, contact the development team or create an issue in the project repository.

---

**Version**: 1.0.0  
**Last Updated**: February 2026  
**Maintained By**: UniPass Development Team
