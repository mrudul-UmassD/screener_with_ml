# 🌐 Web Frontend Guide

## Quick Start

The Resume Screener now includes a modern, interactive web interface!

### Starting the Application

```powershell
python app_simple.py
```

Then open your browser to: **http://localhost:5000**

## Features

### 🎨 Modern UI
- Clean, professional design
- Responsive layout (works on mobile)
- Real-time statistics dashboard
- Interactive candidate cards

### 📊 Three Main Sections

#### 1. Upload Data
- **Upload Resumes**: Add candidate resumes with automatic skill extraction
- **Upload Jobs**: Post job descriptions with requirement parsing

#### 2. Screen Candidates
- Select a job posting
- Click "Start Screening" to rank all candidates
- ML algorithms calculate:
  - Skill match scores
  - Semantic similarity
  - Experience scores
  - Overall rankings

#### 3. View Results
- See ranked candidates for each job
- Color-coded score visualizations
- Matched skills display
- Contact information
- Export-ready data

## API Endpoints Used

The frontend communicates with these endpoints:

- `GET /` - Web interface
- `GET /api/health` - Health check
- `GET /api/stats` - Dashboard statistics
- `POST /api/upload/resume` - Upload resume
- `POST /api/upload/job` - Upload job
- `POST /api/screen` - Run screening
- `GET /api/results/<job_id>` - Get results

## Sample Workflow

1. **Upload a Job Description**
   - Go to "Upload Data" tab
   - Fill in job title and description
   - System extracts required skills automatically

2. **Upload Candidate Resumes**
   - Same tab, left panel
   - Add candidate name and resume content
   - System extracts skills and experience

3. **Screen Candidates**
   - Go to "Screen Candidates" tab
   - Select your job from dropdown
   - Click "Start Screening"
   - Wait for ML processing (may take 10-30 seconds)

4. **View Rankings**
   - Automatically redirected to results
   - See candidates ranked by match score
   - Top 3 candidates highlighted with gold badge
   - View detailed score breakdowns

## Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS Grid/Flexbox
- **Vanilla JavaScript** - No frameworks, lightweight
- **Fetch API** - RESTful communication

### Backend
- **Flask** - Web server
- **Flask-CORS** - Cross-origin support
- **Jinja2** - Template engine

## Customization

### Colors
Edit `static/css/style.css` and modify CSS variables:
```css
:root {
    --primary: #4F46E5;  /* Main brand color */
    --success: #10B981;  /* Success states */
    --danger: #EF4444;   /* Error states */
}
```

### Scoring Weights
Edit `config.py`:
```python
WEIGHTS = {
    'skill_match': 0.4,         # 40% weight on skills
    'semantic_similarity': 0.4,  # 40% weight on semantic match
    'experience': 0.2            # 20% weight on experience
}
```

## Screenshots

### Dashboard
- Real-time statistics
- Total jobs, resumes, screenings

### Upload Interface
- Split-panel design
- Resume and job upload forms
- Instant skill extraction feedback

### Results View
- Ranked candidate cards
- Score visualizations
- Matched skills display
- Top performers highlighted

## Browser Compatibility

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+

## Development

### File Structure
```
Resume Screener/
├── templates/
│   └── index.html          # Main frontend
├── static/
│   ├── css/
│   │   └── style.css       # Styles
│   └── js/
│       └── app.js          # Frontend logic
├── app_simple.py           # Simplified launcher
└── src/
    └── api.py              # API routes
```

### Adding Features

1. **New API Endpoint**: Add route in `app_simple.py`
2. **New UI Section**: Add tab in `templates/index.html`
3. **New Styles**: Add to `static/css/style.css`
4. **New Logic**: Add to `static/js/app.js`

## Troubleshooting

### Port Already in Use
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <process_id> /F
```

### CORS Errors
- Ensure Flask-CORS is installed
- Check browser console for specific errors
- Verify API URL in `static/js/app.js`

### Slow Screening
- First screening loads the embedding model (10-20 seconds)
- Subsequent screenings are faster
- Large candidate pools take longer

## Production Deployment

For production use:

```powershell
# Install gunicorn
pip install gunicorn

# Run with production server
gunicorn -w 4 -b 0.0.0.0:5000 app_simple:app
```

Or use Docker, Heroku, AWS, etc.

## Next Steps

- Add user authentication
- Implement data visualization charts
- Add export to PDF/Excel
- Enable batch resume upload
- Add candidate comparison view
- Implement search and filters

---

**Enjoy your AI-powered Resume Screener! 🚀**
