# Path2Work Static Images Documentation

This directory contains the five primary visual assets for the Path2Work web application, plus placeholders and replacement specifications.

## 1. Five Core Images

| Filename | Placement & Role | Aspect Ratio & Crop | Purpose |
|---|---|---|---|
| `path2work-hero.jpg` | Public Landing Page (`/`) Hero Banner | ~16:9 widescreen, subject weighted to right side | Editorial, aspirational hero for South African tech graduates proving their capability |
| `path2work-auth.jpg` | Authentication split panel (`auth/login.html`, `auth/register.html`) | ~3:4 or 4:5 vertical portrait | Professional, relatable portrait of an early-career IT candidate |
| `path2work-pathway-support.jpg` | Candidate Dashboard / Pathway Card: Cloud & IT Support | ~16:10 or 3:2 landscape | Hands-on IT infrastructure and systems diagnosis |
| `path2work-pathway-development.jpg` | Candidate Dashboard / Pathway Card: Software Engineering | ~16:10 or 3:2 landscape | Modern software development and engineering workflow |
| `path2work-employer-talent.jpg` | Employer Talent Pipeline (`/employer/dashboard`) & Evidence Review | ~16:9 or 3:2 landscape | Tech team collaboration and talent discovery for recruiters/engineering leaders |

## 2. Image Standards & Guidelines
- **Current format:** The canonical assets in use are `.jpg` files. The repository also contains same-content `.webp`-named aliases; the templates use the `.jpg` names so file extensions are consistent with the source assets.
- **Visual Tone:** Authentic, professional, natural lighting, contemporary South African tech ecosystem
- **Typography/Overlays:** No baked-in text, logos, or artificial device mockups in the source images
- **Fallback:** If an image is unavailable or loading fails, all templates include graceful CSS background gradients and accessible alt text.

## 3. Placeholder Slots for Future Expansion
When adding additional pathway images or employer marketing visuals, use correctly encoded files and follow the naming convention below:
- `path2work-pathway-data.webp` — Junior Data Analyst pathway card
- `path2work-pathway-cybersecurity.webp` — Cybersecurity pathway card
- `path2work-pathway-qa.webp` — Quality Assurance & Testing pathway card
- `path2work-passport-badge.webp` — Special verification seal graphic
- `path2work-employer-banner.webp` — Employer hiring campaign banner
