# PineCraft AI Landing Page Setup Guide

Welcome! This guide will help you set up your landing page with email capture and analytics. No coding experience needed!

## 🚀 Quick Start

### Step 1: View Your Landing Page
```bash
open pinecraft-landing-page.html
```

### Step 2: Set Up Email Capture (Choose ONE option)

#### Option A: Tally Forms (EASIEST - Recommended for beginners!)
1. Go to [tally.so](https://tally.so)
2. Click "Start for free"
3. Choose "Create from scratch"
4. Add an "Email" field
5. Customize the button text to "Get Early Access"
6. Click "Publish" → "Share" → "Embed on website"
7. Copy the embed code
8. In your landing page file, find this comment:
   ```html
   <!-- Simple form placeholder - Replace with your email service -->
   ```
9. Replace the entire `<form>` section with your Tally embed code

#### Option B: ConvertKit (Good for creators)
1. Sign up at [convertkit.com](https://convertkit.com)
2. Go to "Forms" → "Create New"
3. Choose "Inline" form type
4. Design your form (keep it simple!)
5. Click "Embed"
6. Copy the HTML code
7. Replace the form in your landing page

#### Option C: Mailchimp (Popular choice)
1. Sign up at [mailchimp.com](https://mailchimp.com)
2. Go to "Audience" → "Signup forms"
3. Choose "Embedded forms"
4. Customize and copy the code
5. Replace the form in your landing page

### Step 3: Add Microsoft Clarity Analytics

1. Go to [clarity.microsoft.com](https://clarity.microsoft.com)
2. Sign in with your Microsoft account (or create one - it's free!)
3. Click "New project"
4. Enter your website name: "PineCraft AI"
5. Choose "E-commerce" as your category
6. Click "Create"
7. You'll see a code snippet that looks like this:
   ```javascript
   (function(c,l,a,r,i,t,y){
       c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
       t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
       y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
   })(window, document, "clarity", "script", "YOUR-PROJECT-ID");
   ```
8. Copy this code
9. In your landing page, find this comment:
   ```html
   <!-- Microsoft Clarity - Add your tracking code here -->
   ```
10. Paste your code right after this comment

## 📝 Customizing Your Landing Page

### Changing Text
- Open `pinecraft-landing-page.html` in any text editor
- Find the text you want to change
- Replace it with your new text
- Save the file

### Changing Colors
All colors are defined in your `pinecraft-styles.css` file. The main colors are:
- Blue: `#00D9FF`
- Orange: `#FF9F00`
- Dark background: `#0A0E1A`

### Changing the Logo
The logo appears in two places:
1. Hero section (top)
2. Footer (bottom)

Just make sure the path points to your logo file:
```html
<img src="../PineCraft AI Branding/pinecraft-ai-logo.svg" alt="PineCraft AI Logo">
```

## 🌐 Making It Live

To put your landing page online, you'll need web hosting. Here are beginner-friendly options:

### Option 1: Netlify (FREE & EASY)
1. Go to [netlify.com](https://netlify.com)
2. Sign up for free
3. Drag your entire project folder onto the Netlify dashboard
4. Your site will be live in seconds!

### Option 2: GitHub Pages (FREE)
1. Create a [GitHub](https://github.com) account
2. Create a new repository
3. Upload your files
4. Go to Settings → Pages → Enable GitHub Pages

### Option 3: Traditional Hosting
Use services like:
- Hostinger
- Bluehost
- GoDaddy
Upload your files via FTP or their file manager

## 📊 Understanding Your Analytics

Once Microsoft Clarity is set up, you can see:
- Where people click most (heatmaps)
- How far they scroll
- Where they get confused
- Session recordings of real users

This helps you improve your landing page based on real data!

## ❓ Troubleshooting

### Images not showing?
Check that the file paths are correct. The logo path should match where you put the files.

### Form not working?
Make sure you've replaced the placeholder form with a real email service form.

### Page looks broken?
Ensure the CSS file path is correct:
```html
<link rel="stylesheet" href="../PineCraft AI Branding/pinecraft-styles.css">
```

## 🎉 You're Done!

Your landing page is now ready to:
- Capture emails
- Track visitor behavior
- Convert visitors into customers

Remember: The page already matches your PineCraft AI branding with the Tron Legacy theme!

Need help? The landing page is designed to work right out of the box. Just add your email form and analytics, and you're good to go! 