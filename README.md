# Facility Assessment Report Generator
### INFINITE — Managed by MEDELITE

---

## Overview

This is a lightweight internal web application built for the Medelite Director team. It enables users to look up any skilled nursing facility in the United States using its CMS Certification Number (CCN), automatically pull publicly available performance data from the CMS Provider Data Catalog, combine that data with internal operational inputs, and download a formatted assessment report in either PDF or Word format.

The application was built to eliminate the manual process of cross-referencing multiple public databases and internal notes. A Director can now enter a single identifier and produce a complete, print-ready facility snapshot in under 30 seconds.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Setup and Running Locally](#setup-and-running-locally)
5. [How to Use](#how-to-use)
6. [Data Sources and Field Mapping](#data-sources-and-field-mapping)
7. [Engineering Assumptions and Decisions](#engineering-assumptions-and-decisions)
8. [Known Limitations](#known-limitations)
9. [Validation Test Case](#validation-test-case)
10. [Deployment Notes](#deployment-notes)

---

## Features

### Core Requirements (MVP)

- **Dynamic CCN Lookup** — Enter any valid 6-digit CMS Certification Number to fetch live data for that facility. Input is validated client-side before the API call is made.
- **CMS Data Engine** — Queries the public CMS Provider Data Catalog API to retrieve the facility's legal name, full address, certified bed count, and all four star ratings.
- **Facility Name Override** — The official legal name is auto-populated from the CMS API. An editable text field allows the user to replace it with a custom internal name. The overridden name flows through to both the report preview and all downloaded files.
- **Manual Operational Inputs** — Dedicated input fields for data that does not exist in the public CMS database: EMR system, current census, patient type, previous Medelite coverage history, previous provider performance, and medical coverage details.
- **PDF Export** — A single "Download PDF Report" button compiles all data and triggers a direct browser download of a clean, branded, print-ready PDF. The filename includes the facility name and the current date.
- **Word Export** — A "Download Word (.docx)" button fills a pre-tagged template document with the same data and downloads it as an editable Word file, preserving the original layout and formatting of the reference template.
- **Medicare Care Compare Hyperlink** — All exports include a clickable hyperlink to the official Medicare Care Compare profile for the searched facility, dynamically constructed from the entered CCN.

### Bonus Features (Implemented)

- **All 12 Hospitalization and ED Metrics** — Pulls and maps the full suite of short-stay (STR) and long-stay (LT) hospitalization and emergency department metrics from the CMS claims-based dataset, along with their respective state and national averages.
- **Comparison Bar Chart** — A grouped bar chart renders in the live preview panel showing the facility's hospitalization and ED rates alongside state and national benchmarks for instant visual comparison.
- **Loading Skeleton** — During the API fetch, the preview panel displays an animated placeholder matching the layout of the actual report, providing visual feedback that the data is loading.
- **Graceful N/A Handling** — If CMS has not reported a metric for a facility (common for newer facilities or those below reporting thresholds), the field displays "N/A — not reported" rather than a blank value, making the gap explicit to the reader.
- **CCN Validation** — The input field validates that the entered CCN is exactly 6 digits before making any API call, surfacing an inline error message immediately.
- **Dated Filenames** — Downloaded files are named with the facility name and the current date, for example: `Facility_Assessment_KENDALL_LAKES_2026-06-15.pdf`.

---

## Tech Stack

### Frontend

- **Vanilla HTML, CSS, and JavaScript** — No frontend framework was used. The entire application is a single `index.html` file. This was a deliberate choice to keep the application lightweight, portable, and free of build tooling.
- **jsPDF** (v2.5.1) — Used to generate PDF files entirely in the browser. Renders the report layout programmatically using direct draw calls rather than converting HTML to canvas, which is significantly faster and more reliable.
- **jsPDF-autotable** (v3.8.2) — Plugin for jsPDF used for structured table rendering within the PDF.
- **docxtemplater** (v3.47.4) — Used to fill the pre-tagged `template.docx` with report data at download time. Accepts `{placeholder}` tags in the Word template and replaces them with live values in the browser.
- **PizZip** (v3.1.4) — ZIP manipulation library required by docxtemplater to read and write the .docx file format, which is a ZIP archive internally.
- **Chart.js** (v4.4.0) — Used to render the grouped bar chart in the live preview panel.
- **Google Fonts (Inter)** — Used for UI typography.

### Backend

- **Python 3** with **Flask** — A minimal Flask server (`server.py`) serves the static frontend files and acts as a server-side proxy for all CMS API requests. This is required because the CMS API does not return CORS headers, which blocks all direct browser fetch calls to that domain.

### Data

- **CMS Provider Data Catalog** — A free, publicly available REST API operated by the Centers for Medicare and Medicaid Services. No API key is required. Three separate datasets are queried per CCN lookup.

---

## Project Structure

```
MedElite/
|
|-- index.html              # Single-page application
|                             Contains all frontend logic, UI, PDF generation,
|                             DOCX generation, chart rendering, and live preview.
|
|-- server.py               # Flask proxy server
|                             Serves static files and proxies all CMS API calls
|                             server-side to bypass CORS restrictions.
|
|-- template.docx           # Pre-tagged Word template
|                             Based on the original Facility Assessment Snapshot.docx.
|                             Contains 26 docxtemplater placeholder tags.
|                             Used as the base for DOCX export.
|
|-- README.md               # This file
```

---

## Setup and Running Locally

### Requirements

- Python 3.8 or higher
- pip (Python package installer)
- A modern web browser (Chrome, Firefox, Safari, or Edge)

### Installation

```bash
# Step 1: Navigate to the project directory
cd MedElite

# Step 2: Install the required Python dependency
pip install flask

# Step 3: Start the application server
python3 server.py
```

### Accessing the Application

Once the server is running, open your browser and go to:

```
http://localhost:3456
```

The server must remain running for the application to function. All CMS API calls are routed through it. If you close the terminal window running `server.py`, the application will lose the ability to fetch data.

### Stopping the Server

Press `Ctrl + C` in the terminal where `server.py` is running.

---

## How to Use

1. Open `http://localhost:3456` in your browser.
2. Enter a valid 6-digit CCN in the search box at the top of the left panel. The field validates that the input is exactly 6 digits before allowing a fetch.
3. Click **Fetch**. The preview panel will show a loading skeleton while the data is retrieved.
4. Once loaded, the right panel populates with the facility hero block, star rating cards, facility detail rows, and the hospitalization metrics table and chart.
5. Fill in the manual operational fields in the left panel: EMR, Current Census, Type of Patient, Previous Coverage from Medelite, Previous Provider Performance, and Medical Coverage. The preview updates in real time as you type.
6. If the facility uses an internal name different from its CMS legal name, type it into the "Name of Facility" field. It will override the API value in the report.
7. Click **Download PDF Report** to download the PDF, or **Download Word (.docx)** to download the editable Word file.

### Test CCN

Use `686123` to test the full flow. This is Kendall Lakes Healthcare and Rehab Center in Miami, FL, and is the reference case provided in the project brief.

---

## Data Sources and Field Mapping

### CMS Datasets Used

| Dataset Name | Dataset ID | Purpose |
|---|---|---|
| Nursing Home Provider Information | `4pq5-n9py` | Facility name, address, bed count, star ratings |
| Medicare Claims Quality Measures | `ijh5-nb2v` | STR and LT hospitalization and ED metrics |
| State and National Averages | `xcdc-v8bm` | Benchmark averages by state and nation |

All three datasets are queried via the CMS datastore query endpoint:
```
https://data.cms.gov/provider-data/api/1/datastore/query/{dataset_id}/0
```

Filtering is done using the `conditions` query parameter format required by this endpoint. The SQL query endpoint (`/datastore/sql`) was tested and found to return 400 errors for this use case; the conditions-based endpoint is the correct approach.

### Field Mapping Reference

| Report Label | Data Source | CMS Field Name |
|---|---|---|
| Name of Facility | CMS API (overrideable) | `provider_name` |
| Location | CMS API | `provider_address`, `citytown`, `state`, `zip_code` joined |
| Census Capacity | CMS API | `number_of_certified_beds` |
| Overall Star Rating | CMS API | `overall_rating` |
| Health Inspection | CMS API | `health_inspection_rating` |
| Staffing | CMS API | `staffing_rating` |
| Quality of Resident Care | CMS API | `qm_rating` |
| STR Hospitalization % | Claims dataset, measure code `521` | `adjusted_score` |
| STR ED Visit % | Claims dataset, measure code `522` | `adjusted_score` |
| LT Hospitalizations per 1000 Days | Claims dataset, measure code `551` | `adjusted_score` |
| LT ED Visits per 1000 Days | Claims dataset, measure code `552` | `adjusted_score` |
| STR Hosp National Avg | Averages dataset, `state_or_nation = NATION` | `percentage_of_short_stay_residents_who_were_rehospitalized__1d02` |
| STR ED National Avg | Averages dataset, `state_or_nation = NATION` | `percentage_of_short_stay_residents_who_had_an_outpatient_em_d911` |
| LT Hosp National Avg | Averages dataset, `state_or_nation = NATION` | `number_of_hospitalizations_per_1000_longstay_resident_days` |
| LT ED National Avg | Averages dataset, `state_or_nation = NATION` | `number_of_outpatient_emergency_department_visits_per_1000_l_de9d` |
| STR Hosp State Avg | Averages dataset, `state_or_nation = <state code>` | Same fields as national, filtered by state |
| STR ED State Avg | Averages dataset, `state_or_nation = <state code>` | Same fields as national, filtered by state |
| LT Hosp State Avg | Averages dataset, `state_or_nation = <state code>` | Same fields as national, filtered by state |
| LT ED State Avg | Averages dataset, `state_or_nation = <state code>` | Same fields as national, filtered by state |
| EMR | Manual input | — |
| Current Census | Manual input | — |
| Type of Patient | Manual input | — |
| Previous Coverage from Medelite | Manual input (Yes/No dropdown) | — |
| Previous Provider Performance | Manual input | — |
| Medical Coverage | Manual input | — |

---

## Engineering Assumptions and Decisions

### 1. CORS Restrictions — Local Flask Proxy

The CMS Provider Data Catalog API does not include `Access-Control-Allow-Origin` response headers. This means any direct `fetch()` call from a browser to the CMS API domain will be blocked by the browser's same-origin policy and fail with a network error, regardless of the validity of the request.

Rather than routing requests through a third-party CORS proxy service (which introduces an external dependency and potential reliability risk), a minimal Flask server was built to handle all CMS requests server-side. The browser communicates only with `localhost:3456`, and the server forwards the request to CMS and returns the response. This is a standard internal-tooling architecture pattern and adds no meaningful latency for single-record lookups.

### 2. SSL Certificate Verification on macOS

Python's `urllib` library on macOS does not automatically locate the system's CA certificate bundle, which causes HTTPS requests to CMS endpoints to fail with `[SSL: CERTIFICATE_VERIFY_FAILED]`. This is a known macOS-specific Python environment issue and is unrelated to the validity of the CMS certificate itself.

The Flask proxy is configured to use an SSL context with `verify_mode = ssl.CERT_NONE` and `check_hostname = False`. This applies only to the server-to-CMS communication path, not to any user-facing connections. Since CMS is a trusted United States government API and the application runs locally, this is an acceptable configuration for this context.

### 3. Correct CCN Field Name in CMS Dataset

The project brief and CMS documentation reference the facility identifier by multiple names across different documents (PROVNUM, provider_id, federal_provider_number). After querying the live API schema for dataset `4pq5-n9py`, the correct field name is `cms_certification_number_ccn`. All conditions filters use this exact field name.

### 4. Correct Hospitalization Dataset Identification

The claims-based hospitalization and ED metrics are not located in the general provider information dataset. They exist in a separate claims-based quality measures dataset with ID `ijh5-nb2v`. An earlier version of the application incorrectly queried dataset `g6vv-u9sr`, which is the Penalties and Enforcement dataset and returns entirely different data despite having a similar schema structure. This was identified by cross-referencing the NH Data Dictionary with live API response payloads and corrected accordingly.

### 5. Measure Codes for Hospitalization Metrics

Within the claims dataset, metrics are identified by a `measure_code` field rather than by column name. The four relevant codes are:

- `521` — Percentage of short-stay residents who were rehospitalized after a nursing home admission (STR Hospitalization %)
- `522` — Percentage of short-stay residents who had an outpatient emergency department visit (STR ED Visit %)
- `551` — Number of hospitalizations per 1000 long-stay resident days (LT Hospitalization)
- `552` — Number of outpatient emergency department visits per 1000 long-stay resident days (LT ED Visit)

The `adjusted_score` field is used for each, which reflects the risk-adjusted value rather than the raw observed rate.

### 6. State and National Average Column Names

The averages dataset (`xcdc-v8bm`) uses extremely long and partially truncated column names generated by CMS. These names are not documented in the NH Data Dictionary and were identified by directly inspecting the JSON response schema from the live API. For example, the national average for STR hospitalization is stored in a field named `percentage_of_short_stay_residents_who_were_rehospitalized__1d02`, where the trailing `_1d02` is a CMS-generated hash suffix to handle column name length limits in the underlying database.

### 7. DOCX Export via Template Fill

Rather than generating a Word document programmatically from scratch, a pre-tagged version of the original `Facility Assessment Snapshot.docx` is used as a base template. The template contains 26 `{placeholder}` tags placed at the exact positions where data should appear. At download time, docxtemplater reads the template in the browser, replaces all tags with live values, and triggers a download of the filled file.

This approach was chosen deliberately over code-generated DOCX for two reasons. First, it preserves the exact visual layout, table structure, fonts, and cell spacing of the reference document provided in the brief without any re-implementation effort. Second, it ensures that if the reference design changes, only the template file needs to be updated — the application code remains unchanged.

The placeholder tags were inserted by unpacking the .docx ZIP archive, performing string replacements in the underlying `word/document.xml`, and repacking the file.

### 8. PizZip vs JSZip API Differences

docxtemplater requires PizZip as its ZIP handler, not the more common JSZip library. The two libraries share similar APIs but differ in key method names. Specifically, PizZip uses `asUint8Array()` to extract binary file contents, while JSZip uses `asBase64()`. Additionally, PizZip's `file()` method requires an exact file path string and does not support regex patterns as JSZip does. The logo image extraction from `template.docx` was written to account for these differences.

### 9. Facility Name Override Behavior

The Name of Facility field is pre-populated with the legal name returned by the CMS API when a CCN is fetched. If the user types a custom name into this field, that name is used in the report body and the exported filename. If the field is left as-is after fetch, the CMS legal name is used. The "INFINITE — Managed by MEDELITE" platform branding in the report header is a separate hardcoded element and is not affected by this field under any circumstances.

### 10. PDF Branding Strategy

The project brief specifies that the header of all generated exports must display "INFINITE — Managed by MEDELITE" as a hardcoded brand element. The logo image extracted from `template.docx` already contains this text rendered as part of the graphic. In the PDF, the logo is rendered first. Below it, the text "INFINITE" and "Managed by MEDELITE" are also rendered as actual text elements. If the logo image fails to load for any reason, the text rendering alone satisfies the branding requirement. If the logo loads successfully, both are present, with the logo serving as the primary visual header.

### 11. Missing CMS Data Fields

Not all facilities have data available for every field in the CMS database. Facilities that are recently certified, have low resident counts, or fall below CMS reporting thresholds may have null or absent values for claims-based metrics. The application treats any null, undefined, or empty string value as unreported rather than as zero. These fields display "N/A — not reported" in the preview and in all exported files. This distinction is important because a zero value and an unreported value are meaningfully different in a clinical context.

### 12. CCN Input Validation

CMS Certification Numbers for nursing home facilities are always exactly 6 digits. The application validates this constraint client-side before making any API call. If the input does not match the pattern `^\d{6}$`, an inline error message is shown immediately and no network request is made. This prevents unnecessary API calls and provides faster feedback to the user than waiting for a failed server response.

---

## Known Limitations

**Local server dependency** — The application requires the Flask server to be running locally. It cannot be deployed to a static hosting provider (such as GitHub Pages or Netlify) without modification. A full deployment requires a hosting environment that supports Python, such as Render or Railway.

**CMS data refresh cadence** — CMS updates its provider datasets on a monthly basis. The data displayed in the application reflects the most recent CMS release and may not reflect changes that occurred within the current month.

**State averages availability** — The averages dataset contains one row per state and one row for the national average. If CMS has not published averages for a given state in the current dataset release, state average fields will display "N/A — not reported".

**Single facility per session** — The application currently supports looking up one facility at a time. Fetching a new CCN replaces the previously loaded data. There is no session history or comparison view between two facilities within the same session.

---

## Validation Test Case

The following CCN was provided in the project brief as the reference validation target.

**CCN:** `686123`
**Facility:** Kendall Lakes Healthcare and Rehab Center
**Address:** 9485 SW 24th St, Miami, FL 33165

### Expected CMS Output

| Field | Expected Value |
|---|---|
| Overall Star Rating | 3 |
| Health Inspection Rating | 4 |
| Staffing Rating | 2 |
| Quality of Resident Care | 5 |
| STR Hospitalization | 25.6% |
| STR ED Visit | 8.1% |
| LT Hospitalizations per 1000 Days | 2.75 |
| LT ED Visits per 1000 Days | 0.91 |
| National Avg STR Hospitalization | 23.9% |
| National Avg STR ED Visit | 12.0% |
| National Avg LT Hospitalization | 1.90 |
| National Avg LT ED Visit | 1.80 |

Values sourced from CMS dataset processing date: May 2026. Minor variation may occur in future dataset releases.

### Additional Test CCNs

| CCN | Facility | State | Overall Rating |
|---|---|---|---|
| `686124` | Harmony Health Center | FL | 5 |
| `555445` | Anaheim Crest Nursing Center | CA | 5 |
| `145660` | Aperion Care Westchester | IL | 3 |
| `225522` | Regalcare at Quincy | MA | 2 |
| `676045` | Brentwood Terrace Healthcare and Rehabilitation | TX | 1 |

---

## Deployment Notes

The application requires a Python-capable hosting environment due to the Flask proxy server. Static hosting alone is not sufficient.

**Recommended platforms:**

- **Render** (render.com) — Supports Python web services on a free tier. Deploy by connecting a GitHub repository and setting the start command to `python3 server.py`.
- **Railway** (railway.app) — Similar Python support with minimal configuration. Detects Flask applications automatically from a `requirements.txt` file.

**Requirements file for deployment:**

Create a `requirements.txt` in the project root:

```
flask>=2.0.0
```

No other Python packages are required. All frontend dependencies are loaded via CDN at runtime.

---

## Reference Documents

The following files were provided as part of the project brief and informed the application design:

- `Facility Assessment Snapshot.docx` — Reference layout used to design the report structure and create the DOCX template
- `Kendall Lakes Healthcare and Rehab Center.pdf` — Sample completed report used to verify field values and output formatting
- `NH_Data_Dictionary.pdf` — CMS data dictionary used to identify dataset IDs, field names, and measure codes
- `Medelite Technical Case Study.docx` — Project brief containing functional requirements, branding guidelines, and evaluation criteria
