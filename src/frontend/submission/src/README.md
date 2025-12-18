# Submission Interface Source Code

React/TypeScript implementation of the Syntheverse contribution submission interface.

## Overview

This directory contains the frontend implementation for user contribution submissions, providing an intuitive interface for uploading research, documentation, and other materials for PoC evaluation.

## Component Architecture

### Submission Components
- **FileUpload.tsx**: Drag-and-drop file upload with progress indication
- **SubmissionForm.tsx**: Contribution metadata and description input
- **ValidationDisplay.tsx**: Real-time form validation and error feedback
- **ProgressTracker.tsx**: Submission status and evaluation progress

### Preview Components
- **FilePreview.tsx**: Uploaded file content preview and editing
- **MetadataEditor.tsx**: Contribution metadata editing interface
- **TagSelector.tsx**: Research domain and topic tagging system
- **LicenseSelector.tsx**: Content licensing and attribution options

## State Management

### Submission State
```typescript
interface SubmissionState {
  files: File[];
  metadata: {
    title: string;
    description: string;
    authors: string[];
    tags: string[];
    license: string;
  };
  validation: {
    isValid: boolean;
    errors: ValidationError[];
  };
  status: 'idle' | 'uploading' | 'processing' | 'submitted' | 'error';
  progress: {
    uploaded: number;
    total: number;
    percentage: number;
  };
}
```

### Custom Hooks
```typescript
const useFileUpload = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [progress, setProgress] = useState<UploadProgress>({});

  const uploadFiles = async (fileList: FileList) => {
    const uploadPromises = Array.from(fileList).map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
        onUploadProgress: (progressEvent) => {
          setProgress(prev => ({
            ...prev,
            [file.name]: {
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percentage: Math.round((progressEvent.loaded * 100) / progressEvent.total)
            }
          }));
        }
      });

      return response.json();
    });

    const results = await Promise.all(uploadPromises);
    setFiles(prev => [...prev, ...results]);
  };

  return { files, progress, uploadFiles };
};
```

## File Handling

### Upload Configuration
```typescript
const UPLOAD_CONFIG = {
  maxFileSize: 100 * 1024 * 1024, // 100MB
  allowedTypes: [
    'application/pdf',
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/zip',
    'application/x-tar'
  ],
  maxFiles: 10,
  chunkSize: 1024 * 1024 // 1MB chunks for large files
};
```

### Validation Logic
```typescript
const validateSubmission = (submission: SubmissionData): ValidationResult => {
  const errors: string[] = [];

  // File validation
  if (submission.files.length === 0) {
    errors.push('At least one file is required');
  }

  if (submission.files.some(file => file.size > UPLOAD_CONFIG.maxFileSize)) {
    errors.push(`Files must be smaller than ${UPLOAD_CONFIG.maxFileSize / (1024 * 1024)}MB`);
  }

  // Metadata validation
  if (!submission.metadata.title.trim()) {
    errors.push('Title is required');
  }

  if (!submission.metadata.description.trim()) {
    errors.push('Description is required');
  }

  if (submission.metadata.tags.length === 0) {
    errors.push('At least one tag is required');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
};
```

## API Integration

### Submission API
```typescript
class SubmissionAPI {
  async uploadFile(file: File): Promise<UploadResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    return response.json();
  }

  async submitContribution(data: SubmissionData): Promise<SubmissionResult> {
    const response = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`Submission failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getSubmissionStatus(submissionId: string): Promise<SubmissionStatus> {
    const response = await fetch(`/api/submission/${submissionId}/status`);
    return response.json();
  }
}

export const submissionAPI = new SubmissionAPI();
```

## User Experience Features

### Progressive Enhancement
- **Basic Form**: Functional without JavaScript
- **Enhanced UX**: Drag-and-drop, progress indicators with JavaScript
- **Accessibility**: Screen reader support, keyboard navigation

### Real-time Feedback
- **Upload Progress**: Visual progress bars and percentage indicators
- **Validation Messages**: Immediate feedback on form errors
- **Status Updates**: Live updates on submission processing status

## Development

### Component Testing
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FileUpload } from './FileUpload';

test('handles file upload', async () => {
  const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });

  render(<FileUpload onUpload={jest.fn()} />);

  const input = screen.getByTestId('file-input');
  fireEvent.change(input, { target: { files: [mockFile] } });

  await waitFor(() => {
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
  });
});
```

### Integration Testing
```typescript
test('complete submission workflow', async () => {
  render(<SubmissionWizard />);

  // Step 1: File upload
  const fileInput = screen.getByTestId('file-input');
  fireEvent.change(fileInput, { target: { files: [testFile] } });

  // Step 2: Metadata entry
  const titleInput = screen.getByLabelText('Title');
  fireEvent.change(titleInput, { target: { value: 'Test Contribution' } });

  // Step 3: Submission
  const submitButton = screen.getByText('Submit Contribution');
  fireEvent.click(submitButton);

  await waitFor(() => {
    expect(screen.getByText('Submission successful!')).toBeInTheDocument();
  });
});
```

## Documentation

- [AGENTS.md](AGENTS.md) - Detailed component documentation
- [FRACTAL.md](FRACTAL.md) - Fractal analysis and patterns
- [Submission Interface](../../AGENTS.md) - Interface overview documentation
