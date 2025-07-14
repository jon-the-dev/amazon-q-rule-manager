# Amazon Q Rule Manager Frontend

A modern React frontend for browsing the Amazon Q Rule Manager catalog.

## Features

- **Dark Matrix-inspired Theme**: Modern dark interface with neon green accents
- **Advanced Search**: Search rules by name, description, tags, or category
- **Category Filtering**: Filter by programming language or technology
- **Detailed Rule Pages**: Comprehensive information about each rule
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Automatically synced with the latest catalog

## Development

### Prerequisites

- Node.js 18+ 
- npm

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will be available at `http://localhost:3000`.

### Building for Production

```bash
# Build for production
npm run build
```

The build artifacts will be in the `build/` directory.

### Deployment

The frontend is automatically deployed to GitHub Pages when changes are pushed to the main branch via GitHub Actions.

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── Header.js       # Navigation header
│   ├── RuleCard.js     # Rule display card
│   ├── SearchBar.js    # Search functionality
│   └── CategoryFilter.js # Category filtering
├── pages/              # Page components
│   ├── Home.js         # Main rules catalog page
│   └── RuleDetail.js   # Individual rule details
├── App.js              # Main app component
├── App.css             # App-wide styles
├── index.js            # React entry point
└── index.css           # Global styles
```

## Styling

The frontend uses a custom CSS approach with:
- CSS Grid and Flexbox for layouts
- CSS custom properties for theming
- Responsive design with mobile-first approach
- Matrix-inspired dark theme with green accents
- Smooth animations and transitions

## Data Source

The frontend fetches rule data from:
- `/rules_catalog.json` - Rule metadata and catalog information
- `/rules/*.md` - Individual rule content files

These files are automatically copied during the build process from the main Python package.
