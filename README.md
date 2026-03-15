# Jira-Flection

Jira-Flection is a powerful Django-based web application designed to natively interact with your JIRA instance and provide a highly responsive, modern interface for browsing, querying, and managing your software project's issues—without ever leaving your local dashboard.

## Overview & Features

- **Jira v3 API Integration**: Uses standard Jira API endpoints to retrieve projects, lists of issues, dynamically formatted ADF descriptions, and specific subtasks.
- **Dynamic Tree Loading**: Browse projects cleanly through a structured Epic -> Story -> Subtask layout. 
    - Click **"⚡ Load Epics"** to narrow down your view immediately to the top-level tickets.
    - Drill down naturally using nested accordions: Each Epic houses a "📎 Load Stories" button, which recursively fetches linked stories within the view. 
    - Each Story allows you to view its "📎 Load Subtasks" inside a neatly scrolling container.
- **In-Memory Tracking**: Avoid duplicate API calls! Single issue searches cleanly slide right into the standard pagination table dynamically. 
    - If you query a ticket that is already rendered in the display, the app gracefully skips fetching it and instead highlights the existing table row for you.
- **At-A-Glance Indicators**: Visual tracking utilizing natively generated context emojis alongside tickets so you immediately know what you're interacting with:
    - ⚡ Epics  
    - 📖 Stories 
    - 📋 Tasks 
    - 🐛 Bugs 
    - 🗃️ Subtasks
- **Sleek Accordion View**: Subtask descriptions cleanly open downward organically in their native rows instead of blocking out the screen or creating empty whitespace.  
- **Status Filtering (Load Done)**: Automatically filters out issues marked as "Done" or "Dropped" by default to keep your workspace clean. Toggle the "Load Done" checkbox to retrieve the full project history.
- **Dedicated Isolated Ticket Views**: Hover over any ticket in the grid and click the "🔗 Default View" button to instantly drop into a dedicated tab. 
    - This mode features a pristine 2-column SaaS layout mapping the ticket data on the left with a dedicated "Actions Menu" sidebar on the right.
    - Features a **Recursive Auto-Loading Snapshot Tree**! Upon loading the page, the system crawls Jira, finds every linked Story to that Epic, then autonomously crawls every Story to find every associated Subtask, building the entire family tree of your project inside dynamic nested accordions on the spot without needing manual requests!

## Tech Stack
- **Backend Framework**: Django 5.x
- **Frontend Engine**: Vanilla JS, styled with custom CSS directly mapped to `base.html` and `project_detail.html` providing a glass-paneled dark mode interface.
- **API Fetching**: Native backend request calls translating securely wrapped API Tokens instead of raw auth endpoints to Jira.

## Usage

1. **Jira Settings**: Upon boot up, navigate to the `Settings` sidebar menu to configure your target `.atlassian.net` workspace domain. You will need your Jira Email Address and an Atlassian API Token.
2. **Dashboard Overview**: The homepage fetches dynamic tiles representing all accessible JIRA projects your API Key has scope for.
3. **Project Management**: Clicking into a specific Jira tile provides a highly responsive query panel. 
    - Search for a specific ticket like `DP-1` or globally paginate down the line using standard load commands.