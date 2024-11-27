# EB1_scripts
In this repo, I share my scripts for Extraordinary Ability Green Card (EB-1A/EB-1B) applications. One important step of the EB-1A and EB-1B application process is obtaining recommendation letters from independent recommenders—people you don't know personally and have never coauthored papers with. While some people attend conferences to connect with potential recommenders, I chose to reach out directly to researchers who have cited my papers by sending cold emails requesting recommendation letters. To get started, you need to compile a list of potential recommenders and gather content for your cold email outreach. Here, I would like to share some scripts I used for this process.

I would like to share my cold call statistics: I sent 94 cold call emails for my EB-1A application. Eight researchers rejected my requests, nine researchers accepted them, and the remaining 77 researchers did not reply. I lost the detailed cold call statistics for my EB-1B application since I was using my work email.

## Step 1: Find my citers

I modified Graham Neubig's [research career tools repo](https://github.com/neubig/research-career-tools) to generate a CSV file for conducting further data manipulation.

The CSV file contains the following columns:
- Rank
- Citing Author
- Author ID
- Total Citations
- Author Paper Count
- Cited Papers and Citing Papers

Based on this information, I can identify recommenders who best fit my EB-1B and EB-1A applications, particularly those with high paper counts who have either cited my papers multiple times or cited multiple papers of mine.

Using the CSV file, I can generate cold call emails with detailed information about each potential recommender.

## Step 2: Enrich citers information [TODO]
More information such as citer names, citer emails, and citers' locations (since EB1A requires global recognition, making it important to find citers from different continents) could be added by modifying the script to call other APIs.

## Step 3: Automation tool [TODO]

While the CSV file can be used to create an AI agent for automatically generating and sending cold call emails to potential recommenders, I took a different approach for my applications. I chose to review each recommender's profile individually and add personal touches to each email.

However, if you're short on time and want to reach out to as many recommenders as possible, you can leverage the CSV file with an AI agent or workflow to automate email generation.

## Step 4: Use AI to facilitate petition letter preparation