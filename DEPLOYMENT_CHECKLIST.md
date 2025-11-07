# OCR System Deployment Checklist

## Pre-Deployment Checklist

### Environment Requirements
- [ ] Docker installed and running
- [ ] NVIDIA Docker runtime (for GPU support)
- [ ] Port 8080 available
- [ ] Minimum 4GB RAM available
- [ ] Minimum 10GB disk space available

### System Verification
```bash
# Check Docker
docker --version
docker info

# Check GPU (if using GPU)
nvidia-smi

# Check available memory
free -h  # Linux
# or
systeminfo | findstr /C:"Total Physical Memory"  # Windows
```

## Deployment Steps

### 1. Container Setup
```bash
# Check if container exists
docker ps -a | grep paddleocr

# Start existing container (recommended)
docker start loving_rhodes

# OR create new container
docker run -d -p 8080:8080 --name ocr-container paddleocr-api
```

### 2. Application Deployment
```bash
# Copy updated app.py to container
docker cp app.py loving_rhodes:/app/app.py

# Restart container to apply changes
docker restart loving_rhodes

# Wait for startup (10-15 seconds)
sleep 15
```

### 3. Health Check
```bash
# Check container status
docker ps | grep loving_rhodes

# Check logs for errors
docker logs loving_rhodes --tail 10

# Test API endpoint
curl -f http://localhost:8080/docs
```

### 4. Functional Testing
```bash
# Test with sample image
curl -X POST 'http://localhost:8080/ocr/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@images/aug_035.jpg;type=image/jpeg' | python -m json.tool

# Verify response structure
# Should contain: device, results, total_text_regions
```

## Post-Deployment Verification

### API Response Validation
- [ ] Status code 200 for valid requests
- [ ] JSON response with expected structure
- [ ] Text extraction working correctly
- [ ] Confidence scores present (0.0-1.0)
- [ ] Bounding box coordinates present
- [ ] Device information included

### Performance Verification
- [ ] Response time under 15 seconds for large images
- [ ] Memory usage stable
- [ ] No error logs in container
- [ ] Concurrent request handling

### Error Handling Testing
- [ ] Missing file returns proper error
- [ ] Invalid file format handled gracefully
- [ ] Large file size handled appropriately
- [ ] Network errors handled properly

## Production Configuration

### Security Setup
```bash
# Set up API key authentication (future)
# Configure rate limiting
# Set up HTTPS (production)
# Configure firewall rules
```

### Monitoring Setup
```bash
# Set up log rotation
docker run --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  ocr-container

# Set up health monitoring
curl -f http://localhost:8080/docs || echo "Health check failed"
```

### Backup Strategy
- [ ] Container image backup
- [ ] Configuration backup (app.py)
- [ ] Log backup strategy
- [ ] Disaster recovery plan

## Troubleshooting Guide

### Container Won't Start
```bash
# Check Docker daemon
docker info

# Check port conflicts
netstat -tulpn | grep 8080

# Check GPU availability
nvidia-smi

# View detailed logs
docker logs loving_rhodes
```

### API Returns Empty Results
```bash
# Check OCR processing
docker logs loving_rhodes --tail 20

# Verify image format
file images/aug_035.jpg

# Test with different image
curl -X POST 'http://localhost:8080/ocr/' \
  -F 'file=@other_image.jpg'
```

### Performance Issues
```bash
# Check resource usage
docker stats loving_rhodes

# Check system memory
free -h

# Monitor GPU usage (if applicable)
nvidia-smi -l 1
```

### Memory Issues
```bash
# Check container memory usage
docker stats --no-stream loving_rhodes

# Restart container if memory leak suspected
docker restart loving_rhodes

# Monitor system memory
watch -n 1 free -h
```

## Maintenance Tasks

### Daily
- [ ] Check container status
- [ ] Review error logs
- [ ] Monitor resource usage
- [ ] Verify API responsiveness

### Weekly
- [ ] Update Docker images
- [ ] Clean up unused containers/images
- [ ] Review performance metrics
- [ ] Backup configuration files

### Monthly
- [ ] Security updates
- [ ] Performance optimization
- [ ] Capacity planning
- [ ] Documentation updates

## Scaling Considerations

### Horizontal Scaling
```bash
# Run multiple instances
docker run -d -p 8081:8080 --name ocr-container-2 paddleocr-api
docker run -d -p 8082:8080 --name ocr-container-3 paddleocr-api

# Set up load balancer (nginx/HAProxy)
```

### Resource Scaling
- [ ] Monitor CPU usage trends
- [ ] Monitor memory usage trends
- [ ] Plan GPU capacity
- [ ] Disk space planning

## Rollback Procedure

### Quick Rollback
```bash
# Stop problematic container
docker stop loving_rhodes

# Start previous version (if available)
docker start loving_rhodes_backup

# Restore previous app.py
docker cp app.py.backup loving_rhodes:/app/app.py
docker restart loving_rhodes
```

### Complete Reset
```bash
# Remove container
docker stop loving_rhodes
docker rm loving_rhodes

# Pull fresh image
docker pull paddleocr-api

# Create new container
docker run -d -p 8080:8080 --name loving_rhodes paddleocr-api

# Deploy current app.py
docker cp app.py loving_rhodes:/app/app.py
docker restart loving_rhodes
```

## Performance Benchmarks

### Test Images
- **Small** (500x500, 50KB): ~2 seconds
- **Medium** (2000x2000, 1MB): ~5 seconds
- **Large** (4000x4000, 5MB): ~15 seconds

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Load test (10 concurrent requests, 100 total)
ab -n 100 -c 10 -p test_image.jpg -T multipart/form-data http://localhost:8080/ocr/
```

## Contact Information

### Support Channels
- **Container Issues**: Check Docker logs
- **API Issues**: Review FastAPI logs
- **Performance Issues**: Monitor resource usage
- **Documentation**: Check README.md and IMPLEMENTATION_GUIDE.md

### Emergency Contacts
- **System Administrator**: [Contact Info]
- **Development Team**: [Contact Info]
- **Infrastructure Team**: [Contact Info]

---

## Deployment Summary

**Completed Checklist Items**: [ ] / [ ]
**Deployment Date**: ___________
**Deployed By**: ___________
**Version**: 1.0
**Status**: [ ] Success [ ] Partial Success [ ] Failed

**Notes**:
_________________________________________________________
_________________________________________________________
_________________________________________________________

**Next Review Date**: ___________