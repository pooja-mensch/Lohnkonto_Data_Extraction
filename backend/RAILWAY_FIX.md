# Railway Deployment Fix - Java Not Found

## Problem
```
Error: [Errno 2] No such file or directory: 'java'
```

Railway deployment is not installing Java, causing the JAR processor to fail.

## Solutions (Try in Order)

### Solution 1: Force Dockerfile Deployment (Recommended)

Railway should automatically detect the Dockerfile and use it instead of Nixpacks.

**Steps:**

1. **In Railway Dashboard:**
   - Go to your backend service
   - Click **Settings** → **Deploy**
   - Under "Builder", ensure it's set to **Dockerfile** (not Nixpacks)
   - Click **Deploy** to redeploy

2. **If Builder option isn't available:**
   - Go to **Settings** → **General**
   - Delete the service
   - Create new service from GitHub repo
   - Select `backend` directory
   - Railway will auto-detect Dockerfile

### Solution 2: Use nixpacks.json

Some Railway versions prefer JSON format.

**File created:** `nixpacks.json`

**Steps:**

1. Push the new `nixpacks.json` to your repository
2. In Railway, trigger a new deployment
3. Railway should now use the JSON configuration

### Solution 3: Set Environment Variables

Force Railway to use specific build configuration.

**In Railway Dashboard, add these variables:**

```env
NIXPACKS_PKGS=python311 openjdk17
NIXPACKS_PYTHON_VERSION=3.11
```

Then redeploy.

### Solution 4: Use Railway Template

Use Railway's template system for proper detection.

**Steps:**

1. Create a file `railway.toml` in backend directory (already created)
2. Ensure it contains:
   ```toml
   [build]
   builder = "DOCKERFILE"
   ```
3. Push and redeploy

### Solution 5: Manual Railway CLI Deployment

Force the builder via CLI.

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Deploy with Dockerfile
railway up --detach
```

## Verify Java Installation

After deploying, check the `/health` endpoint:

```bash
curl https://your-app.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "template_exists": true,
  "template_path": "template.xlsx",
  "java_installed": true,
  "java_version": "openjdk version \"17.0.x\""
}
```

If `java_installed` is `false`, Java is not installed.

## Quick Test Script

Test if Java is available in your Railway deployment:

**Add this temporary endpoint to `api.py`:**

```python
@app.get("/test-java")
async def test_java():
    import subprocess
    try:
        result = subprocess.run(
            ["java", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return {
            "java_available": True,
            "output": result.stderr or result.stdout
        }
    except FileNotFoundError:
        return {
            "java_available": False,
            "error": "Java not found in PATH"
        }
    except Exception as e:
        return {
            "java_available": False,
            "error": str(e)
        }
```

Then visit: `https://your-app.railway.app/test-java`

## Recommended: Use Dockerfile

The most reliable method is to use the Dockerfile, which explicitly installs Java.

**Current Dockerfile includes:**
- Python 3.11
- OpenJDK (Java Runtime)
- All required dependencies

**To force Dockerfile usage:**

1. **Option A - Railway Dashboard:**
   - Settings → Deploy → Builder → Select "Dockerfile"

2. **Option B - Delete nixpacks files:**
   ```bash
   cd backend
   rm nixpacks.toml nixpacks.json
   git commit -m "Force Dockerfile usage"
   git push
   ```
   Railway will then automatically use Dockerfile.

3. **Option C - Add railway.toml:**
   ```toml
   [build]
   builder = "DOCKERFILE"
   ```

## Alternative: Deploy to Different Platform

If Railway continues to have issues, consider these alternatives:

### Render.com (Dockerfile Support)
```bash
# Free tier available
# Good Docker support
# Go to render.com → New → Web Service → Connect GitHub
```

### Fly.io (Excellent Docker Support)
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
cd backend
fly launch
fly deploy
```

### Heroku (Container Registry)
```bash
heroku container:login
heroku create your-app-name
heroku container:push web
heroku container:release web
```

## Debug Logs

Check Railway logs for these indicators:

**Good (Java installed):**
```
Installing nixPkgs: python311 openjdk17
...
Setting up Java...
Java installed successfully
```

**Bad (Java missing):**
```
No Java runtime found
Skipping Java installation
```

## Contact Support

If none of these solutions work:

1. **Railway Discord:** https://discord.gg/railway
2. **Railway Support:** support@railway.app
3. **Include in your message:**
   - Project ID
   - Service name
   - This error: "Java not found"
   - Mention you need Java for JAR execution

## Immediate Workaround

While fixing Railway, you can deploy the backend to another platform:

**Quick Deploy to Render:**
1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repository
4. Select `backend` directory
5. Docker will be auto-detected
6. Deploy

**Estimated time:** 5-10 minutes

Then update your frontend's `VITE_API_URL` to the new Render URL.

---

**Created:** 2025-01-17
**Last Updated:** 2025-01-17
