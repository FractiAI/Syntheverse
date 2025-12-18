# Flask UI Templates

HTML templates and frontend assets for the Syntheverse legacy web interface.

## Overview

This directory contains Jinja2 templates, static assets, and presentation layer components for the Flask-based web interface that provides a traditional web experience for Syntheverse users.

## Template Structure

### Base Templates
- **base.html**: Main template with common layout and navigation
- **layout.html**: Responsive layout structure and CSS framework integration
- **navigation.html**: Site navigation and user menu components

### Page Templates
- **dashboard.html**: User dashboard with contribution overview
- **submission.html**: File upload and contribution submission forms
- **archive.html**: Contribution archive browsing interface
- **profile.html**: User profile and settings management

### Component Templates
- **contribution_card.html**: Individual contribution display component
- **evaluation_results.html**: Scoring and qualification display
- **pagination.html**: Result pagination controls
- **modals.html**: Dialog and modal components

## Static Assets

### CSS Files
- **styles.css**: Main stylesheet with Syntheverse branding
- **responsive.css**: Mobile and tablet responsive styles
- **animations.css**: UI transition and animation effects

### JavaScript Files
- **app.js**: Main application logic and event handlers
- **validation.js**: Form validation and user input processing
- **api.js**: Frontend API communication utilities

## Template Variables

### Global Variables
```jinja2
{{ user }}           # Current user object
{{ config }}         # Application configuration
{{ csrf_token }}     # CSRF protection token
{{ request.endpoint }} # Current page endpoint
```

### Page-Specific Variables
```jinja2
{{ contributions }}  # List of user contributions
{{ evaluation }}     # Current evaluation results
{{ pagination }}     # Pagination metadata
{{ filters }}        # Active search/filter parameters
```

## Usage

### Template Rendering
```python
from flask import render_template

@app.route('/dashboard')
@login_required
def dashboard():
    contributions = get_user_contributions(current_user.id)
    return render_template('dashboard.html',
                         contributions=contributions,
                         user=current_user)
```

### Template Inheritance
```html
<!-- child_template.html -->
{% extends "base.html" %}

{% block title %}Custom Page Title{% endblock %}

{% block content %}
  <div class="custom-content">
    <!-- Page-specific content -->
  </div>
{% endblock %}
```

## Integration

### Flask Application
- **Template Loading**: Automatic template discovery and caching
- **Context Processors**: Global variable injection
- **Error Handlers**: Custom error page templates

### Static Asset Management
- **URL Generation**: `url_for('static', filename='css/styles.css')`
- **Cache Busting**: Version query parameters for asset updates
- **CDN Integration**: Optional external asset hosting

## Development Guidelines

### Template Best Practices
- **Semantic HTML**: Proper document structure and accessibility
- **Jinja2 Filters**: Custom filters for data formatting
- **Macro Usage**: Reusable template components
- **Internationalization**: `{{ _('text') }}` for i18n support

### CSS Organization
- **BEM Methodology**: Block-Element-Modifier naming convention
- **CSS Variables**: Theme and branding customization
- **Responsive Design**: Mobile-first approach

### JavaScript Integration
- **Progressive Enhancement**: Core functionality without JavaScript
- **Event Delegation**: Efficient event handling patterns
- **API Integration**: RESTful communication with backend

## Maintenance

- **Template Validation**: HTML validation and accessibility testing
- **Asset Optimization**: Minification and compression for production
- **Browser Testing**: Cross-browser compatibility verification
- **Performance Monitoring**: Template rendering performance tracking

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Flask UI](../../ui_web/AGENTS.md) - Web interface documentation
