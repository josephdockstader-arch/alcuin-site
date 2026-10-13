# Privacy page — drafted 2026-09-10 per Joseph's Q9 answer (audit fixes).
# Awaiting his read; edit any line, rerun python3 ../build_redesign.py.
#
# CORRECTED 2026-09-18, the day the site went live. The first sentence
# said "does not use analytics, advertising, or tracking of any kind."
# That was written before deploy and became false the moment it shipped:
# Cloudflare injects a Real User Monitoring beacon server-side, so it is
# invisible in the built HTML and only shows up in a browser's network
# tab. Every page load fires POST /cdn-cgi/rum.
# Joseph's call was to keep the analytics and state it plainly. The
# replacement says what happens and stops -- no paragraph explaining how
# privacy-conscious the choice is. On a site that sells data-handling
# judgment to schools, this is the most checkable claim on it.
# IF THE CLOUDFLARE SETTING IS EVER TURNED OFF, this sentence has to
# change back. Check before assuming either version is current.

## browser-title
Privacy | The Alcuin Project

## meta-description
How The Alcuin Project handles information visitors share through this site: what we collect through the contact form and newsletter, and what we do not.

## hero-h1
Privacy

## body
This site counts page views through Cloudflare. That count stores nothing in your browser and is not tied to you. There is no advertising. The one thing stored in your browser is a session marker that remembers a completed booking form during your visit, and it disappears when you close the tab.

When you send booking details or subscribe to the newsletter, the information goes to a private spreadsheet owned by The Alcuin Project, delivered through Google's infrastructure. Booking details are used to prepare for your call. Newsletter addresses are used to send the newsletter. Neither is shared or sold.

To have your information removed, email bookings@alcuinproject.com and we will delete it.
