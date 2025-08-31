# Coastal Monitor Frontend 🌊

A modern, responsive React application built with Next.js for coastal monitoring and flood forecasting.

## 🚀 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with Tailwind
- **Charts**: Recharts
- **Maps**: Leaflet with React-Leaflet
- **Authentication**: Supabase
- **State Management**: React Hooks
- **HTTP Client**: Fetch API

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── AlertManagement.tsx
│   │   │   ├── CoastalMap.tsx
│   │   │   ├── DataVisualization.tsx
│   │   │   ├── FloodForecasting.tsx
│   │   │   ├── MonitoringDashboard.tsx
│   │   │   ├── NotificationSettings.tsx
│   │   │   ├── StationsList.tsx
│   │   │   ├── TideChart.tsx
│   │   │   └── WaveChart.tsx
│   │   ├── dashboard/            # Dashboard pages
│   │   │   └── page.tsx
│   │   ├── login/               # Authentication pages
│   │   │   └── page.tsx
│   │   ├── globals.css          # Global styles
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Home page
│   └── lib/
│       └── supabase.ts          # Supabase client configuration
├── public/                      # Static assets
├── lib/
│   └── supabase.ts             # Supabase configuration
├── package.json
├── next.config.ts
├── tailwind.config.ts
└── tsconfig.json
```

## 🛠️ Installation

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Setup Steps

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env.local
   ```

4. **Configure environment variables** in `.env.local`:
   ```env
   # API Configuration
   NEXT_PUBLIC_API_URL=http://localhost:8000
   
   # Supabase Configuration
   NEXT_PUBLIC_SUPABASE_URL=your-supabase-project-url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
   ```

5. **Start development server**:
   ```bash
   npm run dev
   ```

6. **Open in browser**: `http://localhost:3001`

## 🔧 Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix
```

### Development Workflow

1. **Component Development**:
   - Create new components in `src/app/components/`
   - Follow TypeScript best practices
   - Use Tailwind CSS for styling
   - Implement responsive design

2. **Page Development**:
   - Add new pages in `src/app/`
   - Use Next.js App Router conventions
   - Implement proper SEO metadata

3. **API Integration**:
   - Use fetch API for HTTP requests
   - Handle loading and error states
   - Implement proper TypeScript interfaces

## 🎨 Styling Guidelines

### Tailwind CSS Classes

- **Layout**: Use flexbox and grid utilities
- **Spacing**: Consistent padding and margins (p-4, m-6, etc.)
- **Colors**: Use semantic color classes
- **Typography**: Consistent font sizes and weights
- **Responsive**: Mobile-first approach with breakpoint prefixes

### Component Patterns

```tsx
// Example component structure
import React from 'react';

interface ComponentProps {
  title: string;
  data: any[];
  onAction?: () => void;
}

const Component: React.FC<ComponentProps> = ({ title, data, onAction }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      {/* Component content */}
    </div>
  );
};

export default Component;
```

## 🗺️ Key Components

### CoastalMap
- Interactive Leaflet map
- Monitoring station markers
- Real-time data display
- Station selection functionality

### DataVisualization
- Container for TideChart and WaveChart
- Responsive chart layout
- Real-time data updates

### TideChart & WaveChart
- Recharts-based visualizations
- Time-series data display
- Interactive tooltips
- Multiple data series

### FloodForecasting
- AI-powered predictions
- Risk assessment display
- Model performance metrics
- Contributing factors analysis

### StationsList
- Tabular station data
- Filtering and sorting
- Status indicators
- Selection handling

## 🔐 Authentication

### Supabase Integration

```tsx
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

### Authentication Flow

1. **Login**: Email/password authentication
2. **Session Management**: Automatic token refresh
3. **Protected Routes**: Dashboard access control
4. **Logout**: Session cleanup

## 📱 Responsive Design

### Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Layout Adaptations

- **Mobile**: Single column, stacked components
- **Tablet**: Two-column grid, condensed navigation
- **Desktop**: Full multi-column layout, expanded features

## 🚀 Performance Optimization

### Best Practices

1. **Code Splitting**: Automatic with Next.js
2. **Image Optimization**: Use Next.js Image component
3. **Lazy Loading**: Implement for heavy components
4. **Memoization**: Use React.memo for expensive renders
5. **Bundle Analysis**: Regular bundle size monitoring

### Monitoring

```bash
# Analyze bundle size
npm run build
npm run analyze
```

## 🧪 Testing

### Testing Strategy

1. **Unit Tests**: Component logic testing
2. **Integration Tests**: API integration testing
3. **E2E Tests**: User workflow testing

### Setup Testing (Future)

```bash
# Install testing dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom jest

# Run tests
npm test
```

## 🚀 Deployment

### Build Process

```bash
# Create production build
npm run build

# Test production build locally
npm start
```

### Deployment Platforms

#### Vercel (Recommended)

1. Connect GitHub repository
2. Configure environment variables
3. Deploy automatically on push

#### Netlify

1. Build command: `npm run build`
2. Publish directory: `out`
3. Configure environment variables

### Environment Variables

**Production Environment**:
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Errors**:
   - Check TypeScript errors: `npm run type-check`
   - Verify environment variables
   - Clear `.next` cache

2. **Runtime Errors**:
   - Check browser console
   - Verify API connectivity
   - Check Supabase configuration

3. **Styling Issues**:
   - Verify Tailwind CSS compilation
   - Check responsive breakpoints
   - Clear browser cache

### Debug Commands

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Check TypeScript
npm run type-check
```

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Recharts Documentation](https://recharts.org/)
- [React Leaflet Documentation](https://react-leaflet.js.org/)

## 🤝 Contributing

1. Follow TypeScript best practices
2. Use consistent naming conventions
3. Implement responsive design
4. Add proper error handling
5. Write meaningful commit messages
6. Test on multiple devices/browsers

---

**Happy coding! 🚀**
