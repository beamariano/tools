# Tests for Image and Video Processing Tools

This directory contains comprehensive tests for all Python modules in the tools package.

## Running Tests

### Install pytest
```bash
pip install pytest pytest-cov
```

### Run all tests
```bash
cd /Users/b/tools
pytest tests/
```

### Run with coverage report
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_constants.py
pytest tests/test_messages.py
pytest tests/test_format_utils.py
```

### Run with verbose output
```bash
pytest tests/ -v
```

## Test Files

- `test_constants.py` - Tests for constants module (enums, sets, helper functions)
- `test_messages.py` - Tests for message handling and formatting
- `test_format_utils.py` - Tests for format detection and conversion logic
- `test_change_video_duration.py` - Tests for video duration adjustment functions
- `conftest.py` - Shared pytest fixtures and configuration

## Test Coverage

The test suite covers:

### constants.py
- ✓ All enum definitions (ImageFormat, VideoFormat, VideoCodec)
- ✓ File extension sets and mappings
- ✓ Format category classification (lossy, lossless, transparency, animation)
- ✓ Quality recommendations and defaults
- ✓ Helper functions (is_image_file, is_video_file, supports_transparency, is_lossy_format)
- ✓ Default folder paths and legacy aliases

### messages.py
- ✓ MessageHandler class (error, success, warning, info methods)
- ✓ Custom exception classes (ToolException, FileNotFoundError, etc.)
- ✓ Format conversion message functions
- ✓ Video processing message functions
- ✓ Folder management message functions
- ✓ Message formatting with and without colors

### format_utils.py
- ✓ Format detection from filenames
- ✓ Extension lookup for formats
- ✓ Quality recommendations by format and use case
- ✓ Format conversion analysis (transparency loss, quality loss)
- ✓ Optimal output format selection
- ✓ Comprehensive format information

### change_video_duration.py
- ✓ Folder existence checking and creation
- ✓ Video file discovery
- ✓ Fade effect application
- ✓ User input handling (float and yes/no inputs)

## Notes

- Tests use mocking for external dependencies (cv2, moviepy, PIL) to avoid requiring actual media files
- Temporary directories are created and cleaned up automatically using pytest fixtures
- Tests are designed to be fast and not require external resources
- All tests follow pytest conventions and best practices

## Future Enhancements

Additional tests could be added for:
- `image_to_video.py` - Complete image-to-video conversion with MoviePy mocking
- `optimize_images.py` - Image optimization with PIL mocking
- `image_to_c-array.py` - C array generation from images
- Integration tests with actual small media files
- Performance benchmarks
