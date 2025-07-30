# PRIDE Archive Professional UI

A modern, professional web interface for the PRIDE Archive MCP server with enhanced user experience and design.

## Features

### 🎨 Modern Design
- **Professional Color Scheme**: Clean, scientific aesthetic with blue primary colors
- **Typography**: Inter font family for excellent readability
- **Responsive Layout**: Works seamlessly on desktop and mobile devices
- **Visual Hierarchy**: Clear organization with cards, headers, and sections

### 💬 Enhanced Chat Interface
- **Real-time Messaging**: WebSocket-based communication
- **Message Avatars**: Visual distinction between user and AI messages
- **Typing Indicators**: Animated dots showing when AI is processing
- **Status Indicators**: Connection status with color-coded indicators

### 🚀 Improved User Experience
- **Quick Examples**: Clickable example queries to get started
- **Professional Branding**: PRIDE Archive logo and consistent styling
- **Smooth Animations**: Hover effects and transitions
- **Error Handling**: Clear error messages with proper styling

## Quick Start

### Option 1: Use the Start Script
```bash
# Start both MCP server and Professional UI
./start.sh
```

### Option 2: Manual Start
```bash
# Terminal 1: Start MCP server
uv run python main.py --host 127.0.0.1 --port 9000

# Terminal 2: Start Professional UI
uv run python test_professional_ui.py
```

### Option 3: Direct Module Execution
```bash
cd mcp_client_tools
uv run python -m mcp_client_tools.professional_ui --server-url http://127.0.0.1:9000 --port 9090
```

## Access the Interface

Once started, open your browser and navigate to:
```
http://127.0.0.1:9090
```

## Design System

### Color Palette
- **Primary Blue**: `#2563eb` - Main brand color
- **Gray Scale**: Professional grays for text and backgrounds
- **Status Colors**: Green (success), Orange (warning), Red (error)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800
- **Hierarchy**: Clear heading and body text sizing

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Hover effects with smooth transitions
- **Input Fields**: Focus states with blue accent
- **Messages**: Distinct styling for user vs AI messages

## Technical Details

### Architecture
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: FastAPI with WebSocket support
- **Styling**: Custom CSS with CSS variables
- **Responsive**: Mobile-first design approach

### Key Features
- **WebSocket Communication**: Real-time bidirectional messaging
- **Auto-reconnection**: Automatic WebSocket reconnection on disconnect
- **Error Handling**: Graceful error display and recovery
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Comparison with Previous UI

| Feature | Previous UI | Professional UI |
|---------|-------------|-----------------|
| Design | Basic Tailwind | Custom professional design |
| Typography | Default fonts | Inter font family |
| Color Scheme | Standard blue | Professional blue palette |
| Layout | Simple grid | Card-based layout |
| Animations | Basic hover | Smooth transitions |
| Mobile | Basic responsive | Mobile-first design |
| Branding | Minimal | PRIDE Archive branding |

## Customization

### Colors
Edit the CSS variables in the `:root` selector:
```css
:root {
    --primary-600: #2563eb;  /* Main blue */
    --gray-900: #111827;     /* Dark text */
    /* ... other colors */
}
```

### Typography
Change the font family in the body selector:
```css
body {
    font-family: 'Your Font', -apple-system, BlinkMacSystemFont, sans-serif;
}
```

### Layout
Modify the container max-width for different screen sizes:
```css
.container {
    max-width: 1200px;  /* Adjust as needed */
}
```

## Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## Performance

- **Lightweight**: No heavy frameworks, just vanilla CSS/JS
- **Fast Loading**: Optimized CSS and minimal JavaScript
- **Efficient**: WebSocket connection for real-time updates
- **Responsive**: Smooth performance on all device sizes

## Future Enhancements

- [ ] Dark mode support
- [ ] Advanced search filters
- [ ] Data visualization components
- [ ] Export functionality
- [ ] User preferences
- [ ] Accessibility improvements
- [ ] Internationalization support 