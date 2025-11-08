# Contributing to MemeCraft Pro

First off, thank you for considering contributing to MemeCraft Pro! It's people like you that make MemeCraft Pro such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to support@memecraft.pro.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed and what behavior you expected**
* **Include screenshots if possible**
* **Include your environment details** (OS, browser, Node version, Python version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List some examples of how it would be used**

### Pull Requests

* Fill in the required template
* Follow the coding style guidelines
* Include tests when adding new features
* Update documentation as needed
* Ensure all tests pass

## Development Process

### Setup Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/memecraft-pro.git
   cd memecraft-pro
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   yarn install
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn server:app --reload

   # Terminal 2 - Frontend
   cd frontend
   yarn start
   ```

### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow the style guide
   - Add tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   yarn test
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

## Style Guides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

**Commit Message Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning (formatting, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvements
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

**Example:**
```
feat: add GIF export functionality

Add support for exporting memes as animated GIFs using gif.js library.
Users can now create multi-frame animations with custom timing.

Closes #123
```

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

```python
# Good
def calculate_viral_score(engagement_data: dict) -> int:
    """
    Calculate viral potential score based on engagement metrics.
    
    Args:
        engagement_data: Dictionary containing likes, shares, comments
        
    Returns:
        Viral score between 0 and 100
    """
    likes = engagement_data.get('likes', 0)
    shares = engagement_data.get('shares', 0)
    score = min((likes / 1000 + shares / 100), 100)
    return int(score)

# Bad
def calc_score(data):
    l = data['likes']
    s = data['shares']
    return int(min((l/1000+s/100),100))
```

**Key Points:**
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black formatter default)
- Use type hints for function arguments and return values
- Write docstrings for all public functions and classes
- Use descriptive variable names
- Keep functions focused and small (<50 lines)

### JavaScript/React Style Guide

Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) with React:

```javascript
// Good
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const MemeCard = ({ meme, onEdit, onDelete }) => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleEdit = async () => {
    setIsLoading(true);
    try {
      await onEdit(meme.id);
      navigate(`/editor/${meme.id}`);
    } catch (error) {
      console.error('Edit failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="meme-card" data-testid={`meme-${meme.id}`}>
      <h3>{meme.title}</h3>
      <Button onClick={handleEdit} disabled={isLoading}>
        {isLoading ? 'Loading...' : 'Edit'}
      </Button>
    </div>
  );
};

export default MemeCard;
```

**Key Points:**
- Use functional components with hooks
- Use arrow functions for component definitions
- Add PropTypes or TypeScript types
- Use destructuring for props
- Add `data-testid` attributes for testing
- Keep components small and focused
- Use meaningful variable names
- Follow React hooks rules

### CSS/Tailwind Guidelines

```javascript
// Good - Organized, semantic classes
<div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-800">
  <h2 className="text-xl font-bold text-white">Title</h2>
  <Button className="bg-green-500 hover:bg-green-600">Action</Button>
</div>

// Bad - Messy, hard to read
<div className="flex items-center justify-between p-4 bg-slate-900 rounded-lg border border-slate-800 shadow-lg hover:shadow-xl transition-shadow duration-200">
```

**Key Points:**
- Use Tailwind utility classes
- Group related classes together
- Use semantic spacing (p-4, mx-2, etc.)
- Prefer Tailwind over custom CSS
- Use CSS modules for component-specific styles
- Follow mobile-first responsive design

## Testing Guidelines

### Backend Tests

```python
# tests/test_meme_api.py
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_create_meme():
    """Test meme creation endpoint"""
    meme_data = {
        "title": "Test Meme",
        "canvas_data": {},
        "thumbnail_url": "data:image/png;base64,test",
        "tags": ["test"]
    }
    
    response = client.post(
        "/api/memes",
        json=meme_data,
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "Test Meme"

def test_list_memes():
    """Test meme listing endpoint"""
    response = client.get(
        "/api/memes",
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Frontend Tests

```javascript
// MemeCard.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import MemeCard from './MemeCard';

describe('MemeCard', () => {
  const mockMeme = {
    id: '1',
    title: 'Test Meme',
    thumbnail_url: 'test.jpg'
  };

  it('renders meme title', () => {
    render(<MemeCard meme={mockMeme} />);
    expect(screen.getByText('Test Meme')).toBeInTheDocument();
  });

  it('calls onEdit when edit button clicked', () => {
    const onEdit = jest.fn();
    render(<MemeCard meme={mockMeme} onEdit={onEdit} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    expect(onEdit).toHaveBeenCalledWith('1');
  });
});
```

## Documentation

### Code Comments

```python
# Good - Explain WHY, not WHAT
# Calculate viral score using engagement velocity and share ratio
# Higher values indicate more potential for viral spread
viral_score = (engagement_velocity * 0.6) + (share_ratio * 0.4)

# Bad - States the obvious
# Set viral score to calculation result
viral_score = (engagement_velocity * 0.6) + (share_ratio * 0.4)
```

### API Documentation

When adding new API endpoints, document them:

```python
@api_router.post("/memes", response_model=MemeResponse, tags=["Memes"])
async def create_meme(
    meme_data: MemeCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new meme.
    
    Args:
        meme_data: Meme creation data including title, canvas data, thumbnail
        current_user: Authenticated user from JWT token
        
    Returns:
        Created meme with generated ID and timestamps
        
    Raises:
        HTTPException: 401 if user not authenticated
        HTTPException: 400 if meme data invalid
        
    Example:
        ```json
        {
            "title": "My Meme",
            "canvas_data": {...},
            "thumbnail_url": "data:image/png;base64,...",
            "tags": ["funny", "relatable"]
        }
        ```
    """
    # Implementation
```

## Review Process

1. **Self Review**
   - Review your own code before submitting
   - Check for typos and formatting
   - Ensure tests pass
   - Update documentation

2. **Pull Request**
   - Fill out the PR template completely
   - Link related issues
   - Add screenshots for UI changes
   - Request review from maintainers

3. **Code Review**
   - Address all review comments
   - Push changes to same branch
   - Re-request review after changes

4. **Merge**
   - Squash commits if requested
   - Delete branch after merge

## Questions?

Feel free to:
- Open an issue for discussion
- Join our Discord community
- Email us at support@memecraft.pro

## Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Mentioned in release notes
- Eligible for contributor badges

Thank you for contributing to MemeCraft Pro! 🎉
