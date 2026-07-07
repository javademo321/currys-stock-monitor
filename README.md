# Currys MacBook Stock Monitor (free, always-on)

Checks the Currys Business product page **twice a day** on GitHub's servers
(so it runs even when your computer is off) and **emails
`andrew@multibrands-techtron.com`** the moment it is back in stock.

**Watching:** APPLE MacBook Pro 16" (2026) - M5 Max, 2 TB SSD, RAM 48 GB, Space Black
(code MGEE4B/A) - https://business.currys.co.uk/catalogue/computing/laptops/macbook/apple-macbook-pro-16-2026-m5-max-2-tb-ssd-ram-48-gb-space-black/N428505W

Cost: **£0.** GitHub Actions is free (unlimited minutes on a public repo), and
email goes through Web3Forms' free tier (~250 emails/month; this uses ~60).

---

## One-time setup (about 5 minutes)

### 1. Get a free email key from Web3Forms
1. Go to https://web3forms.com
2. Enter **Email** in the "Create your Access Key" box and submit.
3. Web3Forms emails an **Access Key** (a long code) to that address. Copy it.
   - This is what lets the monitor deliver mail to that inbox. No password/SMTP needed.

### 2. Create the GitHub repository
1. Sign in at https://github.com (create a free account if needed).
2. Click **New repository** → name it e.g. `currys-stock-monitor` → **Public**
   (public = unlimited free Actions minutes) → **Create repository**.
3. Upload these files, keeping the folder structure:
   - `check_stock.py`
   - `.github/workflows/stock-check.yml`
   - `README.md` (optional)

   Easiest way: on the repo page click **Add file → Upload files**, then drag in
   `check_stock.py`. To add the workflow, click **Add file → Create new file**,
   type `.github/workflows/stock-check.yml` as the name, and paste the contents.

### 3. Add your email key as a secret
1. In the repo: **Settings → Secrets and variables → Actions → New repository secret**.
2. Name: `WEB3FORMS_KEY`
3. Value: paste the Access Key from step 1. **Save.**

### 4. Turn it on and test
1. Go to the **Actions** tab → if prompted, click **"I understand my workflows, enable them."**
2. Click **Currys Stock Check** → **Run workflow**. Tick **"Send a test email instead
   of checking stock?"** and run it → you should get a **TEST** email within a minute.
   This confirms email delivery works.
3. Run it again **without** ticking the box to do a real check. While the item is out
   of stock you'll see `Still OUT OF STOCK. No action.` in the log. When it flips to in
   stock you'll get the IN STOCK email automatically.

That's it. It now runs automatically at ~9am and ~2pm UK time every day.

---

## Good to know
- **Times are in UTC.** The schedule (`0 8,13 * * *`) = 9am/2pm UK during summer
  (BST). In winter it becomes 8am/1pm UK; change the cron to `0 9,14 * * *` if you
  want exactly 9/2 in winter. GitHub also sometimes delays scheduled runs by a few
  minutes at busy times - fine for this use.
- **60-day rule.** GitHub disables scheduled workflows if a repo has no activity for
  60 days (it emails you first). Just click **Run workflow** occasionally, or make
  any small commit, to keep it alive.
- **No false alarms.** If the page fails to load or looks wrong, the script logs it
  and stays quiet - it only emails when it positively sees the item is buyable.
- **Change the recipient** by generating a new Web3Forms key for a different address
  and updating the `WEB3FORMS_KEY` secret.
- **Watch a second model** (e.g. the 36GB variant) by copying `check_stock.py`,
  changing `URL` and `PRODUCT_CODE`, and adding another step to the workflow.
