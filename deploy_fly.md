# 🆓 Deploy to Fly.io (FREE Alternative)

Fly.io offers a generous free tier that's perfect for testing your app.

## Free Tier Includes:
- **3 shared-cpu-1x VMs** (256MB RAM each)
- **3GB persistent volume storage**
- **160GB outbound data transfer**
- **No sleep mode** (unlike Render)

## Step 1: Install Fly CLI

```bash
# macOS
brew install flyctl

# Or download from: https://fly.io/docs/getting-started/installing-flyctl/
```

## Step 2: Setup Fly.io

```bash
cd content-creation/quote_speak_app_deploy

# Login to Fly.io
flyctl auth signup  # or flyctl auth login

# Initialize your app
flyctl launch
```

When prompted:
- **App name**: `quote-speak-app-yourname`
- **Region**: Choose closest to you
- **Add a PostgreSQL database**: `No`
- **Add a Redis database**: `No`
- **Deploy now**: `No` (we'll set env vars first)

## Step 3: Configure Environment

```bash
# Set environment variables
flyctl secrets set OPENAI_API_KEY="sk-your-actual-key"
flyctl secrets set SECRET_KEY="your-random-secret-key"
flyctl secrets set FLASK_ENV="production"
flyctl secrets set MAX_TEXT_LENGTH="2000"
flyctl secrets set MAX_TITLE_LENGTH="100"

# Optional: Add other API keys
flyctl secrets set ELEVENLABS_API_KEY="your-elevenlabs-key"
```

## Step 4: Create Fly Configuration

The `flyctl launch` command should have created a `fly.toml` file. If not, create it:

```toml
# fly.toml
app = "quote-speak-app-yourname"
primary_region = "sjc"

[build]

[http_service]
  internal_port = 5000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

[env]
  PORT = "5000"
  FLASK_ENV = "production"
```

## Step 5: Deploy

```bash
# Deploy your app
flyctl deploy

# Check status
flyctl status

# View logs
flyctl logs
```

## Step 6: Access Your App

Your app will be available at:
`https://quote-speak-app-yourname.fly.dev`

## 🎯 Fly.io Advantages

✅ **No sleep mode** (unlike Render free tier)  
✅ **Better performance** (dedicated resources)  
✅ **Global edge locations**  
✅ **Automatic HTTPS**  
✅ **Easy scaling**  

## 💡 Free Tier Tips

1. **Monitor Usage**:
```bash
flyctl dashboard
```

2. **Scale Down When Not Needed**:
```bash
flyctl scale count 0  # Stop all machines
flyctl scale count 1  # Start one machine
```

3. **Check Billing**:
```bash
flyctl dashboard billing
```

## 🔧 Troubleshooting

**Deployment Failed:**
```bash
flyctl logs
# Check for missing dependencies or env vars
```

**Out of Memory:**
```bash
# Increase memory (may cost extra)
flyctl scale memory 512
```

**App Not Responding:**
```bash
flyctl status
flyctl logs --follow
```

## 📊 Cost Monitoring

Free tier limits:
- **Compute**: 2,340 hours/month (3 VMs × 780 hours)
- **Bandwidth**: 160GB outbound
- **Storage**: 3GB persistent volumes

Monitor usage:
```bash
flyctl dashboard billing
```

## 🚀 Success!

Your app is now running on Fly.io for free! The main advantages over Render:
- No sleep mode
- Better performance
- More generous free tier
- Professional infrastructure