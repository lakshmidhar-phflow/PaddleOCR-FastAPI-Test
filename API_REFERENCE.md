# OCR API Quick Reference

## Base URL
```
http://localhost:8080
```

## Endpoints

### OCR Processing
```
POST /ocr/
```

### Request Headers
```
accept: application/json
Content-Type: multipart/form-data
```

### Request Body
```
file: <image_file> (required)
```

### Response
```json
{
    "device": "gpu:0",
    "results": [
        {
            "text": "Extracted text",
            "confidence": 0.995,
            "bounding_box": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        }
    ],
    "total_text_regions": 1
}
```

## cURL Examples

### Basic Usage
```bash
curl -X POST 'http://localhost:8080/ocr/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@invoice.jpg;type=image/jpeg'
```

### With PNG File
```bash
curl -X POST 'http://localhost:8080/ocr/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@document.png;type=image/png'
```

### Save Response to File
```bash
curl -X POST 'http://localhost:8080/ocr/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@invoice.jpg;type=image/jpeg' \
  -o ocr_results.json
```

## Python Examples

### Using requests
```python
import requests

url = 'http://localhost:8080/ocr/'
with open('invoice.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)
    results = response.json()

    print(f"Device: {results['device']}")
    print(f"Total regions: {results['total_text_regions']}")

    for item in results['results']:
        print(f"Text: {item['text']}")
        print(f"Confidence: {item['confidence']}")
        print(f"Box: {item['bounding_box']}")
        print("---")
```

### Batch Processing
```python
import requests
import os

def process_image(image_path):
    url = 'http://localhost:8080/ocr/'
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
        return response.json()

# Process all images in directory
image_dir = 'images/'
for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        image_path = os.path.join(image_dir, filename)
        results = process_image(image_path)
        print(f"Processed {filename}: {results['total_text_regions']} text regions found")
```

## Response Fields Reference

### Device
- **Type**: String
- **Values**: "gpu:0", "cpu", "unknown"
- **Description**: Processing device used for OCR

### Results Array
- **Type**: Array of objects
- **Description**: List of detected text regions

#### Text Object Fields
- **text** (string): Recognized text content
- **confidence** (float): Confidence score (0.0 - 1.0)
- **bounding_box** (array): Four corner coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

### Total Text Regions
- **Type**: Integer
- **Description**: Total number of text regions detected

## Error Responses

### File Not Provided
```json
{
    "detail": [
        {
            "loc": ["body", "file"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

### Processing Error
```json
{
    "error": "Error processing result: [error details]",
    "results": [
        {
            "text": "Error processing result: [error details]",
            "confidence": 0.0,
            "bounding_box": []
        }
    ],
    "total_text_regions": 1
}
```

## Supported Image Formats

| Format | Extensions | Notes |
|--------|------------|-------|
| JPEG | .jpg, .jpeg | Recommended for photos |
| PNG | .png | Supports transparency |
| BMP | .bmp | Uncompressed format |
| TIFF | .tiff, .tif | High quality, large files |

## Performance Tips

1. **Image Size**: Optimal range 500x500 to 4000x4000 pixels
2. **File Size**: Keep under 10MB for best performance
3. **Text Quality**: Clear, high-contrast text works best
4. **Batch Requests**: Process 5-10 images sequentially for best throughput

## Troubleshooting

### Common HTTP Status Codes
- **200**: Success
- **400**: Bad request (missing file, invalid format)
- **422**: Validation error
- **500**: Internal server error

### Debug Commands
```bash
# Check if server is running
curl http://localhost:8080/docs

# Check container logs
docker logs loving_rhodes --tail 20

# Test with sample image
curl -X POST 'http://localhost:8080/ocr/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@images/aug_035.jpg;type=image/jpeg' | python -m json.tool
```

## Integration Examples

### Node.js
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('invoice.jpg'));

axios.post('http://localhost:8080/ocr/', form, {
  headers: {
    ...form.getHeaders()
  }
})
.then(response => {
  console.log('OCR Results:', response.data);
})
.catch(error => {
  console.error('Error:', error.message);
});
```

### JavaScript (Browser)
```html
<script>
async function processImage(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8080/ocr/', {
    method: 'POST',
    body: formData
  });

  const results = await response.json();
  console.log('OCR Results:', results);
  return results;
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    processImage(file);
  }
});
</script>
```

---

**Quick Test Command**:
```bash
curl -X POST 'http://localhost:8080/ocr/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@images/aug_035.jpg;type=image/jpeg'
```