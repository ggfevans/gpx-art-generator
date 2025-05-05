# Phase 7: Web Interface Prompts

## Step 19: FastAPI Backend

```text
Create FastAPI backend that wraps the CLI tool in web/backend/main.py:

1. Set up FastAPI project structure:
   web/
   ├── backend/
   │   ├── main.py
   │   ├── handlers.py
   │   ├── models.py
   │   └── requirements.txt
   ├── frontend/
   └── docker-compose.yml

2. Create FastAPI application in main.py:
   - Import FastAPI and necessary modules
   - Create app instance with CORS middleware
   - Add static file serving for generated files

3. Create API models in models.py:
   - GPXUploadRequest (file + options)
   - GenerateResponse (files + metadata)
   - Options schema (matching CLI options)

4. Implement main API endpoint in handlers.py:
   @app.post("/api/generate")
   async def generate_artwork(
       file: UploadFile = File(...),
       options: str = Form(...)
   ):
       """Generate artwork from GPX file."""

5. Add CLI integration in handlers.py:
   - Save uploaded file temporarily
   - Build CLI command from options
   - Execute CLI as subprocess
   - Capture output and errors
   - Return generated files

6. Add error handling:
   - Validate file type (.gpx)
   - Check file size limits
   - Handle CLI execution errors
   - Clean up temporary files

7. Create file serving endpoint:
   @app.get("/files/{filename}")
   async def get_file(filename: str):
       """Serve generated artwork files."""

8. Add CORS configuration:
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_methods=["*"],
       allow_headers=["*"],
   )

9. Create backend requirements.txt:
   fastapi>=0.100.0
   uvicorn>=0.23.0
   python-multipart>=0.0.6
   pydantic>=2.0.0

10. Add basic tests for API:
    - Test file upload
    - Test option parsing
    - Test CLI integration
    - Test error responses

Success criteria:
- API accepts GPX files and generates artwork
- Files can be downloaded via API
- Error handling works properly
```

## Step 20: React Frontend Setup

```text
Create React TypeScript frontend in web/frontend/:

1. Initialize React project:
   cd web/frontend
   npm create vite@latest . -- --template react-ts
   
2. Add necessary dependencies:
   npm install @tanstack/react-query axios
   npm install @radix-ui/react-select @radix-ui/react-checkbox
   npm install lucide-react clsx tailwind-merge
   npm install react-dropzone

3. Set up Tailwind CSS:
   npm install -D tailwindcss postcss autoprefixer
   npx tailwindcss init -p

4. Create basic project structure:
   frontend/
   ├── src/
   │   ├── components/
   │   │   ├── ui/
   │   │   └── UploadForm.tsx
   │   ├── lib/
   │   │   ├── api.ts
   │   │   └── types.ts
   │   ├── App.tsx
   │   └── main.tsx
   ├── package.json
   └── tsconfig.json

5. Create TypeScript types in lib/types.ts:
   - GPXOptions interface
   - APIResponse interface
   - FileDownload interface

6. Create API client in lib/api.ts:
   - generateArtwork function
   - downloadFile function
   - Error handling

7. Style the app with Tailwind:
   - Configure tailwind.config.js
   - Update globals.css

8. Create basic App layout:
   - Header with project title
   - Main upload area
   - Footer with links

9. Create tests:
   - Component tests with Vitest
   - API integration tests

Success criteria:
- React app runs without errors
- TypeScript configured properly
- API client functions created
```

## Step 21: Upload UI

```text
Create the upload and options UI in frontend/src/components/UploadForm.tsx:

1. Create file upload component:
   - Use react-dropzone for drag & drop
   - Show file preview and validation
   - Display file size and type

2. Create options form sections:
   - Line styling (color, thickness, style)
   - Distance markers toggle and unit selection
   - Information overlay checkboxes and position
   - Export format selection
   - Dimension settings

3. Add form validation:
   - Validate required fields
   - Check file type (.gpx only)
   - Validate hex color codes
   - Validate numeric inputs

4. Create reusable UI components:
   - ColorPicker component
   - Select component with options
   - Checkbox group component
   - NumberInput component

5. Add form state management:
   - Use React hooks for state
   - Create form context if needed
   - Handle option dependencies

6. Style the form with Tailwind:
   - Clean, modern design
   - Responsive layout
   - Clear visual hierarchy
   - Proper spacing and typography

7. Add accessibility:
   - Proper ARIA labels
   - Keyboard navigation
   - Screen reader support
   - Error announcements

8. Create component tests:
   - Test form submission
   - Test validation logic
   - Test option changes
   - Test file upload

Success criteria:
- Form is intuitive and easy to use
- All CLI options are available
- Validation provides clear feedback
- Design is clean and professional
```

## Step 22: Web Integration

```text
Complete the web application by connecting frontend to backend:

1. Update UploadForm to use API client:
   - Call generateArtwork on form submission
   - Handle loading states
   - Display progress indicator
   - Handle success/error responses

2. Create download interface:
   - Display generated files
   - Create download buttons
   - Show file sizes
   - Add preview images if possible

3. Add error handling:
   - Display API errors to user
   - Provide retry options
   - Show helpful error messages
   - Handle network issues

4. Create notification system:
   - Toast notifications for success/error
   - Loading indicators
   - Progress feedback

5. Add Docker configuration:
   web/Dockerfile:
   - Multi-stage build for frontend
   - Include backend setup
   - Configure nginx for serving

   web/docker-compose.yml:
   - Frontend service
   - Backend service
   - Shared volumes
   - Port mapping

6. Update backend to handle frontend:
   - Serve built frontend files
   - Configure proper routing
   - Add production settings

7. Create end-to-end tests:
   - Test complete workflow
   - Test file download
   - Test error scenarios

8. Add documentation:
   - Web interface usage guide
   - Deployment instructions
   - Docker setup guide

9. Create production build scripts:
   - Build frontend
   - Package with backend
   - Create Docker image

Success criteria:
- Complete workflow works in browser
- Files can be uploaded and downloaded
- Docker deployment works
- Application handles errors gracefully
```